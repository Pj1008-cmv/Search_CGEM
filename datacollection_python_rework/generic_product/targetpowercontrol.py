"""Standardized interface for reading and setting RVP power state (on/off)"""

import logging
import random
import sys
import time

# local imports
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.hardware.ttk3 as ttk3
import generic_product.utilities.logger as logger
from generic_product.sv_ipc_wrapper import PySVOpenIPCWrapper

# need to set this value in product-specific implementation!
DUT_POWERSPLITTER_PORT_NUM = None
PYSV_PRODUCT = None

def target_power_on_control(wait_for_POST: bool=True) -> None:
    """Turn on the unit and wait until 10AD is reached."""
    logger.info('Turning on the target.')
    ttk3.set_powerspliter_port_state(DUT_POWERSPLITTER_PORT_NUM, func='on')
    if wait_for_POST:
        logger.info('We will wait until unit reaches 10AD.')
        ttk3.wait_until_specified_POST_code(target_post_code='10AD')
        sv_ipc_wrapper = PySVOpenIPCWrapper(PYSV_PRODUCT, is_processor_on_fn=is_target_power_on)
        sv_ipc_wrapper.get_all(force_update=True)  # refresh PythonSV!

def target_power_off_control(delay_after_s: float = 5) -> None:
    """Turn off the unit and sleep for specified seconds."""
    logger.info(f'Turning off the target - will wait {delay_after_s}s.')
    ttk3.set_powerspliter_port_state(DUT_POWERSPLITTER_PORT_NUM, func='off')
    time.sleep(delay_after_s)

def is_target_power_on() -> bool:
    """Returns `True` if power is on, `False` otherwise."""
    return _get_target_power_state(DUT_POWERSPLITTER_PORT_NUM) == 'on'

def is_target_power_off() -> bool:
    """Returns `True` if power is off, `False` otherwise."""
    return _get_target_power_state(DUT_POWERSPLITTER_PORT_NUM) == 'off'

def _get_target_power_state(port_num: int) -> str:
    """Use ttk3 to query powersplitter state.
    
    In case this command is called 2+ times back-to-back,
    catching `OSError` and re-trying after a wait period per call.
    
    Returns
    -------
    port_state: str ('on', 'off')
    """
    try:
        port_state = ttk3.read_powersplitter_port_state(port_num)
    except OSError:
        time.sleep(0.5 + (random.randrange(0, 1000) / 1000))  # 500 -> 1500 ms
        port_state = ttk3.read_powersplitter_port_state(port_num)
    logger.info(f'DUT is currently: {port_state.upper()}')
    return port_state