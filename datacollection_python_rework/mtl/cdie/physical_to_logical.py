# imports, std library
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

def create_physical_logical_map(slice_disable_mask_hex,
                                NUM_ATOM_MODULES=2,
                                NUM_BIG_CORES = 6):
    """Based on slice disable mask and information about number of cores/atom modules on product,
    create mapping between physical and logical cores.

    ```
    (annotated) cdie.fuses.dmu_fuse.fw_fuses_llc_slice_ia_core_dis.description text:

    Fusedown of a physical IA core, or Atom module, and its co-located LLC CBO.
    Not all options are available. Probably only disable pairs is supported.
    
    'xxxxxxxxx1' - disable core 0, and its co-located LLC CBO      # Atom module 0
    'xxxxxxxx1x' - disable core 1, and its co-located LLC CBO      # Atom module 1
    'xxxxxxx1xx' - disable core 2, and its co-located LLC CBO      # RWC 0  \\
    'xxxxxx1xxx' - disable core 3, and its co-located LLC CBO      # RWC 1  /sliced off together
    'xxxxx1xxxx' - disable core 4, and its co-located LLC CBO      # RWC 2  \\
    'xxxx1xxxxx' - disable core 5, and its co-located LLC CBO      # RWC 3  /sliced off together
    'xxx1xxxxxx' - disable core 6, and its co-located LLC CBO      # RWC 4  \\
    'xx1xxxxxxx' - disable core 7, and its co-located LLC CBO      # RWC 5  /sliced off together
    'x1xxxxxxxx' - disable core 8, and its co-located LLC CBO
    '1xxxxxxxxx' - disable core 9, and its co-located LLC CBO
    ```
    """

    physical = [f'a{i}' if i < NUM_ATOM_MODULES else f'c{i-NUM_ATOM_MODULES}'
                for i in reversed(range(NUM_ATOM_MODULES + NUM_BIG_CORES))]
    
    slice_disable_mask_binary = f'{slice_disable_mask_hex:0{NUM_ATOM_MODULES + NUM_BIG_CORES}b}'
    
    slice_enabled = [compute_element 
                        for compute_element, slice_disable in zip(physical, slice_disable_mask_binary) 
                        if slice_disable == '0']
 
    bigcore_enabled = [element for element in slice_enabled if 'c' in element]
    atommod_enabled = [element for element in slice_enabled if 'a' in element]

    bigcore_physical_to_logical = {int(core[1:]): len(bigcore_enabled) - i - 1
                                    for i, core in enumerate(bigcore_enabled)}
    
    atom_physical_to_logical = {int(core[1:]) : len(atommod_enabled) - i - 1
                                for i, core in enumerate(atommod_enabled)}

    logger.info(f'Computed big core physical to logical map: {bigcore_physical_to_logical}')
    logger.info(f'Computed atom mod physical to logical map: {atom_physical_to_logical}')

    return bigcore_physical_to_logical, atom_physical_to_logical


# Testing
if __name__ == '__main__':

    # Testing big core no-disable logic
    assert(create_physical_logical_map(0x00) == ({5: 5,  4: 4,  3: 3,  2: 2, 1: 1,  0: 0}, {1: 1, 0: 0}))

    ## Testing big core logic (and atom no-disable logic)
    # 2-core disable, no atom slice dis
    assert(create_physical_logical_map(0x0C) == ({5: 3,  4: 2,  3: 1,  2: 0              }, {1: 1, 0: 0}))
    assert(create_physical_logical_map(0x30) == ({5: 3,  4: 2,                1: 1,  0: 0}, {1: 1, 0: 0}))
    assert(create_physical_logical_map(0xC0) == ({              3: 3,  2: 2,  1: 1,  0: 0}, {1: 1, 0: 0}))
    # 4-core disable, no atom slice dis
    assert(create_physical_logical_map(0xF0) == ({                            1: 1,  0: 0}, {1: 1, 0: 0}))
    assert(create_physical_logical_map(0xCC) == ({              3: 1,  2: 0              }, {1: 1, 0: 0}))
    assert(create_physical_logical_map(0x3C) == ({5: 1,  4: 0                            }, {1: 1, 0: 0}))

    ## Testing atom mod logic
    assert(create_physical_logical_map(0x01)[1] == {1: 0})  # mod 0 disabled
    assert(create_physical_logical_map(0x02)[1] == {0: 0})  # mod 1 disabled
    assert(create_physical_logical_map(0x03)[1] == {    })  # mods 0, 1 disabled 