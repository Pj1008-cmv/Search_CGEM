import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger
import mtl.cdie.voltage as cdie_voltage
import generic_product.utilities.voltagetest as voltagetest

generic_product.utilities.logger.setup_logging()

### Ring

@pytest.mark.requires_processor_and_nevo
def test_ring_voltage_read(processor_turn_on_before_test):
    assert cdie_voltage.read_ring_voltage() > 0

@pytest.mark.requires_processor_and_nevo
def test_ring_voltage_set_dlvr(processor_turn_on_before_turn_off_after_test):
    voltagetest.voltage_set_test(
        read_fn=cdie_voltage.read_ring_voltage,
        set_fn=cdie_voltage.set_ring_voltage_dlvr
    )

@pytest.mark.requires_processor_and_nevo
def test_ring_voltage_set_dlvr_withintolerance(processor_turn_on_before_turn_off_after_test):
    voltagetest.voltage_set_within_tolerance_test(
        read_fn=cdie_voltage.read_ring_voltage,
        set_within_tol_fn=cdie_voltage.set_ring_voltage_dlvr_withintolerance,
        allowed_tolerance=cdie_voltage.SET_READ_LOOP_TOLERANCE_V
    )

### Bigcore

### Atom