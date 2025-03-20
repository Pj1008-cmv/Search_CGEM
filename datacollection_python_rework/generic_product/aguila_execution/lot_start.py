"""
"""

# imports, std lib
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import generic_product.hardware.nevo as nevo
import generic_product.hardware.hostpc
import generic_product.utilities.profiling

# ensure logger is set to "automation" mode (no timestamps -- Aguila already has them!)
logger.automation_mode = True

# Initialize and set up Nevo singleton object (happens once for entire lot)
nevo_singleton = nevo.Nevo()
assert nevo_singleton._performed_first_init
assert nevo_singleton._state == nevo.NevoStates.ENUMERATED
logger.info('Initialized Nevo and enumerated all channels.')

# Create profiling runner
profiler = generic_product.utilities.profiling.ProfilingRunner()