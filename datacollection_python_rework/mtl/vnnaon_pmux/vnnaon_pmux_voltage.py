"""Meteorlake system-agent dielet voltage set and read-back."""

# imports, std library
import functools
import sys

# imports, pythonsv
paths = [
    r'C:\pythonsv\meteorlake',
    r'applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp'
]
for path in paths:
    if path not in sys.path:
        sys.path.append(path)
# # meteorlake pythonsv imports

# imports, local
import mtl.cdie.voltage
import generic_product.utilities.logger as logger as logger
import generic_product.hardware.nevo as nevo

# global variable declarations
VREAD       = "voltage_read"
VSET        = "voltage_set"
GATE        = "gate_override"
ENABLE      = "enable"
SELECT      = "select"

### READ
def read_vnnaon_voltage() -> str:
    """Reads VCCSA voltage."""
    return nevo.read_value('VNNAON')

### switch pmux
# TODO: understand Craig's code and implement here.

def generic_set_sram_mux_state(
    pmux_state, 
    voltage_read,
    voltage_set,
    gate_override,
    enable,
    select):
    
    '''
    Toggles a given domain SRAM voltage supply to either 
    
    VNNAON (enable=True)
    or
    Domain DLVR/SVID supply (enable=False)

    Arguments:
        domain
            IP to switch SRAM mux for
            possible inputs:
            cdie_ring
            cdie_atom0
            cdie_atom1
            soc
        enable
            enables given SRAM MUX(es)
            True:   MUX is toggled to VNNAON voltage rail
            False:  MUX is toggled to DLVR/SVID voltage rail
    
    Returns:
        None
    '''
    pass
    global ENABLE
    global SELECT
    global VSET

    sram_domains = {
        "atom0": {
            "voltage_read":     "read_atommod_voltage(0)",
            "voltage_set":      "set_dvlr_voltage(domain='atom0', set_V=vnnaon_v, powerstate=0)",
            "gate_override":    "cdie.atom0.pma_pmsb.pma_cr_clk_gate_override.surv_obs_clk_gate_ovrd",
            "enable":           ["cdie.atom0.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en"], 
            "select":           ["cdie.atom0.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel"]
            },
        "atom1": {
            "voltage_read":     "read_atommod_voltage(1)",
            "voltage_set":      "set_dvlr_voltage(domain='atom1', set_V=vnnaon_v, powerstate=0)",
            "gate_override":    "cdie.atom1.pma_pmsb.pma_cr_clk_gate_override.surv_obs_clk_gate_ovrd",
            "enable":           ["cdie.atom1.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en"], 
            "select":           ["cdie.atom1.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel"]
            },
        # Ring
        "ccf": {
            "voltage_read":     "read_ring_voltage()",
            "voltage_set":      "set_dvlr_voltage(domain='ring', set_V=vnnaon_v, powerstate=0)",
            "enable":           ["cdie.taps.soc_cbpma0_ccf_pma_inst_pma.pma_overrides.pma_llc_pwr_mux_sel_ovrd_en"], 
            "select":           ["cdie.taps.soc_cbpma0_ccf_pma_inst_pma.pma_overrides.pma_llc_pwr_mux_sel_ovrd_val"]
            },
        # All IPU domains - Atom, IPU, VPU, Media, Display
        "soc": {
            "voltage_read":     "VCCSA",
            "voltage_set":      "VCC_SA",
            "gate_override":    "soc.north.pmsb.clr_pmsb_top.ccf_pmc_regs.ccf_pmc_regs_clkgate_ovrd",
            "enable":           ["soc.north.atom.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.media_pwrmux_ovrd_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.display_pwrmux_ovrd_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.ipu_pwrmux_ovrd_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.vpu_pwrmux_ovrd_en"], 
            "select":           ["soc.north.atom.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.media_pwrmux_ovrd_val", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.display_pwrmux_ovrd_val", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.ipu_pwrmux_ovrd_val", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.vpu_pwrmux_ovrd_val"]
            }
    }
        
    # TODO: Check domain WP register to check if safe to toggle PMUX

    # TODO: Create generic PMUX set function with parameters set by domain specific functions
    
    # TODO: build correct voltage read method
    
    # Set IP voltage to VNNAON
    set_ip_voltage(
        read_domain_voltage=voltage_read,
        set_domain_voltage=voltage_set)
    
    Enable clock gate
    eval(gate_override=1)

    # Enable bit can only be set if select bit set
    for ip in range(len(select))
        eval(select=1)
        eval(enable=pmux_state)

def atom_pmux_set(mux_state, mod_num):
    generic_set_sram_mux_state(
        pmux_state      = mux_state, 
        voltage_read    = functools.partial(mtl.cdie.voltage.read_atommod_voltage, modulenum_physical=mod_num),
        voltage_set     = functools.partial(mtl.cdie.voltage.set_atommod_voltage_dlvr_withintolerance, modulenum=mod_num),
        gate_override   = f"cdie.atom{mod_num}.pma_pmsb.pma_cr_clk_gate_override.surv_obs_clk_gate_ovrd",
        enable          = [f"cdie.atom{mod_num}.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en"],
        select          = [f"cdie.atom{mod_num}.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel"]
    )

def ring_pmux_set(mux_state):
    generic_set_sram_mux_state(
        pmux_state      = mux_state, 
        voltage_read    = mtl.cdie.voltage.read_ring_voltage,
        voltage_set     = mtl.cdie.voltage.set_ring_voltage_dlvr_withintolerance,
        gate_override   = "cdie.pmsb.clr_pmsb_top.ccf_pmc_regs.ccf_pmc_regs_clkgate_ovrd",
        enable          = ["cdie.taps.soc_cbpma0_ccf_pma_inst_pma.pma_overrides.pma_llc_pwr_mux_sel_ovrd_en"],
        select          = ["cdie.taps.soc_cbpma0_ccf_pma_inst_pma.pma_overrides.pma_llc_pwr_mux_sel_ovrd_val"]
    )

def soc_pmux_set(mux_state):
    generic_set_sram_mux_state(
        pmux_state      = mux_state, 
        voltage_read    = mtl.voltage.read_vccsa_voltage,
        voltage_set     = mtl.soc.voltage.set_vccsa_voltage_svid_withintolerance,
        gate_override   = "soc.north.pmsb.clr_pmsb_top.ccf_pmc_regs.ccf_pmc_regs_clkgate_ovrd",
        enable          = ["soc.north.atom.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.media_pwrmux_ovrd_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.display_pwrmux_ovrd_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.ipu_pwrmux_ovrd_en", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.vpu_pwrmux_ovrd_en"],
        select          = ["soc.north.atom.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.media_pwrmux_ovrd_val", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.display_pwrmux_ovrd_val", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.ipu_pwrmux_ovrd_val", "soc.north.pcudata.io_surv_dual_rail_pmux_sel_control.vpu_pwrmux_ovrd_val"]
    )

def set_domain_voltage(
    read_domain_voltage,
    set_domain_voltage):
    '''
    Heler script to abstract logic to check and set domain SVID/DLVR equal to VNNAON

    Arguments:
        read_domain_voltage
            Function to set voltage for current domain, i.e. 
            cdie.voltage.set_atommod_voltage_dlvr for cdie atoms

        set_domain_voltage
        
        
        voltage_set

    '''
    vnnaon_voltage  = nevo.read_value('VNNAON')
    
    read_domain_voltage()

    if vnnaon_voltage > domain_voltage:
        set_domain_voltage(vnnaon_voltage)
        print("Setting domain rail equal to VNNAON")