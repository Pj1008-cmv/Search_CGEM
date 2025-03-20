# imports, std library
import re
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\datacollection_python_new') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
import mtl.cdie.frequency as cdie_frequency
import mtl.cdie.fuse_overrides as cdie_fuseovs
import mtl.cdie.voltage as cdie_voltage
import mtl.processorinfo
import mtl.soc.fuse_overrides as soc_fuseovs
import mtl.sv
from mtl import bootstagetransitions

def parse_active_compute_elements(elementstr, prefix):
    """Returns tuple: `(active_elements, class_lookup_element)`
    
    - `active_elements`: collection (list) of integer active element physical indices.
            Ex: C0123 = turn on cores 0-3, `active_elements` = `[0, 1, 2, 3]`
    - `class_lookup_element`: int, physical index of class lookup compute element (relevant for parellel search).
            Ex: C0123 = turn on cores 0-3, `class_lookup_element` = `0`
    """
    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()  # this assumes that SVIPC and ProcInfo singletons have already been created.

    match = re.search(rf'{prefix}\d*', elementstr)
    if match is None:
        return None, None
    else:
        active = match.group()
    # naming convention shorthand: standalone "C" or "A" indicates all cores/modules active
    if active == prefix:
        active = list(processorinfo.valid_cores['bigcore' if prefix == 'C' else 'atommod'])
    # otherwise, we have a list of active cores/modules!
    else:
        active = [int(i) for i in active[1:]] # remove the 'C' or 'A' prefix
    class_lookup = str(min(active))
    return active, class_lookup

def execute_fuse_recipe(testtype: str, fcorner: str, elements='N/A'):
    '''Cdie fuse recipe - supports big core, atom module, and ring.
    
    Note that `elements` can take arguments in two forms:
    
    - Integer, representing physical element number.  This is useful for singlecore testing.
            Ex: Big Core 0, Atom module 1, etc.

    - String, encoding which core(s) and atom module(s) are active.  Defined in mtl.cdie.fuse_overrides.CORE_MASK.  Useful for parallel search.
            Ex: 'A' -> 0xFF00  # enable all atom modules
    '''
    logger.info(f'Called with args (testtype, fcorner, elements) = ({testtype}, {fcorner}, {elements})')

    ring_flow = 'ring' in testtype.lower()
    bigcore_flow = 'avx' in testtype.lower()
    atommod_flow = 'atom' in testtype.lower()
    # assuming there's no flow that has both 'A###' and 'C###' in the str.

    # performing argument parsing (to match w block comment description)
    core_mask_elements = None
    if type(elements) == int or elements.isnumeric():
        elements = f"{'A' if atommod_flow else 'C'}{elements}"
    if bigcore_flow:
        active_bigcores, class_lookup_element = parse_active_compute_elements(elements, prefix='C')
        active_atommods = []
        core_mask_elements = elements
    elif atommod_flow:
        active_atommods, class_lookup_element = parse_active_compute_elements(elements, prefix='A')
        active_bigcores = []
        core_mask_elements = elements

    processorinfo = mtl.processorinfo.MeteorlakeProcessorInfo()  # this assumes that SVIPC and ProcInfo singletons have already been created.
    set_ratio = cdie_frequency.freq_to_ratio(processorinfo.classdata[(testtype, fcorner, class_lookup_element)]['Frequency'])

    # set GCD, SOC fuses
    bootstagetransitions.perform_transition(to_stage=bootstagetransitions.SOC_FUSEBREAK)
    soc_fuseovs.disable_soc_atom()
    cdie_fuseovs.zero_out_cdie_deltas_in_soc()

    # set Cdie fuses
    bootstagetransitions.perform_transition(to_stage=bootstagetransitions.CDIE_FUSEBREAK)
    # general fuses
    if core_mask_elements is not None:
        cdie_fuseovs.set_cdie_core_mask(core_mask_elements)  # only set for bigcore/atom, not ring
    cdie_fuseovs.disable_c_state()
    cdie_fuseovs.zero_cdie_itd_fuses()
    cdie_fuseovs.zero_out_p0_big_core_delta()
    cdie_fuseovs.zero_out_p0_atom_delta()
    cdie_fuseovs.zero_out_p0_avx_delta()
    cdie_fuseovs.zero_out_avx_VF_deltas()
    cdie_fuseovs.zero_out_vf_deltas_all_cores()
    cdie_fuseovs.zero_out_p0_downbins()
    # domain-specific fuses
    if bigcore_flow:
        cdie_voltage.flatten_bigcore_vf(1.3)
        cdie_voltage.flatten_ring_vf(1.2)
        cdie_frequency.set_core_ratio_p0_fuse(set_ratio)
    elif atommod_flow:
        cdie_frequency.set_atom_ratio_fuse(set_ratio)
    elif ring_flow:
        cdie_frequency.set_ring_ratio_fuse(set_ratio)
        cdie_frequency.set_core_ratio_fuse(8)

    # boot to EFI, verify all set fuses (happens after transition to EFI)
    bootstagetransitions.perform_transition(to_stage=bootstagetransitions.EFI_STAGE)

    # verify necessary registers (separate from fuses)
    if ring_flow:
        assert set_ratio == cdie_frequency.read_ring_ratio()
    else:
        assert cdie_frequency.all_core_ratios_valid(active_bigcores, active_atommods, set_ratio)