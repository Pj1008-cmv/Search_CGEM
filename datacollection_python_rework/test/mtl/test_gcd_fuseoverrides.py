import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger
import mtl.bootstagetransitions as bst
import mtl.gcd.fuse_overrides as gcd_fuseovs

generic_product.utilities.logger.setup_logging()

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_gcd_itd_disable(processor_turn_on_before_turn_off_after_test):
    bst.perform_transition(bst.SOC_FUSEBREAK)
    gcd_fuseovs.disable_gt_itd()
    bst.perform_transition(bst.EFI_STAGE)
    gcd_fuseovs.verify_gt_itd_disabled()

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_gcd_cep_disable(processor_turn_on_before_turn_off_after_test):
    bst.perform_transition(bst.SOC_FUSEBREAK)
    gcd_fuseovs.disable_gcd_cep()
    bst.perform_transition(bst.EFI_STAGE)
    gcd_fuseovs.verify_gcd_cep_disabled()

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_gcd_set_tjmax(processor_turn_on_before_turn_off_after_test):
    TJ_MAX = 120    
    bst.perform_transition(bst.SOC_FUSEBREAK)
    gcd_fuseovs.set_gcd_tj_max(TJ_MAX)
    bst.perform_transition(bst.EFI_STAGE)
    gcd_fuseovs.verify_gcd_tj_max(tj_max_expected=TJ_MAX)