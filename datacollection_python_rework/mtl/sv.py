# imports, std library
from operator import index
import sys

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
from generic_product.sv_ipc_wrapper import PySVOpenIPCWrapper
import generic_product.utilities.logger as logger
import mtl.bootstagetransitions as bootstagetransitions

### functions to obtain fresh reference to pythonsv dielet object with optional boot stage checking

def get_cdie(ensure_at_cdie_fusebreak: bool=False, ensure_booted: bool=False):
    """Obtain fresh reference to `sv.cdie`.  Optionally verify processor is at desired boot stage beforehand."""
    if ensure_at_cdie_fusebreak: bootstagetransitions.ensure_at_cdie_fusebreak()
    elif ensure_booted:          bootstagetransitions.ensure_at_content_stage()
    sv_ipc_wrapper = PySVOpenIPCWrapper()
    return sv_ipc_wrapper.sv.socket0.compute0

def get_gcd(ensure_at_gcd_fusebreak: bool=False, ensure_booted: bool=False):
    """Obtain fresh reference to `sv.gcd`.  Optionally verify processor is at desired boot stage beforehand."""
    if ensure_at_gcd_fusebreak: bootstagetransitions.ensure_at_gcd_fusebreak()
    elif ensure_booted:         bootstagetransitions.ensure_at_content_stage()
    sv_ipc_wrapper = PySVOpenIPCWrapper()
    return sv_ipc_wrapper.sv.socket0.gcd

def get_soc(ensure_at_soc_fusebreak: bool=False, ensure_booted: bool=False):
    """Obtain fresh reference to `sv.soc`.  Optionally verify processor is at desired boot stage beforehand."""
    if ensure_at_soc_fusebreak: bootstagetransitions.ensure_at_soc_fusebreak()
    elif ensure_booted:         bootstagetransitions.ensure_at_content_stage()
    sv_ipc_wrapper = PySVOpenIPCWrapper()
    return sv_ipc_wrapper.sv.socket0.soc

def get_ioe(ensure_at_ioe_fusebreak: bool=False, ensure_booted: bool=False):
    """Obtain fresh reference to `sv.ioe`.  Optionally verify processor is at desired boot stage beforehand."""
    if ensure_at_ioe_fusebreak: bootstagetransitions.ensure_at_ioe_fusebreak()
    elif ensure_booted:         bootstagetransitions.ensure_at_content_stage()
    sv_ipc_wrapper = PySVOpenIPCWrapper()
    return sv_ipc_wrapper.sv.socket0.ioe

### Fuse set / readback

def extract_fuse_str_name(fuse_set_str: str) -> str:
    # remove spaces
    modified = fuse_set_str.replace(' ', '')
    # ensure no in-place operators
    for inplaceoperator in ['+', '-', '*', '/', '%']:
        modified = modified.replace(inplaceoperator, '')
    # extract the fuse name
    return modified.split('=')[0]

def set_fuse(fuse_set_str: str):
    """Set desired fuse and value, log into `fuse_set_record dictionary` for later verification!"""
    # obtain references to pythonsv dielet objects (silence stdout)
    dielet = fuse_set_str.split('.')[0]
    if dielet == 'soc':
        soc = get_soc()
    elif dielet == 'cdie':
        cdie = get_cdie()
    elif dielet == 'gcd':
        gcd = get_gcd()
    elif dielet == 'ioe':
        ioe = get_ioe()
    # read fuse value prior to set
    fuse_name = extract_fuse_str_name(fuse_set_str)
    value_before = eval(fuse_name)
    # set!
    logger.info(f'Setting {fuse_set_str}')
    exec(fuse_set_str)
    # log that this fuse was set - need to first make sure that we "expand" in-place arithmetic
    fuse_set_str = fuse_set_str.replace(' ', '')
    for operator in ['+=', '-=', '*=', '/=', '%=']:
        if operator not in fuse_set_str:
            continue
        # ex:
        #   1. initial `fuse_set_str`:   "cdie.fuses.dmu_fuse.fw_fuses_ring_vf_voltage_0 += 16"
        #   2. extract `fuse_name`:      "cdie.fuses.dmu_fuse.fw_fuses_ring_vf_voltage_0"
        #   3. log `value_before`:       eval("cdie.fuses.dmu_fuse.fw_fuses_ring_vf_voltage_0")  # ex: = 200
        #   4. calculate expected value: eval("value_before + 16")
        expected_value = eval(fuse_set_str.replace(f'{fuse_name}{operator}=', 'value_before {operator} '))
        break
    # if none of the operators match, we'll enter the else clause
    else:
        # "fuse = value" -> ["fuse", "0"]
        set_val_str = fuse_set_str.split('=')[1]
        expected_value = int(set_val_str, base=16 if 'x' in set_val_str.lower() else 10)
    # log the fuse / set value pair!  `expected_value` should be logged as an integer, since that's what fuse readback returns.
    bootstagetransitions.fuse_set_record[fuse_name] = expected_value

def arbitrary_fuse_loop(fuse_string, index_placeholder='<INDEX>', start_index=0):
    """Sets given fuse string from `start_index` until we get an error/exception (saves us from hard-coding end value)."""
    idx = start_index
    while(True):
        try:
            arbitrary_string = fuse_string.replace(index_placeholder, str(idx))
            set_fuse(arbitrary_string)
            idx += 1
        except AttributeError as e:
            logger.warning(f"Received invalid start_index: {idx}\n{e}")
            break
        except Exception as e:
            if str(e) == 'cannot add new attributes at this point':
                logger.info('No more fuses to set.')
                break
            else:
                logger.error(f"Unknown error: {e}")
                raise

def fuse_loop(fuse_string, num_loops, index_placeholder='<INDEX>', start_index=0):
    """Sets given fuse string from `start_index` onwards, for `num_loop` iterations / consecutive integer values."""
    for idx in range(start_index, num_loops):
        set_fuse(fuse_string.replace(index_placeholder, str(idx)))

def ensure_all_fuse_settings_valid():
    """Ensures that all fuse read values match set values!  If not, raises `AssertionError`"""
    bootstagetransitions.ensure_at_content_stage()
    # obtain references to pythonsv dielet objects
    soc = get_soc()
    cdie = get_cdie()
    gcd = get_gcd()
    # ioe = get_ioe()
    # verify fuses
    if bootstagetransitions.fuse_set_record:
        logger.info('Verifying all fuses set during fuse overrides!')
    for fuse, set_val in bootstagetransitions.fuse_set_record.items():
        read_val = int(eval(fuse))
        if read_val != set_val:
            logger.error(msg:=f'    Fuse set/read mismatch. set={set_val}, readback={read_val} ({fuse})')
            raise AssertionError(msg)
        logger.info(f'    GOOD (readback matches set value)! {fuse}')