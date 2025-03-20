# imports, std lib
import sys

# cell status import?
if(cellstatuspath:=r'I:\cmv\or\mtl\Scripts\cell_status') not in sys.path:
    sys.path.append(cellstatuspath)

# local imports
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

# run cell_status?