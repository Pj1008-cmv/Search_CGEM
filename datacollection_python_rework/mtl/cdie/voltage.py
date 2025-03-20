"""Meteorlake compute dielet voltage set and read-back."""

# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.hardware.nevo as nevo
import generic_product.utilities.algorithm as algorithm
import generic_product.utilities.logger as logger
from generic_product.utilities.pysv_script_manager import PySVScriptManager
from mtl import bootstagetransitions
from mtl.sv import fuse_loop

# imports, pythonsv
dlvr_script = PySVScriptManager('meteorlake.users.dlvr.dlvr_debug_script')
vf_on_the_fly_script = PySVScriptManager('meteorlake.debug.domains.cdie.cores_dbg')

MAX_ALLOWED_DLVR_SET_V = 1.40
MIN_ALLOWED_DLVR_SET_V = 0.45
SET_READ_LOOP_TOLERANCE_V = 0.004

### READ

def read_bigcore_voltage(corenum_physical: int) -> str:
    """Reads voltage of specified Redwood Cove (RWC) big core."""
    return nevo.read_value(f'VL_CORE{corenum_physical}')

def read_atommod_voltage(modulenum_physical: int) -> str:
    """Reads voltage of specified Cresmont (CMT) Atom module."""
    return nevo.read_value(f'VL_ATOM{modulenum_physical}')

def read_ring_voltage() -> str:
    """Reads Ring/LLC voltage."""
    return nevo.read_value(f'VL_LLC')

def read_vccia_voltage() -> str:
    """Read VCCIA voltage."""
    return nevo.read_value('VCCCORE_S')

### SET

## DLVR

def set_voltage_dlvr(domain: str, set_V: float, powerstate: int):
    if set_V > MAX_ALLOWED_DLVR_SET_V or MIN_ALLOWED_DLVR_SET_V > set_V:
        logger.error(msg:=f"Set voltage ({set_V}) is outside allowed voltage range (min={MIN_ALLOWED_DLVR_SET_V}V, max={MAX_ALLOWED_DLVR_SET_V}V)")
        raise RuntimeError(msg)
    dlvr_script.powerstate(
        domain = domain,
        voltage = set_V,
        ps = powerstate, 
        ramp = 1,
        method = 'tap'
    )

# TODO: name argument either `corenum_physical` or `corenum_logical` (need to figure out which it is)
def set_bigcore_voltage_dlvr(corenum: int, set_V: float, powerstate: int=1) -> None:
    """Sets voltage of Redwood Cove (RWC) core using DLVR script."""
    logger.info(f'Setting RWC {corenum} to {set_V}V (powerstate={powerstate})')
    set_voltage_dlvr(f'core{corenum}', set_V, powerstate)
    
# TODO: name argument either `corenum_physical` or `corenum_logical` (need to figure out which it is)
def set_bigcore_voltage_dlvr_withintolerance(corenum: int, set_V: float, powerstate: int=1, tolerance_V: float=SET_READ_LOOP_TOLERANCE_V) -> None:
    algorithm.set_read_ensure_tolerance_loop(
        set_fn               = set_bigcore_voltage_dlvr,
        set_kwarg_key        = 'set_V',
        set_kwds                 = {'corenum':corenum, 'set_V':set_V, 'powerstate':powerstate},
        read_fn              = read_bigcore_voltage,
        read_kwds              = {'corenum_physical':corenum},
        tolerance            = tolerance_V,
        min_allowed_setpoint = MIN_ALLOWED_DLVR_SET_V,
        max_allowed_setpoint = MAX_ALLOWED_DLVR_SET_V
    )

def set_atommod_voltage_dlvr(modulenum: int, set_V: float, powerstate: int=1) -> None:
    """Sets voltage of Crestmont (CMT) Atom module using DLVR script."""
    logger.info(f'Setting CMT {modulenum} to {set_V}V (powerstate={powerstate})')
    set_voltage_dlvr(f'core{modulenum}', set_V, powerstate)

def set_atommod_voltage_dlvr_withintolerance(modulenum: int, set_V: float, powerstate: int=1, tolerance_V: float=SET_READ_LOOP_TOLERANCE_V) -> None:
    algorithm.set_read_ensure_tolerance_loop(
        set_fn               = set_atommod_voltage_dlvr,
        set_kwarg_key        = 'set_V',
        set_kwds             = {'modulenum':modulenum, 'set_V':set_V, 'powerstate':powerstate},
        read_fn              = read_atommod_voltage,
        read_kwds            = {'modulenum_physical':modulenum},
        tolerance            = tolerance_V,
        min_allowed_setpoint = MIN_ALLOWED_DLVR_SET_V,
        max_allowed_setpoint = MAX_ALLOWED_DLVR_SET_V
    )

def set_ring_voltage_dlvr(set_V: float, powerstate: int=1):
    """Sets voltage of Ring/LLC using DLVR script."""
    logger.info(f'Setting Ring to {set_V}V (powerstate={powerstate})')
    set_voltage_dlvr('ring', set_V, powerstate)

