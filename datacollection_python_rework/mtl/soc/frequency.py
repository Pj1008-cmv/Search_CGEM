"""Meteorlake SOC dielet frequency set and read-back."""

# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import mtl.bootstagetransitions as bootstagetransitions
import mtl.soc.shared_vars as soc_shared_vars
from mtl.sv import get_soc

### READ

# def read_soc_atom_ratio() -> int:
#     """Reads SOC Atom module ratio (100s of MHz)"""
#     soc = get_soc()
#     pll_cmt = int(soc.north.pcudata.io_wp_cv_ia_ccp_dvfs_ia_ccp0.ia_ratio)/1 * 100
#     logger.info(f"SOC_CMT Clock Readback Freq: {pll_cmt} (vs setpoint: {soc_shared_vars.G_cmt})")
#     return pll_cmt

# def SOC_Media_Ratio_Profile():
#     print("Profiling: Media set point: " + str(globalVars.G_media))
#     #print ("{0}._custom_fuseOv: Warning: Found Class Data. CDclk Freq is - {1}".format(selfname, globalVars.G_cdclk))
#     #need to find read fuse
#     pll_media = int(soc.north.pcudata.io_wp_cv_media.ratio)/3*50
#     print("Profiling: SOC Media Clock Readback Freq: " + str(pll_media))
#     return pll_media

# def SOC_Cdclk_Ratio_Profile():
#     print("Profiling: CDclk set point: " + str(globalVars.G_cdclk))
#     #print ("{0}._custom_fuseOv: Warning: Found Class Data. CDclk Freq is - {1}".format(selfname, globalVars.G_cdclk))
#     #need to find read fuse
#     pll_cdclk = int(soc.north.disp.igfxhwregsdisp1.cdclk_ctl.cd_frequency_decimal)/2
#     print("Profiling: SoC CD Clock Readback Freq: " + str(pll_cdclk))
#     return pll_cdclk
    
# def SOC_Fclk_Ratio_Profile():
    
#     globalVars.G_fclk = round(globalVars.G_fclk/16.667)
#     print("Profiling: Fclk set point: " + str(globalVars.G_fclk))
#     # print ("{0}._custom_fuseOv: Warning: Found Class Data. Fclk Freq is - {1}".format(selfname, fuseovs_soc.G_fclk))#warning
    
#     # print("NOTE: READING soc.south.fuses.sa_pll.ccu_fuse_ccu_freq_group1_fuse_cfgcr_psf0_ratio")
#     # pll_fclk = int(soc.south.fuses.sa_pll.ccu_fuse_ccu_freq_group1_fuse_cfgcr_psf0_ratio)
#     pll_fclk = int(soc.north.pcudata.io_wp_cv_psf0.ratio)*16.667
#     # soc.north.pcudata.io_wp_cv_psf0.ratio
#     print("Profiling: SoC F Clock Readback Freq: " + str(pll_fclk))
#     return pll_fclk


# def SOC_Nclk_Ratio_Profile():
#     print("Profiling: Nclk set point: " + str(globalVars.G_nclk))
#     # print ("{0}._custom_fuseOv: Warning - Found Class Data. Nclk Freq is {1}".format(selfname, fuseovs_soc.G_nclk))#warning
    
#     pll_nclk = int(soc.north.ngu_pma.ngu_pma_cr_top.ngu_nclk_cfg.ngu_nclk_ratio)/1 * 100
#     print("Profiling: SoC N Clock Readback Freq: " + str(pll_nclk))
#     return pll_nclk

# def SOC_Qclk_Ratio_Profile():
#     print("Profiling: Qclk set point: " + str(globalVars.G_qclk))
#     # print ("{0}._custom_fuseOv: Warning - Found Class Data. Qclk Freq is {1}".format(selfname, fuseovs_soc.G_qclk))#warning
#     #qclk
#     #checks gear speed
#     gear4 = soc.north.mem.ddrphy.ddrphy_ddrcomp_sbmem.ddrpll_cr_workpoint0_0_0_0_mchbar.gear4
#     pll_qclk = soc.north.mem.ddrphy.ddrphy_ddrcomp_sbmem.ddrpll_cr_workpoint0_0_0_0_mchbar.qclkratio
#     pll_qclk = float(round(float(pll_qclk)/1 * 33.33))
    
#     if gear4:
#         print("Running at 4th gear")
#     else:
#         print("Running at 2nd gear")
#     # if gear4:
#     #     pll_qclk = int(int(soc.north.mem.ddrphy.ddrphy_ddrcomp_sbmem.ddrpll_cr_workpoint0_0_0_0_mchbar.qclkratio)/266.6) #Gear4 mode
#     # else:
#     #     pll_qclk = int(int(soc.north.mem.ddrphy.ddrphy_ddrcomp_sbmem.ddrpll_cr_workpoint0_0_0_0_mchbar.qclkratio)/133.3)
    
#     # pll_qclk = int(soc.north.mem.ddrphy.ddrphy_ddrcomp_sbmem.ddrpll_cr_workpoint0_0_0_0_mchbar.qclkratio)
   
#     print("Profiling: SoC Q Clock Readback Freq: " + str(pll_qclk))
#     return pll_qclk

# @print_raw_data_point
# def VPU_vpuclk_Ratio_Profile():
#     return soc.north.vpu_btrs.vpu_btrs_bar2_space.pll_frequency_ratio.final_pll_freq/1.0

# ### SET

# def ensure_at_soc_fusebreak():
#     if bootstagetransitions.current_stage != bootstagetransitions.SOC_FUSEBREAK:
#         logger.error(msg:=f"Can only set soc ratio during SOC fusebreak.")
#         raise RuntimeError(msg)