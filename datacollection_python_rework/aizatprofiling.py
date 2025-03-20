import json, sys
##if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
##    sys.path.append(toplevel)
##if (oldlevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python') not in sys.path:
##   sys.path.append(oldlevel)

if (toplevel:=r'C:\SVSHARE\cmv_client_automation_mtl\python\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
if (toplevel:=r'C:\SVSHARE\cmv_client_automation_mtl\python') not in sys.path:
    sys.path.append(toplevel)
if (toplevel:=r'C:\SVSHARE\cmv_client_automation_mtl\python\DTS') not in sys.path:
    sys.path.append(toplevel)


import generic_product.utilities.logger as logger

import namednodes as _namednodes
_namednodes.sv.refresh()
cdie = _namednodes.sv.socket0.compute0
gcd  = _namednodes.sv.socket0.gcd
soc  = _namednodes.sv.socket0.soc

##import mtl_voltage_monitor
##import generic_product.mtl_voltage_control
import Intec_POC as Intec_POC
import voltage_control as voltage_control
import Dts_dump as Dts_dump
import ratio_control as ratio_control

######### Thermals #########
def Max_DTS_Profile():
    return int(soc.north.pcudata.io_package_temperature)*1

def Core_DTS_Profile():
    return Dts_dump.main()

def Atom_DTS_Profile():
    pass

def Ring_DTS_Profile():
    pass

def SA_DTS_Profile():
    pass

def Intec_TC_Profile():
    return Intec_POC.ProfileTCaseTemperature()

def Intec_SP_Profile():
    return Intec_POC.ProfileSetPointTemperature()

def Intec_FB_Profile():
    return Intec_POC.ProfileFeedbackTemperature()

######### Ratio #########
def Ring_Ratio_Profile():
    return int(cdie.dmudata.io_wp_cv_ring.ratio)*1

def Core_Ratio_Profile():
    return int(ratio_control.read_core_ratio())*1

######### Voltage #########
def VCC_RING():
    #return mtl_voltage_monitor.getVoltageAverage("VL_LLC", numSamples=10)
    return int(voltage_control.measure_ccf_voltage())*1

def VCC_CORE0():
    return int(voltage_control.measure_dlvr0_voltage())*1