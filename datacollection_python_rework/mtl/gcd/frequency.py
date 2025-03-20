"""Meteorlake graphics dielet frequency set and read-back."""

# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import mtl.gcd.shared_vars as gcd_shared_vars
from mtl.sv import set_fuse, get_soc
from mtl import bootstagetransitions

def gt_freq_to_ratio(gt_freq_GHz: float) -> int:
    """GT freq (GHz) -> ratio (50s of MHz)"""
    return int(gt_freq_GHz * 1000) / 50

def gt_ratio_to_freq_GHz(gt_ratio: int) -> float:
    return (gt_ratio * 50) / 1000

### READ

def read_gt_ratio(soc=None) -> int:
    """Read GT ratio.    
    TODO why divided by three ?"""
    if soc is None:
        soc = get_soc()
    return int(soc.north.pcudata.io_wp_cv_gt.ratio / 3)

def read_gt_freq(soc=None) -> float:
    """Read GT freq in GHz (ratio -> freq)"""
    return gt_ratio_to_freq_GHz(read_gt_ratio(soc))

### SET

def set_gt_ratio(ratio: int) -> None:
    """Sets GT ratio to fusing - requires being at SOC fusebreak."""
    ratio = int(ratio)  # just in case
    bootstagetransitions.ensure_at_soc_fusebreak()
    logger.info(f'Setting GT ratio to {ratio}.')
    set_fuse(f'soc.south.fuses.punit_fuse.fw_fuses_gt_pn_ratio  = {ratio}')
    set_fuse(f'soc.south.fuses.punit_fuse.fw_fuses_gt_p0_ratio  = {ratio}')
    set_fuse(f'soc.south.fuses.punit_fuse.fw_fuses_gt_p1_ratio  = {ratio}')
    set_fuse(f'soc.south.fuses.punit_fuse.fw_fuses_gt_min_ratio = {ratio}')
    gcd_shared_vars.gt_ratio = ratio

def set_gt_freq(freq_GHz: float) -> None:
    """Sets GT freq (-> ratio) to fusing - requires being at SOC fusebreak."""
    set_gt_ratio(gt_freq_to_ratio(freq_GHz))