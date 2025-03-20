import functools
import sys
import timeit

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

# decorator
def log_runtime(func):
    @functools.wraps(func)
    def wrapper(*args, **kwds):
        start = timeit.default_timer()
        retval = func(*args, **kwds)
        stop = timeit.default_timer()
        logger.info(f'{func.__name__} took {stop-start:0.5f}s to execute')
        return retval

# context manager
class LogRuntime():
    def __enter__(self):
        self.start = timeit.default_timer()
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop = timeit.default_timer()
        logger.info(f'Execution took {self.stop-self.start:0.5f}s.')