# imports, std lib
import importlib
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from generic_product.utilities.singleton import PerArgumentSingleton

class PySVScriptManager(PerArgumentSingleton):
    """Wraps PythonSV scripts that use global sv references
    (ex: dielet variables, like `cdie`).
    
    Only import script when a specific function is attribute is accessed,
    as opposed to upon object creation.
    """
    
    def __init__(self, pysv_script_import_path: str):
        self._pysv_script = None
        self._pysv_script_import_path = pysv_script_import_path

    def __getattr__(self, attr):
        if self._pysv_script is None:
            logger.info(f'Importing PythonSV script: {self._pysv_script_import_path}')
            self._pysv_script = importlib.import_module(self._pysv_script_import_path)
        else:
            self.reload_script()
        return self._pysv_script.__getattribute__(attr)
    
    def reload_script(self):
        if self._pysv_script is None:
            logger.error('Cannot re-import PythonSV script without it first being imported.')
            return
        logger.info(f'Re-importing PythonSV script: {self._pysv_script_import_path}')
        self._pysv_script = importlib.reload(self._pysv_script)
        