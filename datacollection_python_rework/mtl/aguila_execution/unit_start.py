# imports, std lib
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

import generic_product.hardware.ttk3 as ttk3
import generic_product.sv_ipc_wrapper as sv_ipc_wrapper
import mtl.targetpowercontrol as targetpowercontrol
import mtl.processorinfo

# ensure unit is turned on
if targetpowercontrol.is_target_power_off():
    targetpowercontrol.target_power_on_control(wait_for_POST=True)

# perform pythonsv enumeration
sv_ipc_wrapper_singleton = sv_ipc_wrapper.PySVOpenIPCWrapper()
sv_ipc_wrapper_singleton.get_all()
assert sv_ipc_wrapper_singleton.need_refresh is False
assert sv_ipc_wrapper_singleton.ipc.isunlocked()

# create processorinfo singleton and have it read processor info
processorinfo_singleton = mtl.processorinfo.MeteorlakeProcessorInfo()