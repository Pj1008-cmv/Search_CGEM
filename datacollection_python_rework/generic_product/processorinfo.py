"""
NOTES
- currently, the visualid and pds lookup functions use product-specific imports. options:
    - have the functions take an argument to prod-specific scripts
    - use this as a base class for a product-specific implimentation?

"""

# imports, std lib
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from generic_product.utilities.singleton import Singleton
from generic_product.sv_ipc_wrapper import PySVOpenIPCWrapper

class BaseProcessorInfo(Singleton):
    """Singleton object that stores information about the processor.
    
    This is the base class - its methods aren't fully implemented!
    """

    _pysv_ipc_wrapper = None

    classdata = None
    pds = None
    projectdir = None
    obtained_unit_info = False
    qdf = None
    valid_physical_atommods = None
    valid_physical_bigcores = None
    visualid = None
    
    def __init__(self, force_obtain_unit_values=False):
        if self._pysv_ipc_wrapper is None:
            self._pysv_ipc_wrapper = PySVOpenIPCWrapper()
        if self._pysv_ipc_wrapper.ipc.islocked() or self._pysv_ipc_wrapper.need_refresh:
            logger.warning('ProcessorInfo singleton created, but no values have been populated because SV needs a refresh or unit is locked.')
            return
        # only obtain values if the processor is already on
        if self._pysv_ipc_wrapper.is_processor_on_fn() and (not self.obtained_unit_info or force_obtain_unit_values):
            self.obtain_unit_values()
        
    def obtain_unit_values(self):
        self.read_visualid()
        self.read_qdf()
        self.visualid_to_pds()
        self.pds_to_classdict()
        self.create_physical_to_logical_core_map()
        self.get_number_of_cores()
        self.obtained_unit_info = True

    def clear_unit_values(self):
        """Look through all object members and sets all variables that meet specific criteria to `None`.
        
        Variable name criteria:
        - name is all lowercase (not a constant, which is all upper)
        - name doesn't start with '_' (excluding private and dunder variables)
        - is not a function (it's not callable)
        - doesn't contain 'script' (to allow persistence of `fuse_utils` script reference)
        """
        vars = [attr for attr in dir(self) if 
            not callable(getattr(self, attr))   # exclude functions
            and not attr.startswith('_')        # exclude dunders, "private" variables
            and attr.islower()                  # exclude constants
            and 'script' not in attr            # exclude fuse_utils_script (and other dynamic imports)
        ]
        for v in vars:
            setattr(self, v, None)
        self.obtained_unit_info = False

    def read_visualid(self) -> str:
        """Read processor's unique identifier (visual ID).  Store within ProcessorInfo singleton and return."""
        raise NotImplementedError

    def read_qdf(self) -> str:
        """Read processor's QDF.  Store within ProcessorInfo singleton and return."""
        raise NotImplementedError

    def create_physical_to_logical_core_map(self) -> dict:
        """Read processor's core disable register, and calculate mapping between physical and logical cores.
        Store within ProcessorInfo singleton and return dict."""
        raise NotImplementedError

    def visualid_to_pds(self):
        """Look up processor's Visual ID and return product/derivative/stepping.
        The code lives in the I: `cell_status` area.
        """
        raise NotImplementedError

    def pds_to_classdict(self):
        """product/derivative/stepping -> classdict from I: area.  Return `classdict[visualid]`"""
        raise NotImplementedError

    def get_number_of_cores(self):
        """Looks up valid compute elements (big cores, atom modules, etc.) that have Class data."""
        raise NotImplementedError