def set_ring_voltage_dlvr_withintolerance(set_V: float, powerstate: int=1, tolerance_V: float=SET_READ_LOOP_TOLERANCE_V) -> None:
    algorithm.set_read_ensure_tolerance_loop(
        set_fn               = set_ring_voltage_dlvr,
        set_kwarg_key        = 'set_V',
        set_kwds             = {'set_V':set_V, 'powerstate':powerstate},
        read_fn              = read_ring_voltage,
        tolerance            = tolerance_V,
        min_allowed_setpoint = MIN_ALLOWED_DLVR_SET_V,
        max_allowed_setpoint = MAX_ALLOWED_DLVR_SET_V
    )


## VF-on-the-fly

# TODO: name argument either `corenum_physical` or `corenum_logical` (need to figure out which it is)
def set_bigcore_voltage_vfotf(corenum: int, set_V: float, set_ratio: int) -> None:
    """Sets voltage of Redwood Cove (RWC) core using VF-on-the-fly.
    Aguila OTPL test program is expected to track voltage/freq setpoints to pass in.
    """
    if set_V > MAX_ALLOWED_DLVR_SET_V or MIN_ALLOWED_DLVR_SET_V > set_V:
        logger.error(msg:=f"Set voltage ({set_V}) is outside allowed voltage range (min={MIN_ALLOWED_DLVR_SET_V}V, max={MAX_ALLOWED_DLVR_SET_V}V)")
        raise RuntimeError(msg)
    logger.info(f'VFotF: setting voltage ({set_V}V) and core ratio ({set_ratio})')
    vf_on_the_fly_script.lock_freq_acode_dcode(core_index=corenum, voltage=set_V, ratio=set_ratio)

# TODO: name argument either `corenum_physical` or `corenum_logical` (need to figure out which it is)
def set_bigcore_voltage_vfotf_withintolerance(corenum: int, set_V: float, set_ratio: int, tolerance_V: float = SET_READ_LOOP_TOLERANCE_V) -> None:
    algorithm.set_read_ensure_tolerance_loop(
        set_fn               = set_bigcore_voltage_vfotf,
        set_kwarg_key        = 'set_V',
        set_kwds             = {'corenum':corenum, 'set_V':set_V, 'set_ratio':set_ratio},
        read_fn              = read_bigcore_voltage,
        read_kwds            = {'corenum_physical':corenum},
        tolerance            = tolerance_V,
        min_allowed_setpoint = MIN_ALLOWED_DLVR_SET_V,
        max_allowed_setpoint = MAX_ALLOWED_DLVR_SET_V
    )

# TODO: figure out how to set atom w/ VFotF
def set_atommod_voltage_cfotf(modulenum: int, set_V: float, set_ratio: int) -> None:
    raise NotImplementedError

def set_atommod_voltage_cfotf_withintolerance(modulenum: int, set_V: float, set_ratio: int, tolerance_V: float=SET_READ_LOOP_TOLERANCE_V) -> None:
    raise NotImplementedError

### VF

#### generic cdie

def shift_vf(fuse, offset_V, num_vf_points=9):
    bootstagetransitions.ensure_at_cdie_fusebreak()
    fuse_ticks = int(offset_V*256)
    fuse_loop(f'{fuse} += {fuse_ticks}', num_loops=num_vf_points)

def flatten_vf(fuse, set_V, num_vf_points=9):
    bootstagetransitions.ensure_at_cdie_fusebreak()
    fuse_ticks = int(set_V*256)
    fuse_loop(f'{fuse} = {fuse_ticks}', num_loops=num_vf_points)

#### per-domain

def shift_ring_vf(offset_V):
    logger.info(f"Adding {offset_V}V to ring VF curve")
    shift_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_ring_vf_voltage_<INDEX>', offset_V=offset_V)

def flatten_ring_vf(set_V):
    logger.info(f"Setting ring VF curve to flat {set_V}V")
    flatten_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_ring_vf_voltage_<INDEX>', set_V=set_V)

def shift_atom_vf(offset_V):
    logger.info(f"Adding {offset_V}V to atom VF curve")
    shift_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_atom_vf_voltage_<INDEX>', offset_V=offset_V)

def flatten_atom_vf(set_V):
    logger.info(f"Setting atom VF curve to flat {set_V}V")
    flatten_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_atom_vf_voltage_<INDEX>', set_V=set_V)

def shift_bigcore_vf(offset_V):
    logger.info(f"Adding {offset_V}V to bigcore VF curve")
    shift_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_ia_vf_voltage_<INDEX>', offset_V=offset_V)
    shift_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_ia_ulvt_vf_voltage_<INDEX>', offset_V=offset_V)

def flatten_bigcore_vf(set_V):
    logger.info(f"Setting bigcore VF curve to flat {set_V}V")
    flatten_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_ia_vf_voltage_<INDEX>', set_V=set_V)
    flatten_vf(fuse=f'cdie.fuses.dmu_fuse.fw_fuses_ia_ulvt_vf_voltage_<INDEX>', set_V=set_V)