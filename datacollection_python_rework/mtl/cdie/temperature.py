# imports, std library
import json, sys
path_file = r"C:\sthi\Fusion\meteorlake.s.681.cdie-gcd-socnorth\python\path_list.json"
with open(path_file, 'r') as file_obj:
    json_dict = json.load(file_obj)
for path in json_dict["path_list"]:
    if path not in sys.path:
        sys.path.append(path)
        
import mtl_voltage_monitor
import namednodes as _namednodes
_namednodes.sv.refresh()
cdie = _namednodes.sv.socket0.compute0
gcd  = _namednodes.sv.socket0.gcd
soc  = _namednodes.sv.socket0.soc

nevoRailNames = {"core0":"VL_CORE0",
    "core1":"VL_CORE1",
    "core2":"VL_CORE2",
    "core3":"VL_CORE3",
    "core4":"VL_CORE4",
    "core5":"VL_CORE5",
    "atom0":"VL_ATOM0",
    "atom1":"VL_ATOM1",
    "ring":"VL_LLC",
    "RING":"VL_LLC",        # NOTE that RING repeat here since DLVR uses lower case and VCC_RING is upper case. This is the most elegant fix.
    "GT":"VCCGT",
    "SA":"VCCSA",
    "VNNAON":"VNNAON",
    "VCCIA":"VCCCORE_S"
}

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

def Max_DTS_Profile():
    return int(soc.north.pcudata.io_package_temperature)*1

def Ring_Ratio_Profile():
    return int(cdie.dmudata.io_wp_cv_ring.ratio)*1

def VCC_RING():
    return mtl_voltage_monitor.getVoltageProfiling([nevoRailNames["ring"]])[0]