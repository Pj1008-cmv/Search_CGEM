"""NOTE before using this module, ensure you instantiate PySVOpenIPCWrapper singelton!"""

# imports, std library
import functools
import logging
import sys

# imports, pySV
import pysvtools.bootscript.boot as boot_script

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.hardware.ttk3 as ttk3
import generic_product.utilities.logger as logger
import mtl.sv
import mtl.targetpowercontrol as targetpowercontrol
from generic_product.sv_ipc_wrapper import PySVOpenIPCWrapper
from mtl.processorinfo import MeteorlakeProcessorInfo

sv_ipc_wrapper = PySVOpenIPCWrapper()

# boot stages
POWER_OFF_STAGE = "PowerOffStage"
SOC_FUSEBREAK   = "platform_bootstall"
IOE_FUSEBREAK   = "ioe_bootstall"
GCD_FUSEBREAK   = "gcd_fuse_override_break"
CDIE_FUSEBREAK  = "cdie_dfxagg_break"
EFI_STAGE       = "EfiStage"
WINDOWS_STAGE   = "WindowsStage"

FUSEBREAK_STAGES = [SOC_FUSEBREAK, IOE_FUSEBREAK, GCD_FUSEBREAK, CDIE_FUSEBREAK]
CONTENT_STAGES = [EFI_STAGE, WINDOWS_STAGE]

# valid boot stage transitions (from, to)
VALID_TRANSITIONS = {
    # poweroff -> *
    (POWER_OFF_STAGE, EFI_STAGE),
    # * -> poweroff
    (SOC_FUSEBREAK, POWER_OFF_STAGE),
    (IOE_FUSEBREAK, POWER_OFF_STAGE),
    (GCD_FUSEBREAK, POWER_OFF_STAGE),
    (CDIE_FUSEBREAK, POWER_OFF_STAGE),
    (EFI_STAGE, POWER_OFF_STAGE),
    (WINDOWS_STAGE, POWER_OFF_STAGE),

    # EFI -> break
    (EFI_STAGE, SOC_FUSEBREAK),
    (EFI_STAGE, IOE_FUSEBREAK),
    (EFI_STAGE, GCD_FUSEBREAK),
    (EFI_STAGE, CDIE_FUSEBREAK),

    # break stages, SOC -> *
    (SOC_FUSEBREAK, IOE_FUSEBREAK),
    (SOC_FUSEBREAK, GCD_FUSEBREAK),
    (SOC_FUSEBREAK, CDIE_FUSEBREAK),
    # break stages, IOE -> *
    (IOE_FUSEBREAK, GCD_FUSEBREAK),
    (IOE_FUSEBREAK, CDIE_FUSEBREAK),
    # break stages, GCD -> *
    (GCD_FUSEBREAK, CDIE_FUSEBREAK),

    # break -> EFI
    (SOC_FUSEBREAK, EFI_STAGE),
    (IOE_FUSEBREAK, EFI_STAGE),
    (GCD_FUSEBREAK, EFI_STAGE),
    (CDIE_FUSEBREAK, EFI_STAGE),

    # -> Windows
    (EFI_STAGE, WINDOWS_STAGE),
}

# global variable for tracking current boot stage
current_stage = None
# global dictionary that keeps track of what fuses are set so that we can easily verify
fuse_set_record = {}

def can_transition(from_stage, to_stage):
    """Indicates whether transition from -> to given stages is valid."""
    valid_transition = (from_stage, to_stage) in VALID_TRANSITIONS
    if valid_transition:
        logger.info(f'Transition from {from_stage} to {to_stage} is possible!')
    else:
        logger.info(f'Transition from {from_stage} to {to_stage} is not possible.')
    return valid_transition

def is_in_stage(stage):
    """Verifies whether processor is in specified stage."""
    if stage == POWER_OFF_STAGE:
        return targetpowercontrol.is_target_power_off()
    elif stage == EFI_STAGE:
        return ttk3.read_POST() == '10AD'
    elif stage in FUSEBREAK_STAGES:
        return eval(f'boot_script.boot_vars.breaks.{stage}.at()')
    elif stage == WINDOWS_STAGE:
        return '?'

def determine_current_stage():
    """Uses `is_in_stage(stage) to determine which stage we're in.
    Stages are ordered purposefully so that shorter-check-time stages are first.
    """
    for stage in [POWER_OFF_STAGE, EFI_STAGE] + FUSEBREAK_STAGES:
        if is_in_stage(stage):
            return stage
    return None

def _on_entering_stage(stage):
    """Perform action(s) that need to be done right after transition to `stage`; called by `perform_transition()`"""
    if stage == SOC_FUSEBREAK or stage in CONTENT_STAGES:
        logger.info('Loading soc dielet fuse ram!')
        sv_ipc_wrapper.sv.socket0.soc.south.fuses.load_fuse_ram()
    if stage == IOE_FUSEBREAK or stage in CONTENT_STAGES:
        logger.info('Loading ioe dielet fuse ram!')
        sv_ipc_wrapper.sv.socket0.ioe.fuses.load_fuse_ram()
    if stage == GCD_FUSEBREAK or stage in CONTENT_STAGES:
        logger.info('Loading gcd fuse ram!')
        sv_ipc_wrapper.sv.socket0.gcd.fuses.load_fuse_ram()
    if stage == CDIE_FUSEBREAK or stage in CONTENT_STAGES:
        logger.info('Loading cdie fuse ram!')
        sv_ipc_wrapper.sv.socket0.compute0.fuses.load_fuse_ram()
    if stage in CONTENT_STAGES:
       mtl.sv.ensure_all_fuse_settings_valid()

