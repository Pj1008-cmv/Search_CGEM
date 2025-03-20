import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger
import generic_product.sv_ipc_wrapper
import mtl.targetpowercontrol
import mtl.processorinfo

generic_product.utilities.logger.setup_logging()

@pytest.mark.requires_processor
def test_processor_info(processor_turn_on_before_test):
    p = mtl.processorinfo.MeteorlakeProcessorInfo()
    
    # values from fusing
    assert p.visualid is not None
    assert p.qdf is not None
    assert p.bigcore_physical_logical_core_mapping is not None
    assert p.atom_physical_logical_core_mapping is not None
    
    # values derived from visual id (looked up)
    assert p.pds is not None
    assert p.projectdir is not None
    assert p.classdata is not None