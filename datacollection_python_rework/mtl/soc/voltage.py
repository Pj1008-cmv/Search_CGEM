"""Meteorlake system-agent dielet voltage set and read-back."""

# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.hardware.nevo as nevo
import generic_product.utilities.algorithm as algorithm
import generic_product.utilities.logger as logger
from generic_product.utilities.pysv_script_manager import PySVScriptManager

# imports, pythonsv
svid_script = PySVScriptManager('meteorlake.users.oqmohsin.set_sa_svid')

SET_READ_LOOP_TOLERANCE_V = 0.004
MAX_ALLOWED_VCCSA_SET_V = 1.4
MIN_ALLOWED_VCCSA_SET_V = 0.4

### READ
def read_vccsa_voltage() -> str:
    """Reads VCCSA voltage."""
    return nevo.read_value('VCCSA')

### SET
def set_vccsa_voltage_svid(set_V: float) -> None:
    """Sets VCCSA to specified voltage without verification."""
    if set_V > MAX_ALLOWED_VCCSA_SET_V or MIN_ALLOWED_VCCSA_SET_V > set_V:
        logger.error(msg:=f"Set voltage ({set_V}) is outside allowed voltage range (min={MIN_ALLOWED_VCCSA_SET_V}V, max={MAX_ALLOWED_VCCSA_SET_V}V)")
        raise RuntimeError(msg)
    logger.info(f'Setting VCCSA to {set_V}V via SVID')
    svid_script.set_sa_svid(set_V)

def set_vccsa_voltage_svid_withintolerance(set_V: float, tolerance_V: float=SET_READ_LOOP_TOLERANCE_V) -> None:
    algorithm.set_read_ensure_tolerance_loop(
        set_fn               = set_vccsa_voltage_svid,
        set_kwarg_key        = 'set_V',
        set_kwds             = {'set_V':set_V},
        read_fn              = read_vccsa_voltage,
        tolerance            = tolerance_V,
        min_allowed_setpoint = MIN_ALLOWED_VCCSA_SET_V,
        max_allowed_setpoint = MAX_ALLOWED_VCCSA_SET_V
    )