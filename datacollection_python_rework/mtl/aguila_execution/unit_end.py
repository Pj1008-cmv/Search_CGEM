# imports, std lib
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import mtl.processorinfo
import mtl.bootstagetransitions

# ensure processorinfo singleton's unit-specific info is all cleared
processorinfo_singleton = mtl.processorinfo.MeteorlakeProcessorInfo()
processorinfo_singleton.clear_unit_values()

# turn the processor off
mtl.bootstagetransitions.perform_transition(to_stage=mtl.bootstagetransitions.POWER_OFF_STAGE)