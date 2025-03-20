# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from generic_product.processorinfo import BaseProcessorInfo
from generic_product.utilities import classcsv
from generic_product.utilities import pds
from generic_product.utilities.pysv_script_manager import PySVScriptManager
from mtl.cdie import physical_to_logical

fuse_utils_script = PySVScriptManager('meteorlake.debug.domains.fuse.fuse_utils')

class MeteorlakeProcessorInfo(BaseProcessorInfo):
    """Singleton that stores information about MTL processor.
    

    IDEAS
    - Can init with a flag that tells us whether it was created as part of automation flow or not.
      Then, in scripts that use the processorinfo object, can add checks that only run during automation?

    - If we run on an automated handler, can load entire class dict once at the beginning and reuse
      until lot end.  Overkill for running on RVP.
    """

    MRS_LOOKUP_FOLDER = r'I:\cmv\or\mtl\ProductInfo\MRS_pull'

    pds_lookup_script = None
    bigcore_physical_logical_core_mapping = atom_physical_logical_core_mapping = None

    def __init__(self):
        BaseProcessorInfo.__init__(self)

    def _import_pds_lookup(self):
        if (cellstatuszone:=r'I:\cmv\or\mtl\Scripts\cell_status') not in sys.path:
            sys.path.append(cellstatuszone)
        import utils.visualid_to_pds
        self.pds_lookup_script = utils.visualid_to_pds

    def read_visualid(self) -> str:
        """Read processor's unique identifier (visual ID).  Store in ProcessorInfo singleton and return."""
        logger.info('Reading processor visual ID!')
        if self.visualid is not None:
            logger.warning(f'ProcessorInfo.visualid already has a value ({self.visualid})')        
        assert(self._pysv_ipc_wrapper.ipc.isunlocked())
        self.visualid = fuse_utils_script.visual_ID()
        logger.info(f'visual ID: {self.visualid}')
        return self.visualid

    def read_qdf(self) -> str:
        """Read processor's QDF.  Store within ProcessorInfo singleton and return."""
        logger.info('Reading processor QDF!')
        if self.qdf is not None:
            logger.warning(f'ProcessorInfo.qdf already has a value ({self.qdf})')
        assert(self._pysv_ipc_wrapper.ipc.isunlocked())
        self.qdf = fuse_utils_script.qdf()
        logger.info(f'QDF: {self.qdf}')
        return self.qdf

    def visualid_to_pds(self):
        """Look up processor's Visual ID and return product/derivative/stepping.
        The code lives in the I: `cell_status` area.
        """
        logger.info('Looking up product/derivative/stepping based on visual ID!')
        # import cell status visualid -> pds script
        if self.pds_lookup_script is None:
            self._import_pds_lookup()
        # ensure we have a visual id
        if self.visualid is None:
            self.read_visualid()
        # convert
        self.pds = self.pds_lookup_script.visualid_to_pds(
            visualid=self.visualid,
            mrs_lookup_folder=self.MRS_LOOKUP_FOLDER,
            debug_print=True,
            debug_printer=logger.info,
        )
        logger.info(f'PDS: {self.pds}')
        # update pds in pysv config file
        self._pysv_ipc_wrapper.update_pysv_config(product='meteorlake', derivative=self.pds[1], stepping=self.pds[2])
        self._pysv_ipc_wrapper.get_all()
        return self.pds

    def pds_to_classdict(self):
        """product/derivative/stepping -> classdict from I: area.  Return `classdict[visualid]`"""
        logger.info('Looking up classdict based on product/derivative/stepping and visualid!')
        # import cell status visualid -> pds script
        if self.pds_lookup_script is None:
            self._import_pds_lookup()
        # ensure we have a visual id and p/d/s
        if self.visualid is None:
            self.read_visualid()
        if any([i is None for i in self.pds]):  # if prod, deriv, or step are None
            self.visualid_to_pds()
        # get pds_config.json file -> class.csv -> open class.csv
        self.projectdir = self.pds_lookup_script.pds_to_projectdir(*self.pds)
        classcsvfile = pds.PDS.open_pds_config_and_expand_relative_paths(f'{self.projectdir}\pds_config.json')['class.csv']
        self.classdata = classcsv.csv_to_dict(classcsvfile)[self.visualid]
        logger.info(f'Unit has {len(self.classdata)} rows of class data.')
        return self.classdata
    
    def create_physical_to_logical_core_map(self) -> dict:
        """Read processor's core disable register, and calculate mapping between physical and logical cores.
        Store within ProcessorInfo singleton and return dict.
        """
        logger.info('Reading LLC slice disable fuse to compute physical : logical core maps for big core and atom!')
        # read the fuse from the processor
        cdie = self._pysv_ipc_wrapper.sv.socket0.compute0
        cdie.fuses.load_fuse_ram()
        slice_disable_mask = cdie.fuses.dmu_fuse.fw_fuses_llc_slice_ia_core_dis
        # compute and store mapping
        (self.bigcore_physical_logical_core_mapping, self.atom_physical_logical_core_mapping) \
            = ret_tuple = physical_to_logical.create_physical_logical_map(slice_disable_mask)
        # print to user
        logger.info(f'Slice disable mask fuse: {slice_disable_mask}')
        logger.info(f'big core map: {self.bigcore_physical_logical_core_mapping}')
        logger.info(f'atom mod map: {self.atom_physical_logical_core_mapping}')
        return ret_tuple

    def get_number_of_cores(self):
        """Looks up valid compute elements (big cores, atom modules, etc.) that have Class data."""
        valid_atommods = set()
        valid_bigcores = set()
        for (testtype, corner, element) in self.classdata:
            if 'cdie atom' in testtype.lower():
                valid_atommods.add(int(element))
            elif 'avx' in testtype.lower():
                valid_bigcores.add(int(element))
        self.valid_physical_bigcores = valid_bigcores
        self.valid_physical_atommods = valid_atommods
        logger.info(f'Valid physical big cores, based on class data: {valid_bigcores}')
        logger.info(f'Valid physical atom mods, based on class data: {valid_atommods}')
        return (valid_bigcores, valid_atommods)