"""Generic voltage set test functions -- reduces copy-pasting."""

def voltage_set_test(read_fn, set_fn, voltage_offset_V=0.020):
    """Read before, set higher, check if voltage went up."""
    before_read_V = read_fn()
    set_fn(before_read_V + voltage_offset_V)
    after_read_V = read_fn()
    assert after_read_V > before_read_V

def voltage_set_within_tolerance_test(read_fn, set_within_tol_fn, allowed_tolerance):
    read_V = read_fn()
    set_within_tol_fn(new_setpoint:=(read_V + 0.020))
    assert read_fn() - new_setpoint < allowed_tolerance
