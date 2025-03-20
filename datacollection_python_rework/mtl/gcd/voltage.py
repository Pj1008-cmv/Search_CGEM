"""Meteorlake graphics dielet voltage set and read-back."""

# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.hardware.nevo as nevo
import generic_product.utilities.algorithm as algorithm
import generic_product.utilities.logger as logger
from generic_product.utilities.pysv_script_manager import PySVScriptManager
from mtl.sv import get_soc

# imports, pythonsv
svid_script = PySVScriptManager('meteorlake.users.oqmohsin.set_sa_svid')

MAX_ALLOWED_VCCGT_SET_V = 1.4
MIN_ALLOWED_VCCGT_SET_V = 0.4
SET_READ_LOOP_TOLERANCE_V = 0.004

NUM_VF_CURVE_POINTS_GT = 6

### READ
def read_vccgt_voltage() -> str:
    """Reads VCCGT voltage."""
    return nevo.read_value('VCCGT')

### SET
def set_vccgt_voltage_svid(set_V: float) -> None:
    """Sets VCCGT voltage using SVID."""
    if set_V > MAX_ALLOWED_VCCGT_SET_V or MIN_ALLOWED_VCCGT_SET_V > set_V:
        logger.error(msg:=f"Set voltage ({set_V}) is outside allowed voltage range (min={MIN_ALLOWED_VCCGT_SET_V}V, max={MAX_ALLOWED_VCCGT_SET_V}V)")
        raise RuntimeError(msg)
    logger.info(f'Setting VCCGT to {set_V}V via SVID')
    svid_script.set_sa_svid(set_V, 0x1)

def set_vccgt_voltage_svid_withintolerance(set_V: float, tolerance_V: float=SET_READ_LOOP_TOLERANCE_V) -> None:
    algorithm.set_read_ensure_tolerance_loop(
        set_fn               = set_vccgt_voltage_svid,
        set_kwarg_key        = 'set_V',
        set_kwds             = {'set_V':set_V},
        read_fn              = read_vccgt_voltage,
        tolerance            = tolerance_V,
        min_allowed_setpoint = MIN_ALLOWED_VCCGT_SET_V,
        max_allowed_setpoint = MAX_ALLOWED_VCCGT_SET_V
    )

### VF voltage (arbitrary per-point)
def set_gt_vf_point_voltage(vfpoint: int, set_V: float):
    """Set desired `vfpoint` of GT VF curve to `voltage`."""
    if set_V > MAX_ALLOWED_VCCGT_SET_V or MIN_ALLOWED_VCCGT_SET_V > set_V:
        logger.error(msg:=f"Set voltage ({set_V}) is outside allowed voltage range (min={MIN_ALLOWED_VCCGT_SET_V}V, max={MAX_ALLOWED_VCCGT_SET_V}V)")
        raise RuntimeError(msg)
    soc = get_soc(ensure_at_soc_fusebreak=True)
    cmd = f'soc.south.fuses.punit_fuse.fw_fuses_gt_vf_voltage_{vfpoint} = {int(set_V*256)}'
    logger.info(cmd)
    exec(cmd)

def verify_gt_vf_point_voltage(vfpoint: int, voltage_V: float):
    """Verify that desired GT VF `vfpoint` voltage matches `voltage_V`."""
    soc = get_soc(ensure_booted=True)
    cmd = f'soc.south.fuses.punit_fuse.fw_fuses_gt_vf_voltage_{vfpoint}'
    assert(eval(cmd) == int(voltage_V*256))

### VF voltage (flat all points)
def set_gt_vf_to_flat_voltage(voltage_V: float):
    """Set all GT VF points to `voltage`."""
    for vfpoint in range(NUM_VF_CURVE_POINTS_GT):
        set_gt_vf_point_voltage(vfpoint, voltage_V)

def verify_gt_vf_flat_voltage(voltage_V: float):
    """Verify that all GT VF points set to `voltage_V`"""
    for vfpoint in range(NUM_VF_CURVE_POINTS_GT):
        verify_gt_vf_point_voltage(vfpoint, voltage_V)