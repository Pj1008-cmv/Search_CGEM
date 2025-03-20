import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger
import mtl.bootstagetransitions as bst
import mtl.soc.fuse_overrides as soc_fuseovs

generic_product.utilities.logger.setup_logging()

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_soc_set_tjmax(processor_turn_on_before_turn_off_after_test):
    TJ_MAX = 120    
    bst.perform_transition(bst.SOC_FUSEBREAK)
    soc_fuseovs.set_soc_tj_max(TJ_MAX)
    bst.perform_transition(bst.EFI_STAGE)
    soc_fuseovs.verify_soc_tj_max(tj_max_expected=TJ_MAX)