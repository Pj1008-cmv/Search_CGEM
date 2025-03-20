# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import mtl.cdie.frequency as cdie_frequency
import mtl.gcd.frequency as gcd_frequency
import mtl.gcd.fuse_overrides as gcd_fuseovs
import mtl.processorinfo
import mtl.soc.fuse_overrides as soc_fuseovs
import mtl.sv
from mtl import bootstagetransitions

def execute_fuse_recipe(fcorner: str):
    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()  # this assumes that SVIPC and ProcInfo singletons have already been created.
    gt_freq_set = float(processorinfo.classdata[('GT', fcorner, 'N/A')]['Frequency'])

    # set GCD, SOC fuses
    bootstagetransitions.perform_transition(to_stage=bootstagetransitions.SOC_FUSEBREAK)
    # gcd_fuseovs.disable_gcd_cep()  # per Hsin, no longer disabling CEP via fusing.
    gcd_fuseovs.disable_gt_itd()
    gcd_fuseovs.set_gcd_tj_max(tj_max=120)
    soc_fuseovs.set_soc_tj_max(tj_max=120)
    gcd_frequency.set_gt_freq(freq_GHz=gt_freq_set)

    # set Cdie fuses
    bootstagetransitions.perform_transition(to_stage=bootstagetransitions.CDIE_FUSEBREAK)
    cdie_frequency.set_bigcore_ratio_fuse(ratio=8)

    # boot to EFI, verify all set fuses (happens after transition to EFI)
    bootstagetransitions.perform_transition(to_stage=bootstagetransitions.EFI_STAGE)

    # verify necessary registers (separate from fuses)
    assert gcd_frequency.read_gt_freq() == gt_freq_set