def _on_exiting_stage(stage):
    """Perform action(s) that need to be done as cleanup steps before  transition from `stage`; called by `perform_transition()`"""
    if stage == SOC_FUSEBREAK:
        sv_ipc_wrapper.sv.socket0.soc.south.fuses.flush_fuse_ram()
    elif stage == IOE_FUSEBREAK:
        sv_ipc_wrapper.sv.socket0.ioe.fuses.flush_fuse_ram()
    elif stage == GCD_FUSEBREAK:
        sv_ipc_wrapper.sv.socket0.gcd.fuses.flush_fuse_ram()
    elif stage == CDIE_FUSEBREAK:
        sv_ipc_wrapper.sv.socket0.compute0.fuses.flush_fuse_ram()

def perform_transition(to_stage, from_stage=None):
    """Performs transition `from_stage` -> `to_stage`.

    `from_stage` is by default assigned to global `current_stage` but can also be provided as arg.

    Not assuming that transition `(stage, stage)` is invalid,
    validity is up to the implementation of this function and the `VALID_TRANSITIONS` mapping.
    """
    global current_stage
    global fuse_set_record

    # ensure we have a definite `from_stage`
    if current_stage is None:
        current_stage = determine_current_stage()
    if from_stage is None:
        from_stage = current_stage

    # ensure transition is valid; if not, nothing to do
    if not can_transition(from_stage, to_stage):
        logger.error(f'Cannot transition between stages: {from_stage} -> {to_stage}.')
        return
    logger.info(f'Starting transition between stages: {from_stage} -> {to_stage}!')

    # 3. perform on-exit actions
    _on_exiting_stage(from_stage)

    ### perform the transition!

    if to_stage == POWER_OFF_STAGE:
        sv_ipc_wrapper.need_refresh = True  # since we're powering off
        targetpowercontrol.target_power_off_control(delay_after_s=10)
        fuse_set_record = {}  # clear -- fuses set no longer valid!

    elif from_stage == POWER_OFF_STAGE and to_stage == EFI_STAGE:
        targetpowercontrol.target_power_on_control(wait_for_POST=True)
    
    # Poweroff -> *fusebreak
    # EFI -> *fusebreak
    elif from_stage == EFI_STAGE:
        if to_stage in FUSEBREAK_STAGES:
            # since the processor is already on, we can read out information!
            procinfo = MeteorlakeProcessorInfo()
            _, deriv, step = procinfo.pds
            boot_script.clean_up_vars()
            boot_script.initialize_project('meteorlake')
            
            recipe = f'{deriv.upper()}_{step.upper()}'
            logger.info(f'Calling boot script with recipe: {recipe}')
            boot_script.go(STEPPING=recipe, gotil=to_stage)

    elif from_stage in FUSEBREAK_STAGES:
        # *fusebreak -> *fusebreak
        if to_stage in FUSEBREAK_STAGES:
            boot_script.cont(gotil=to_stage)
        # *fusebreak -> EFI
        elif to_stage == EFI_STAGE:
            boot_script.cont()
            ttk3.wait_until_specified_POST_code(target_post_code='10AD', per_iteration_delay_s=0.001)
            sv_ipc_wrapper.get_all(force_update=True)  # refresh!  performs ipc.unlock() and sv.get_all()

    # test whether transition worked
    if is_in_stage(to_stage):
        current_stage = to_stage
        logger.info(f'Completed transition between stages: {from_stage} -> {to_stage}')
    else:
        logger.error(msg:=f'Transition between stages ({from_stage} -> {to_stage}) failed.')
        raise RuntimeError(msg)

    # perform on-enter actions
    _on_entering_stage(to_stage)

# convinience functions for determining if we are currently in a given stage.
def ensure_at_stage(desired_stages: list):
    """Checks whether `bootstagetransitions.current_stage` is set to a specific boot stage.
    `current_stage` is updated by `perform_transition`, which uses `is_in_stage` for validation."""
    if current_stage not in desired_stages:
        logger.error(msg:=f'Current boot stage ({current_stage}) is not in the expected collection ({desired_stages}).')
        raise RuntimeError(msg)

ensure_at_poweroff       = functools.partial(ensure_at_stage, desired_stages=[POWER_OFF_STAGE])
ensure_at_soc_fusebreak  = functools.partial(ensure_at_stage, desired_stages=[SOC_FUSEBREAK])
ensure_at_ioe_fusebreak  = functools.partial(ensure_at_stage, desired_stages=[IOE_FUSEBREAK])
ensure_at_gcd_fusebreak  = functools.partial(ensure_at_stage, desired_stages=[GCD_FUSEBREAK])
ensure_at_cdie_fusebreak = functools.partial(ensure_at_stage, desired_stages=[CDIE_FUSEBREAK])
ensure_at_content_stage  = functools.partial(ensure_at_stage, desired_stages=CONTENT_STAGES)