import logging

import pytest

def pytest_runtest_setup(item):
    error_msg = 'You must specify the `-m "<marker>"` command line flag when running tests in this repository.'
    try:
        dash_m_flag_value = item.config.getoption('-m')
    except ValueError:
        logging.error(error_msg)
        pytest.skip("Skipping as the test has a marker")
    if not dash_m_flag_value:
        logging.error(error_msg)
        pytest.skip("Skipping as the test has a marker")