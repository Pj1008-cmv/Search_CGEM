# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from mtl.sv import get_soc

def package_max(soc=None):
    """Read processor's package max DTS register."""
    if soc is None:
        soc = get_soc()
    return int(soc.north.pcudata.io_package_temperature)*1