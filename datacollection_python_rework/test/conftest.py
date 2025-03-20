import logging
import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)

import generic_product.utilities.logger as logger
import mtl.bootstagetransitions as bst

generic_product.utilities.logger.setup_logging()

logger = logging.getLogger('automation.test.conftest')

def ensure_processor_at_efi():
    if bst.current_stage != bst.EFI_STAGE:
        if bst.current_stage != bst.POWER_OFF_STAGE:
            logger.critical('... turning processor off')
            bst.perform_transition(to_stage=bst.POWER_OFF_STAGE)
        logger.critical('... transitioning processor to EFI stage (turning back on)')
        logger.error('... transitioning processor to EFI stage (turning back on)')
        logger.warning('... transitioning processor to EFI stage (turning back on)')
        logger.info('... transitioning processor to EFI stage (turning back on)')
        logger.debug('... transitioning processor to EFI stage (turning back on)')
        bst.perform_transition(to_stage=bst.EFI_STAGE)

@pytest.fixture
def processor_turn_on_before_turn_off_after_test(caplog):
    caplog.set_level(logging.DEBUG, logger='automation')
    # before running the test, ensure the unit is powered on
    ensure_processor_at_efi()
    # allow the test to run
    yield
    # turn the processor off
    logger.critical('... transitioning processor to poweroff stage (turning off)')
    bst.perform_transition(to_stage=bst.POWER_OFF_STAGE)

@pytest.fixture
def processor_turn_on_before_test(caplog):
    caplog.set_level(logging.DEBUG, logger='automation')
    # before running the test, ensure the unit is powered on
    ensure_processor_at_efi()
    # run the test; it's ok if the test doesn't turn processor off afterwards
    return