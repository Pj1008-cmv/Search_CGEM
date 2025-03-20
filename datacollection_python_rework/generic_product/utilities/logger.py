"""Drop-in replacement for python's built-in logger for Fusion/Aguila automation.

Based on OR PPV's:
https://github.com/intel-innersource/applications.manufacturing.system-test.client.arrowlake-p/blob/main/Shared/PythonProject/base/utilities/base_logger.py
"""

import logging
import inspect
import time
from datetime import datetime

automation_mode = False

# internal logger - for outputting to file
#   field names: https://docs.python.org/3/library/logging.html#logrecord-attributes
#   style:       https://docs.python.org/3/library/logging.html#logging.Formatter
#                https://docs.python.org/3/howto/logging-cookbook.html#formatting-styles
#   optimizations - disabling automatic collection of unused information
#                https://docs.python.org/3/howto/logging.html#optimization
__logger = logging.getLogger('to_file')
__logger.setLevel(logging.INFO)
__filehandler = logging.FileHandler('C:\Logs\datacollection_python.log', mode='w')
__filehandler.setLevel(logging.INFO)
__filehandler.setFormatter(logging.Formatter('{message}', style='{'))
__logger.addHandler(__filehandler)
logging.logThreads = False
logging.logProcess = False
logging.Multiprocessing = False


### stand-alone functions

##toplevel = r'applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp'
toplevel = r'C:\SVSHARE\cmv_client_automation_mtl'

def log_message(level: str, message: str, stackpos: int=2):
    """Logs message to standard out with calling script/function."""
    timestamp = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    stack = inspect.stack()
    filename = stack[stackpos].filename.replace(toplevel + '\\', '').replace('\\', '.').replace('.py', '')
    function = stack[stackpos].function
    if automation_mode:
        print(                     fr'[{level:>7}]{filename:>55}.{function:<40} {message}')
        __logger.info(fr'[{timestamp}][{level:>7}]{filename:>55}.{function:<40} {message}')  # log with timestamp
    else:
        print(msg:=   fr'[{timestamp}][{level:>7}]{filename:>55}.{function:<40} {message}')
        __logger.info(msg)

def critical(message, stackpos: int=2):
    """Logs critical message to standard out with calling script/function."""
    log_message('CRITICAL', message, stackpos)

def error(message, stackpos: int=2):
    """Logs error message to standard out with calling script/function."""
    log_message('ERROR', message, stackpos)

def warning(message, stackpos: int=2):
    """Logs warning to standard out with calling script/function."""
    log_message('WARNING', message, stackpos)

def info(message, stackpos: int=2):
    """Logs info message to standard out with calling script/function."""
    log_message('INFO', message, stackpos)

def debug(message, stackpos: int=2):
    """Logs debug message to standard out with calling script/function."""
    log_message('DEBUG', message, stackpos)