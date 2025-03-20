# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from mtl.sv import set_fuse
from mtl import bootstagetransitions

def set_soc_tj_max(tj_max: int):
    """Set SOC max transistor junction temperature (TJmax)."""
    bootstagetransitions.ensure_at_soc_fusebreak()
    logger.info(f'Setting SOC TJmax to {tj_max}C.')
    set_fuse(f'soc.south.fuses.punit_fuse.fw_fuses_soc_tj_max = {tj_max}')

def disable_soc_atom():
    bootstagetransitions.ensure_at_soc_fusebreak()
    set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_logical_core_disable_mask = 0x3")
    logger.info("Disabled SOC CMT")