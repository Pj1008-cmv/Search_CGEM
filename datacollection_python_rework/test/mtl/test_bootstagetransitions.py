import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger
import generic_product.utilities.timer as timer
import mtl.bootstagetransitions as bst

generic_product.utilities.logger.setup_logging()

def boot_through_stages_with_verification(stage_list):
    with timer.LogRuntime():
        for stage in stage_list:
            bst.perform_transition(to_stage=stage)
            assert bst.current_stage == stage

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_all_breakstages_to_EFI(processor_turn_on_before_turn_off_after_test):
    boot_through_stages_with_verification(
        [bst.SOC_FUSEBREAK, bst.IOE_FUSEBREAK, bst.GCD_FUSEBREAK, bst.CDIE_FUSEBREAK, bst.EFI_STAGE])

@pytest.mark.skip(reason="Currently, boot script stops at every stage regardless, so no reason to test individual stages.  If we move away from boot script in the future, this can help us time per-stage transitions.")
@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_soc_to_EFI(processor_turn_on_before_turn_off_after_test):
    boot_through_stages_with_verification([bst.SOC_FUSEBREAK, bst.EFI_STAGE])

@pytest.mark.skip(reason="Currently, boot script stops at every stage regardless, so no reason to test individual stages.  If we move away from boot script in the future, this can help us time per-stage transitions.")
@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_cdie_to_EFI(processor_turn_on_before_turn_off_after_test):
    boot_through_stages_with_verification([bst.CDIE_FUSEBREAK, bst.EFI_STAGE])

## Results using bootscript on MTL P682 C0 processor
# Stepping through all fusebreaks took: 412.2041313s
# Only stopping at SOC_FUSEBREAK took:  355.07189619999997
# Only stopping at CDIE_FUSEBREAK took: 343.9205366000001s         
# Stopping @ SOC, CDIE breaks:          355.4396438000001s