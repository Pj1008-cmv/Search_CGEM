# imports, std lib
import sys

# local imports
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.targetpowercontrol as targetpowercontrol

targetpowercontrol.DUT_POWERSPLITTER_PORT_NUM = 0
targetpowercontrol.PYSV_PRODUCT = 'meteorlake'

# alias generic arguments after setting the portnums
target_power_on_control  = targetpowercontrol.target_power_on_control
target_power_off_control = targetpowercontrol.target_power_off_control
is_target_power_on       = targetpowercontrol.is_target_power_on
is_target_power_off      = targetpowercontrol.is_target_power_off
