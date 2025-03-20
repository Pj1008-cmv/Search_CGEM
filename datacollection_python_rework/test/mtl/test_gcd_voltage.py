import sys

import pytest

if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
# imports, local
import generic_product.utilities.logger as logger
import mtl.gcd.voltage as gcd_voltage
import generic_product.utilities.voltagetest as voltagetest

generic_product.utilities.logger.setup_logging()

@pytest.mark.requires_processor_and_nevo
def test_vccgt_voltage_read(processor_turn_on_before_test):
    assert gcd_voltage.read_vccgt_voltage() > 0

@pytest.mark.requires_processor_and_nevo
def test_vccgt_voltage_set_svid(processor_turn_on_before_turn_off_after_test):
    voltagetest.voltage_set_test(
        read_fn=gcd_voltage.read_vccgt_voltage,
        set_fn=gcd_voltage.set_vccgt_voltage_svid
    )

@pytest.mark.requires_processor_and_nevo
def test_vccgt_voltage_set_svid_withintolerance(processor_turn_on_before_turn_off_after_test):
    voltagetest.voltage_set_within_tolerance_test(
        read_fn=gcd_voltage.read_vccgt_voltage,
        set_within_tol_fn=gcd_voltage.set_vccgt_voltage_svid_withintolerance,
        allowed_tolerance=gcd_voltage.SET_READ_LOOP_TOLERANCE_V
    )
