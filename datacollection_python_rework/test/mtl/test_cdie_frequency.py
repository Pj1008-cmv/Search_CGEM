import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger    
import mtl.processorinfo
import mtl.bootstagetransitions as bst
import mtl.cdie.frequency as cdie_frequency

generic_product.utilities.logger.setup_logging()

### Ring

@pytest.mark.requires_processor
def test_ring_ratio_read(processor_turn_on_before_test):
    assert cdie_frequency.read_ring_ratio() > 0

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_ring_ratio_set(processor_turn_on_before_turn_off_after_test):
    current_ratio = cdie_frequency.read_ring_ratio()
    bst.perform_transition(to_stage=bst.SOC_FUSEBREAK)
    cdie_frequency.set_ring_ratio(new_setpoint:=(current_ratio + 5))
    bst.perform_transition(to_stage=bst.EFI_STAGE)
    assert cdie_frequency.read_ring_ratio == new_setpoint

###### QUESTION: if a core is slice disabled is ratio read based on physical or logical number

### Big Core

@pytest.mark.requires_processor
def test_bigcore_ratio_read(processor_turn_on_before_test):
    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()
    for physical_bigcore in processorinfo.bigcore_physical_logical_core_mapping.keys():
        assert cdie_frequency.read_bigcore_ratio(physical_bigcore) > 0

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_bigcore_ratio_set(processor_turn_on_before_turn_off_after_test):
    # only check for one core
    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()
    lowest_active_physical_bigcore = min(processorinfo.bigcore_physical_logical_core_mapping.keys())
    
    current_ratio = cdie_frequency.read_bigcore_ratio(lowest_active_physical_bigcore)
    bst.perform_transition(to_stage=bst.SOC_FUSEBREAK)
    cdie_frequency.set_bigcore_ratio(new_setpoint:=(current_ratio + 5))
    bst.perform_transition(to_stage=bst.EFI_STAGE)
    assert cdie_frequency.read_bigcore_ratio == new_setpoint

### Atom Module

@pytest.mark.requires_processor
def test_atommod_ratio_read(processor_turn_on_before_test):
    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()
    for physical_atommod in processorinfo.atommod_physical_logical_core_mapping.keys():
        assert cdie_frequency.read_atommod_ratio(physical_atommod) > 0

@pytest.mark.fuse_override
@pytest.mark.requires_processor
def test_atommod_ratio_set(processor_turn_on_before_turn_off_after_test):
    # only check for one core
    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()
    lowest_active_physical_atommod = min(processorinfo.atommod_physical_logical_core_mapping.keys())
    
    current_ratio = cdie_frequency.read_atommod_ratio(lowest_active_physical_atommod)
    bst.perform_transition(to_stage=bst.SOC_FUSEBREAK)
    cdie_frequency.set_atommod_ratio(new_setpoint:=(current_ratio + 5))
    bst.perform_transition(to_stage=bst.EFI_STAGE)
    assert cdie_frequency.read_atommod_ratio == new_setpoint