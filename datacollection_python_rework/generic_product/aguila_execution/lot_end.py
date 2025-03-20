# imports, std lib
import sys

# local imports
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import generic_product.hardware.nevo as nevo

# cleanup: terminate Nevo connection
nevo_singleton = nevo.Nevo()
nevo_singleton.terminate()
assert nevo_singleton._active is False
logger.info('Nevo connection terminated.')