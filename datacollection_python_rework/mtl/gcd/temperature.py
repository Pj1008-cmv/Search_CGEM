# imports, std library
import sys
import namednodes as _namednodes
_namednodes.sv.refresh()
cdie = _namednodes.sv.socket0.compute0
gcd  = _namednodes.sv.socket0.gcd
soc  = _namednodes.sv.socket0.soc

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

def Max_DTS_Profile():
    return int(soc.north.pcudata.io_package_temperature)*1