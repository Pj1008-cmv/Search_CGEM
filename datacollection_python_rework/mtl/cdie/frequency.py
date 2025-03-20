"""Meteorlake compute dielet frequency set and read-back."""

# imports, std library
from concurrent.futures import process
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import mtl.processorinfo
from mtl.sv import get_cdie, set_fuse
from mtl import bootstagetransitions

### Cdie ratios = 100s of MHz (ex: ratio 45 = 4.5GHz)

def freq_to_ratio(freq_GHz: float):
    return int(float(freq_GHz) * 10)

def ratio_to_freq(ratio: int):
    return int(ratio) / 10

### READ

def _read_compute_element_ratio(element: int, cdie=None) -> int:
    if cdie is None:
        cdie = get_cdie()
    return int(eval(f'cdie.dmudata.io_wp_cv_ia_ccp_dvfs_ia_ccp{element}.ia_ratio'))

def read_bigcore_ratio(corenum_physical: int, cdie=None, log=False) -> int:
    """Read big core's ratio (in 100s of MHz)"""
    ratio = _read_compute_element_ratio(corenum_physical + 2, cdie)
    if log:
        logger.info(f'Core {corenum_physical} ratio = {ratio}')
    return ratio

def read_atommod_ratio(modulenum_physical: int, cdie=None, log=False) -> int:
    """Read Atom module's ratio (in 100s of MHz)"""
    ratio = _read_compute_element_ratio(modulenum_physical, cdie)
    if log:
        logger.info(f'Atom module {modulenum_physical} ratio = {ratio}')
    return ratio

def read_ring_ratio(cdie=None) -> int:
    """Read Ring ratio (in 100s of MHz)"""
    if cdie is None:
        cdie = get_cdie()
    return int(cdie.dmudata.io_wp_cv_ring.ratio)*1

def all_core_ratios_valid(active_bigcores, active_atommods, set_ratio) -> bool:
    """Expect that all active elements will have ratio of `set_ratio`, and all other elements 0."""
    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()  # this assumes that SVIPC and ProcInfo singletons have already been created.
    logger.info('Checking all bigcore / atommod set ratios...')
    return all(read_bigcore_ratio(c, log=True) == (set_ratio if c in active_bigcores else 0) for c in processorinfo.valid_physical_bigcores) \
        and all(read_atommod_ratio(a, log=True) == (set_ratio if a in active_atommods else 0) for a in processorinfo.valid_physical_atommods)

### SET

def set_bigcore_ratio_fuse(ratio: int) -> None:
    """Set core ratio via fusing.  Can only occur at cdie fusebreak."""
    bootstagetransitions.ensure_at_cdie_fusebreak()
    logger.info(f'Setting core ratio fuses (p0, p1, pn, min) to {ratio}.')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_p0_ratio  = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_p1_ratio  = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_pn_ratio  = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_min_ratio = {ratio}')

def set_ring_ratio_fuse(ratio: int) -> None:
    """Set ring ratio via fusing.  Can only occur at cdie fusebreak."""
    bootstagetransitions.ensure_at_cdie_fusebreak()
    logger.info(f'Setting ring ratio fuses (p0, p1, pn, min) to {ratio}.')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ring_p0_ratio  = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ring_p1_ratio  = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ring_pn_ratio  = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ring_min_ratio = {ratio}')

def set_atommod_ratio_fuse(ratio) -> None:
    """Set core/atom ratio via fusing.  Can only occur at cdie fusebreak."""
    bootstagetransitions.ensure_at_cdie_fusebreak()
    logger.info(f'Setting core ratio fuses (p0, p1, pn, min) and atom-specific ratio fuses (p1, pn) to to {ratio}.')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_p0_ratio   = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_p1_ratio   = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_pn_ratio   = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_ia_min_ratio  = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_atom_p1_ratio = {ratio}')
    set_fuse(f'cdie.fuses.dmu_fuse.fw_fuses_atom_pn_ratio = {ratio}')

def set_core_ratio_p0_fuse(core_ratio):
    bootstagetransitions.ensure_at_cdie_fusebreak()
    logger.info(f"Setting core ratio (specifically p0) to {core_ratio}")
    set_fuse(f"cdie.fuses.dmu_fuse.fw_fuses_ia_p0_ratio = {core_ratio}")

def set_cdie_p0_ratio_in_soc_fuse(core_ratio: int):
    bootstagetransitions.ensure_at_soc_fusebreak()
    set_fuse(f"soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio = {core_ratio}")