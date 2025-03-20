"""
NOTE core_vf_fuses() is removed from original fuseOvs.
NOTE set Avx256_delta() function is removed for now (need to consolidate the experts)
"""

# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from mtl import bootstagetransitions
from mtl.sv import set_fuse, arbitrary_fuse_loop, fuse_loop

CORE_MASK = {
    'C0'    : 0xFEFF,
    'C1'    : 0xFDFF,
    'C2'    : 0xFBFF,
    'C3'    : 0xF7FF,
    'C4'    : 0xEFFF,
    'C5'    : 0xDFFF,
    
    'A0'    : 0xFFF0,
    'A1'    : 0xFF0F,
    
    'A'     : 0xFF00,
    'C'     : 0xC0FF,
    
    'AC'    : 0xC000
}

### Misc

def get_keylocker_state():
    pass

def set_cdie_core_mask(fuse_core: str):
    bootstagetransitions.ensure_at_cdie_fusebreak()
    fuse_mask = CORE_MASK[fuse_core.upper()]
    logger.info(f"Setting fuse mask to {hex(fuse_mask)}")
    set_fuse(f"cdie.fuses.dmu_fuse.fw_fuses_ia_logical_core_disable_mask = {fuse_mask}")

def set_dca(value: int):
    bootstagetransitions.ensure_at_cdie_fusebreak()
    # first fuse is enables, second sets.
    arbitrary_fuse_loop( 'cdie.fuses.core<INDEX>_fuse.core_fuse_pll_fuse_fusecr_dcc_0_dcs_run_mode = 0x0')
    arbitrary_fuse_loop(f'cdie.fuses.core<INDEX>_fuse.core_fuse_pll_fuse_fusecr_dcc_0_dcs_offset_dca_static = {value}')
    
### Disabling / zero-ing out fuses

def zero_out_cdie_deltas_in_soc():
    """Fuses being zero'd:
    - `soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group<INDEX>_atom_delta`
    - `soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group<INDEX>_bigcore_delta`
    - `soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_<INDEX>`
    - `soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_<INDEX>`
    - `soc.south.fuses.punit_fuse.fw_fuses_ccp_0_ia_p0_ratio_downbin`
    """
    bootstagetransitions.ensure_at_soc_fusebreak()
    fuse_loop('soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group<INDEX>_atom_delta = 0', num_loops=8)
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group0_atom_delta = 0")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group1_atom_delta = 0")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group2_atom_delta = 0")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group3_atom_delta = 0")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group4_atom_delta = 0")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group5_atom_delta = 0")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group6_atom_delta = 0")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group7_atom_delta = 0")
    fuse_loop('soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group<INDEX>_bigcore_delta = 0', start_index=1, num_loops=8)
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group1_bigcore_delta = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group2_bigcore_delta = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group3_bigcore_delta = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group4_bigcore_delta = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group5_bigcore_delta = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group6_bigcore_delta = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_p0_ratio_group7_bigcore_delta = 0 ")
    fuse_loop('soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_<INDEX> = 0', num_loops=10)
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_0 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_1 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_2 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_3 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_4 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_5 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_6 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_7 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_8 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ia_int_vf_delta_9 = 0 ")
    fuse_loop('soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_<INDEX> = 0', num_loops=10)
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_0 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_1 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_2 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_3 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_4 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_5 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_6 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_7 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_8 = 0 ")
    # set_fuse("soc.south.fuses.punit_fuse.fw_fuses_ccp_0_pcvf_vf_delta_9 = 0 ")
    set_fuse('soc.south.fuses.punit_fuse.fw_fuses_ccp_0_ia_p0_ratio_downbin = 0')

def disable_c_state():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_die_c_state  = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_core_c_state = 0")

