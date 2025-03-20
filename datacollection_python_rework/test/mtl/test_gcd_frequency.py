import sys
import logging

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger
import mtl.bootstagetransitions as bst
import mtl.gcd.frequency as gcd_frequency

generic_product.utilities.logger.setup_logging()
logger = logging.getLogger('automation.test.mtl.test_gcd_frequency')

@pytest.mark.requires_processor
def test_gt_ratio_read(processor_turn_on_before_turn_off_after_test):
    gt_ratio = gcd_frequency.read_gt_ratio()
    logger.critical(f'Read GT ratio: {gt_ratio}')
    assert gt_ratio > 0

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_gt_ratio_set(processor_turn_on_before_turn_off_after_test):
    current_ratio = gcd_frequency.read_gt_ratio()
    logger.critical(f'Current GT ratio: {current_ratio}')
    bst.perform_transition(to_stage=bst.SOC_FUSEBREAK)

    gcd_frequency.set_gt_ratio(new_setpoint:=(current_ratio + 5))
    logger.critical(f'New GT ratio setpoint: {new_setpoint}')
    bst.perform_transition(to_stage=bst.EFI_STAGE)
    assert gcd_frequency.read_gt_ratio() == new_setpoint