"""Meteorlake graphics dielet frequency set and read-back."""

# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from mtl.sv import set_fuse
from mtl import bootstagetransitions

def disable_gt_itd():
    """Disable ITD on GCD."""
    bootstagetransitions.ensure_at_soc_fusebreak()
    logger.info('Disabling GCD ITD.')
    set_fuse('soc.south.fuses.punit_fuse.fw_fuses_gt_itd_cutoff_v  = 0')
    set_fuse('soc.south.fuses.punit_fuse.fw_fuses_gt_itd_slope     = 0')
    set_fuse('soc.south.fuses.punit_fuse.fw_fuses_gt_itd_cutoff_v2 = 0')
    set_fuse('soc.south.fuses.punit_fuse.fw_fuses_gt_itd_slope2    = 0')

def disable_gcd_cep():
    """Disable CEP on GCD."""
    bootstagetransitions.ensure_at_soc_fusebreak()
    logger.info('Disabling GCD CEP via fusing.')
    set_fuse('soc.south.fuses.punit_fuse.fw_fuses_gt_cep_enable = 0')

def set_gcd_tj_max(tj_max: int):
    """Set GCD max transistor junction temperature (TJmax)."""
    bootstagetransitions.ensure_at_soc_fusebreak()
    logger.info(f'Setting GCD TJmax to {tj_max}C.')
    set_fuse(f'soc.south.fuses.punit_fuse.fw_fuses_gfx_tj_max = {tj_max}')