def zero_cdie_itd_fuses():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    # Core ITD Fuses
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_itd_cutoff_tj      = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ia_itd_cutoff_v    = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ia_itd_cutoff_v2   = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ia_itd_slope       = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ia_itd_slope2      = 0")
    # Atom ITD fuses
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_atom_itd_cutoff_v  = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_atom_itd_cutoff_v2 = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_atom_itd_slope     = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_atom_itd_slope2    = 0")
    # Ring ITD fuses
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ring_itd_cutoff_v  = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ring_itd_cutoff_v2 = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ring_itd_slope     = 0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ring_itd_slope2    = 0")

def zero_out_p0_big_core_delta():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    arbitrary_fuse_loop(f"cdie.fuses.dmu_fuse.fw_fuses_ia_p0_ratio_<INDEX>_bigcore_delta = 0x0", start_index=2)

def zero_out_p0_atom_delta():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    arbitrary_fuse_loop(f"cdie.fuses.dmu_fuse.fw_fuses_ia_p0_ratio_<INDEX>_atom_delta = 0x0", start_index=1)

def zero_out_p0_avx_delta():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ia_p0_ratio_avx256_delta = 0x0")
    set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ia_p0_ratio_avx512_delta = 0x0")

def zero_out_p0_downbins():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    arbitrary_fuse_loop(f"cdie.fuses.dmu_fuse.fw_fuses_ccp_<INDEX>_ia_p0_ratio_downbin = 0x0")

def zero_out_avx_VF_deltas():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    arbitrary_fuse_loop(f"cdie.fuses.dmu_fuse.fw_fuses_ia_avx256_vf_delta_<INDEX> = 0x0")
    arbitrary_fuse_loop(f"cdie.fuses.dmu_fuse.fw_fuses_ia_avx512_vf_delta_<INDEX> = 0x0")
    arbitrary_fuse_loop(f"cdie.fuses.dmu_fuse.fw_fuses_ia_int_vf_delta_<INDEX> = 0x0")
    
def zero_out_vf_deltas_all_cores():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    for ccp_num in range(0, 16):
        arbitrary_fuse_loop(f"cdie.fuses.dmu_fuse.fw_fuses_ccp_{ccp_num}_pcvf_vf_delta_<INDEX> = 0x0")

def disable_afs_cdie():
    bootstagetransitions.ensure_at_cdie_fusebreak()
    # Clear ring AFS enable bit
    set_fuse("cdie.fuses.ccf_pll.ringpll_fuse_fusecr_afs_0_afs_enable = 0x0")
    # Clear atom AFS enable bits
    set_fuse("cdie.fuses.atom0_fuse.fb_ljpll_fusecr_afs_0_afs_enable_fuse = 0x0")
    set_fuse("cdie.fuses.atom1_fuse.fb_ljpll_fusecr_afs_0_afs_enable_fuse = 0x0")
    # Clear core AFS enable bits
    set_fuse("cdie.fuses.core0_fuse.core_fuse_pll_fuse_fusecr_afs_0_afs_enable = 0x0")
    set_fuse("cdie.fuses.core1_fuse.core_fuse_pll_fuse_fusecr_afs_0_afs_enable = 0x0")
    set_fuse("cdie.fuses.core2_fuse.core_fuse_pll_fuse_fusecr_afs_0_afs_enable = 0x0")
    set_fuse("cdie.fuses.core3_fuse.core_fuse_pll_fuse_fusecr_afs_0_afs_enable = 0x0")
    set_fuse("cdie.fuses.core4_fuse.core_fuse_pll_fuse_fusecr_afs_0_afs_enable = 0x0")
    set_fuse("cdie.fuses.core5_fuse.core_fuse_pll_fuse_fusecr_afs_0_afs_enable = 0x0")

# WARNING: DO NOT DISABLE CEP THROUGH FUSEOVS FOR MTL.  FUNCTION COMMENTED OUT SO PEOPLE DONT USE IT  
# def cep_dis_cdie():
#     bootstagetransitions.ensure_at_cdie_fusebreak()
#     set_fuse("cdie.fuses.dmu_fuse.fw_fuses_ia_cep_enable = 0")