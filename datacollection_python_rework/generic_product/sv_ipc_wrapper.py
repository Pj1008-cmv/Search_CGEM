"""Heavily inspired by OR PPV team's Adapter* classes:
- https://github.com/intel-innersource/applications.manufacturing.system-test.client.arrowlake-p/blob/main/Shared/PythonProject/base/adapters.py
- https://github.com/intel-innersource/applications.manufacturing.system-test.client.arrowlake-p/blob/main/Shared/PythonProject/mtlp682/adapters.py
"""

# imports, std lib
import configparser
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from generic_product.utilities.singleton import Singleton

class PySVOpenIPCWrapper(Singleton):
    """Singleton wrapper for PythonSV and OpenIPC / ipccli."""

    _initialized = False
    need_refresh = True

    is_processor_on_fn = None

    __ipc = None
    __sv = None

    def __init__(self, product: str='', derivative: str='auto', stepping: str='auto', is_processor_on_fn=None, bootstagetransitions=None):
        """Set up IPC / pythonsv variables"""
        if not self._initialized:
            # argument error checking
            if any(arg == '' for arg in [product, derivative, stepping]):
                logger.warning(f'PySVOpenIPCWrapper not properly initialized - product ({product!r}), derivative ({derivative!r}), or stepping ({stepping!r}) is empty string')
                return
            if is_processor_on_fn is None:
                logger.error(f'PySVOpenIPCWrapper not properly initialized - need `is_processor_on_fn` function to tell whether processor is on or not.')
                return
            self.is_processor_on_fn = is_processor_on_fn
            self.bootstagetransitions = bootstagetransitions
            self.product = product
            # ipc
            import ipccli
            self.__ipc = ipccli.baseaccess()
            logger.info('Imported ipccli and instantiated ipccli.baseaccess()')
            # sv
            self.update_pysv_config(product, derivative, stepping)
            # all done!
            PySVOpenIPCWrapper._initialized = True

    def setup_sv(self) -> None:
        import namednodes
        namednodes.settings.PROJECT = self.product
        self.__sv = namednodes.sv
        logger.info('Imported namednodes and obtained reference to namednodes.sv')
        self.need_refresh = True

    @property
    def ipc(self):
        return self.__ipc

    @property
    def sv(self):
        """Descriptor for `self.__sv`.  Ensures we have a valid reference to `namednodes.sv` and performs refresh if needed before returning `self.__sv`.
        
        We can check processor power if we've been given function handle to do so, but I don't want to actually make calls to turn on the processor from this script (imo, out of scope).
        """
        if self.bootstagetransitions \
                and hasattr(self.bootstagetransitions, 'current_stage') and hasattr(self.bootstagetransitions, 'FUSEBREAK_STAGES') \
                and self.bootstagetransitions.current_stage in self.bootstagetransitions.FUSEBREAK_STAGES:
            is_processor_on = True
        else:
            logger.info('Checking whether processor is on before executing sv command...')
            is_processor_on = self.is_processor_on_fn()
        base_error_msg = ''
        # ensure self.__sv has been created (which means namednodes has been imported)
        if self.__sv is None:
            if is_processor_on:
                self.setup_sv()
            else:
                base_error_msg = 'PythonSV object (namednodes.sv) not yet configured'
        # ensure PythonSV refresh/get_all is not currently necessary.
        if self.need_refresh:
            if is_processor_on:
                self.__sv_update(ipc=self.__ipc, sv=self.__sv, get_all=False)  # use actual objects
            else:
                base_error_msg = 'PythonSV object (namednodes.sv) requires refresh'
        # if either of above steps couldn't be completed raise error
        if base_error_msg:
            raise RuntimeError(f'{base_error_msg}. However, cannot do so because processor is off - please ensure processor is powered on.')
        # ensure unit is unlocked before returning reference to sv!
        if self.ipc.islocked():
            self.ipc.unlock()
        # return reference to self.__sv!  If we get here, it exists and it is fresh :)
        return self.__sv

    def __sv_update(self, ipc, sv, get_all=True, force=False):
        """Internal function.  Uses given sv/ipc objects to get_all/refresh namednodes."""
        if self.need_refresh or force:
            logger.info('Performing ipc.forcereconfig()')
            ipc.forcereconfig()
            if ipc.islocked():
                logger.info('Unlocking processor!')
                ipc.unlock()
            if get_all:
                logger.info('Performing sv.get_all()')
                sv.get_all()
            else:
                logger.info('Performing sv.refresh()')
                sv.refresh()
            self.need_refresh = False     

    def get_all(self, force_update: bool=False) -> None:
        """If required (`self.need_refresh`) or specifically requested (`force_update`), perform:
        - `ipc.forcereconfig()`
        - `ipc.unlock()        # if unit isn't already unlocked`
        - `sv.get_all()        # should be used over sv.refresh() according to docs`

        docs reference: https://docs.intel.com/documents/PythonSv/PythonSv/Training/pythonsv_bkms.html#dont-call-namednodes.sv.refresh-unless-needed-use-get_all
        """
        self.__sv_update(ipc=self.ipc, sv=self.sv, force=force_update)  # use descriptors

    def refresh(self, force_update: bool=False) -> None:
        """NOTE: self.get_all() is preferred over self.refresh().  See:
        https://docs.intel.com/documents/PythonSv/PythonSv/Training/pythonsv_bkms.html#dont-call-namednodes.sv.refresh-unless-needed-use-get_all
        
        If required (`self.need_refresh`) or specifically requested (`force_update`), perform:
        - `ipc.forcereconfig()`
        - `ipc.unlock()        # if unit isn't already unlocked`
        - `sv.refresh()`
        """
        self.__sv_update(ipc=self.ipc, sv=self.sv, get_all=False, force=force_update)  # use descriptors

    @staticmethod
    def translate_stepping_to_pysv_config_stepping(stepping: str) -> str:
        """If needed, can remap.  Ex: If P682 A2/A3 both use 'A2' as stepping, that translation happens here."""
        if stepping.lower() == 'auto':
            return 'Auto'
        return stepping

    @staticmethod
    def translate_prod_deriv_into_sku(product: str, derivative: str) -> str:
        if derivative.lower() == 'auto':
            return 'Auto'
        mapping = {
            ('meteorlake', 'p682') : 'mtlp682',
            ('meteorlake', 'p281') : 'mtlp281',
        }
        try:
            retval = mapping[(product.lower(), derivative.lower())]
        except KeyError:
            logger.error(f'Product and/or derivative not defined in mapping dict (product.lower(): {product.lower()}) (derivative.lower(): {derivative.lower()})')
            raise
        return retval

    def update_pysv_config(self, product, derivative, stepping, pysv_inifile=r'C:\pythonsv\pysv_config.ini'):
        """Update pysv_config.ini file with specified product, derivative, and stepping.
        
        contents of ini file:
        - product matches python sv project name (ex: 'meteorlake', 'tigerlake', 'tigerlake_pch')
        - sku = 'mtlp682', 'mtlp281'
        - stepping = 'B0', 'C0'
        """
        parser = configparser.ConfigParser()

         # Open and read the pysv_config.ini file
        parser.read(pysv_inifile)

        if product in parser:
            logger.info(f'Update pysv_config.ini for {product}')
            parser[product]['sku'] = self.translate_prod_deriv_into_sku(product, derivative)
            parser[product]['stepping'] = self.translate_stepping_to_pysv_config_stepping(stepping)
            for item, value in parser[product].items():
                logger.info(f"{item:>40} : {value}")
        else:
            logger.error(msg:=f"{product} not already present in pysv_config.ini file.  Please run start script once manually.")
            raise RuntimeError(msg)

        # Write out our new pysv_config.ini file
        with open(pysv_inifile, 'w') as configfile:
            parser.write(configfile)

        # clear parser cache 
        parser.clear()

        self._need_refresh = True