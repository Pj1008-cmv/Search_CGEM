# imports, std lib
import math
import sys
import time

# local imports
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

# I considered adding a timeout, but Aguila handles that well in OTPL.
def set_read_ensure_tolerance_loop(
        set_fn,
        set_kwarg_key: str, 
        read_fn, 
        tolerance: float,
        min_allowed_setpoint: float,
        max_allowed_setpoint: float,
        set_kwds: dict,
        read_kwds: dict = {},
        sleep_duration_between_set_and_read_s: float = 1.0,
        new_setpoint_dampening: float = 0.5) -> float:
    """Ensure abs(set_value - readback) > tolerance; set/read performed user-specified functions/arguments."""
    readback = math.inf
    setpoint = desired_set_value = float(set_kwds[set_kwarg_key])
    iteration = 0
    print('set_fn: ' + str(set_fn))
    print('set_kwarg_key: ' + set_kwarg_key)
    print('read_fn: ' + str(read_fn))
    print('tolerance: '+ str(tolerance))
    print('min_allowed_setpoint: ' + str(min_allowed_setpoint))
    print('max_allowed_setpoint: ' + str(max_allowed_setpoint))
    print(set_kwds)
    print('setpoint: ' + str(setpoint))
    while(abs(desired_set_value - readback) > tolerance):
        logger.info(f'=== set-read iteration {iteration:>2} ===')
        # error-check setpoint before setting
        if (setpoint < min_allowed_setpoint) or (max_allowed_setpoint < setpoint):
            msg = f'Setpoint is outside allowed bounds (max: {max_allowed_setpoint}, min: {min_allowed_setpoint}, set: {setpoint})'
            logger.error(msg)
            raise RuntimeError(msg)
        # set
        logger.info(f'    Setting to {setpoint}')
        set_kwds.update({set_kwarg_key: setpoint})
        set_fn(**set_kwds)
        time.sleep(sleep_duration_between_set_and_read_s)
        # read-back
        readback = float(read_fn(**read_kwds))
        logger.info(f'    Readback after set: {readback}')
        # calculate new setpoint
        setpoint += (setpoint - readback)*new_setpoint_dampening
        iteration += 1
    return readback



### Testing

def _test_set_read_ensure_tolerance_loop():

    class envvar:
        def __init__(self, set_fn):
            self.value = None
            self.set_fn = set_fn
        def set(self, setpoint):
            logger.info(f'{setpoint}')
            self.value = self.set_fn(setpoint)
        def read(self):
            logger.info(f'{self.value}')
            return self.value

    tolerance = 0.004
    # case 1: we can still set voltage
    logger.info('='*50 + 'CASE 1')
    offset_w_error = lambda setpoint: (setpoint - 0.015) + (0.002 * setpoint)
    c1_domain = envvar(set_fn = offset_w_error)
    c1_target = 1.0
    c1_final_readback = set_read_ensure_tolerance_loop(
        set_fn = c1_domain.set,
        set_kwarg_key = 'setpoint',
        set_kwds = {'setpoint' : c1_target},
        read_fn = c1_domain.read,
        tolerance = tolerance,
        min_allowed_setpoint = 0.45,
        max_allowed_setpoint = 1.40,
        sleep_duration_between_set_and_read_s = 0
    )
    assert(abs(c1_final_readback - c1_target) <= tolerance)

    # case 2: voltage set is not responding and our set target is below readback (testing upper limit)
    logger.info('='*50 + 'CASE 2')
    c2_target = 1.0
    always_lower = lambda setpoint: c2_target - tolerance*2
    domain = envvar(set_fn=always_lower)
    try:
        final_readack = set_read_ensure_tolerance_loop(
            set_fn = domain.set,
            set_kwarg_key = 'setpoint',
            set_kwds = {'setpoint' : 1.0},
            read_fn = domain.read,
            tolerance = 0.004,
            min_allowed_setpoint = 0.45,
            max_allowed_setpoint = 1.40,
            sleep_duration_between_set_and_read_s = 0
        )
    except RuntimeError as e:
        logger.info(e)
        logger.info('ran into runtime error, as expected.')

    # case 3: voltage set is not responding and our set target is above readback (testing lower limit)
    logger.info('='*50 + 'CASE 3')
    c2_target = 1.0
    always_lower = lambda setpoint: c2_target + tolerance*2
    domain = envvar(set_fn=always_lower)
    try:
        final_readack = set_read_ensure_tolerance_loop(
            set_fn = domain.set,
            set_kwarg_key = 'setpoint',
            set_kwds = {'setpoint' : 1.0},
            read_fn = domain.read,
            tolerance = 0.004,
            min_allowed_setpoint = 0.45,
            max_allowed_setpoint = 1.40,
            sleep_duration_between_set_and_read_s = 0
        )
    except RuntimeError as e:
        logger.info(e)
        logger.info('ran into runtime error, as expected.')


if __name__ == '__main__':
    _test_set_read_ensure_tolerance_loop()