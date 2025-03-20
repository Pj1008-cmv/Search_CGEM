'''
Script collecting CMV voltage control scripts for MTL

Methods:
    set_voltage(domain, voltage)
    set_rwc_voltage(corenum, voltage)
    set_cmt_voltage(module, voltage)
    set_vccr_voltage(voltage)
    set_vccgt_voltage(voltage)
    set_vccsa_voltage(voltage)
    set_vnnaon_voltage(voltage)
    set_ccf_llc_vnnaon()
    set_cdie_atom0_mux_vnnaon()
    set_cdie_atom1_mux_vnnaon()
        
'''
import argparse
import json
import logging
import os
import sys
import time

import ipccli
#from pysvtools.pmext.mtl_pm_dir.tools import svid as s
#from pysvtools.pmext.mtl_pm_dir.tools import dlvr as d

### path append scripting
READ = "r"
#path_file = r"C:\sthi\Fusion\meteorlake.mp.cdie-gcd-socnorth\python\path_list.json"
path_file = r"C:\SVSHARE\cmv_client_automation_mtl\python\path_file.json"
PATH_LIST = "path_list"

#SVID_rail_import = r"C:\pythonsv\meteorlake\users\oqmohsin"



# Open JSON file and parse to json_dict dictionary
with open(path_file, READ) as file_obj:
    json_dict = json.load(file_obj)
file_obj.close()

# Iterate over and append paths in path_list key in json_dict
for path in json_dict[PATH_LIST]:
    if path not in sys.path:
        sys.path.append(path)
###########################

# local import(s)
import globalVars
import mtl_voltage_monitor
import voltage_control ## ARL
# pythonsv import(s)
from users.dlvr import dlvr_debug_script as dlvr
from users.oqmohsin import set_sa_svid as svid
# CMV data automation import(s)
import general_methods

MAX_ALLOWED_DLVR_VOLTAGE = 1.4
MIN_ALLOWED_DLVR_VOLTAGE = 0.45
# Variables
ipc = itp = ipccli.baseaccess()
# Logging
log_level       = logging.INFO
logger          = general_methods.setupLog(logLevel = log_level)

if itp.islocked():
    itp.unlock()

# # Instantiate objects to set voltages (SVID/DLVR)
# svid = s.Svid()
# dlvr = d.Dlvr()

selfname        = os.path.basename(__file__).split(".")[0]
voltage_domains = {
    "VCCR",
    
    "VCCIA",

    "VCC_CORE0",
    "VCC_CORE1",
    "VCC_CORE2",
    "VCC_CORE3",
    "VCC_CORE4",
    "VCC_CORE5",
    
    "VCC_ATOM0",
    "VCC_ATOM1",
    
    "VNNAON",
    "VCC_GT",
    "VCC_SA"
}

sram_domains = {
    "atom0": {
        "pll": "cdie.dmudata.io_wp_cv_ia_ccp_dvfs_ia_ccp6.ia_ratio",
        "voltage_rail": "vcc_atom0",
        "vf_ratios": "cdie.fuses.dmu_fuse.fw_fuses_atom_vf_ratio_",
        "vf_voltages": "cdie.fuses.dmu_fuse.fw_fuses_atom_vf_voltage_",
        "enable": "cdie.atom0.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en", 
        "select": "cdie.atom0.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel"
        },
    "atom1": {
        "pll": "cdie.dmudata.io_wp_cv_ia_ccp_dvfs_ia_ccp7.ia_ratio",
        "voltage_rail": "vcc_atom1",
        "vf_ratios": "cdie.fuses.dmu_fuse.fw_fuses_atom_vf_ratio_",
        "vf_voltages": "cdie.fuses.dmu_fuse.fw_fuses_atom_vf_voltage_",
        "enable": "cdie.atom1.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en", 
        "select": "cdie.atom1.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel"
        },
    "ccf": {
        "pll": "cdie.dmudata.io_wp_cv_ring.ratio",
        "voltage_rail": "vccr",
        "vf_ratios": "cdie.fuses.dmu_fuse.fw_fuses_ring_vf_ratio_",
        "vf_voltages": "cdie.fuses.dmu_fuse.fw_fuses_ring_vf_voltage_",
        "enable": "cdie.taps.soc_cbpma0_ccf_pma_inst_pma.pma_overrides.pma_llc_pwr_mux_sel_ovrd_en", 
        "select": "cdie.taps.soc_cbpma0_ccf_pma_inst_pma.pma_overrides.pma_llc_pwr_mux_sel_ovrd_val"
        },
    "soc_atom": {
        "pll": "",
        "voltage_rail": "vccsa",
        "vf_ratios": "",
        "vf_voltages": "",
        "enable": "soc.north.atom.pma_pmsb.clpma_cr_surv_ovrd_en2.l2_pwrmux_sel_ovrt_en", 
        "select": "soc.north.atom.pma_pmsb.clpma_cr_surv_obs_l2_biu_pgctl.l2_pwrmux_sel"
        },
    "vpu": {
        "pll": "",
        "voltage_rail": "",
        "vf_ratios": "",
        "vf_voltages": "",
        "enable": "", 
        "select": ""
        },
    "ipu": {
        "pll": "",
        "voltage_rail": "",
        "vf_ratios": "",
        "vf_voltages": "",
        "enable": "", 
        "select": ""
        },
    "gtm": {
        "pll": "",
        "voltage_rail": "",
        "vf_ratios": "",
        "vf_voltages": "",
        "enable": "", 
        "select": ""
        },
    "display": {
        "pll": "",
        "voltage_rail": "",
        "vf_ratios": "",
        "vf_voltages": "",
        "enable": "", 
        "select": ""
        },
}
# added by Hsin. NEVO's rail name dictionary mapping.
# Key: Domain name for DLVR
# Value: the corresponding rail name for NEVO
nevoRailNames = {"core0":"VL_CORE0",
    "core1":"VL_CORE1",
    "core2":"VL_CORE2",
    "core3":"VL_CORE3",
    "core4":"VL_CORE4",
    "core5":"VL_CORE5",
    "atom0":"VL_ATOM0",
    "atom1":"VL_ATOM1",
    "ring":"VL_LLC",
    "SA":"VCCSA",
    "GT":"VCCGT"
}
# the amount of error the DLVR setting voltage allows while setting voltage
DLVRAllowedDelta = 0.004
# voltage domain labels
RWC             = "RWC"
CMT             = "CMT"
VCCR            = "VCCR"
VNNAON          = "VNNAON"
VCCGT           = "VCC_GT"
VCCSA           = "VCC_SA"

#Sram domains
ATOM0       = "atom0"
ATOM1       = "atom1"
CCF         = "ccf"
SOC_ATOM    = "soc_atom"
VPU         = "vpu"
IPU         = "ipu"
GTM         = "gtm"
DISPLAY     = "display"

# Sram labels
PLL             = "pll"
VOLTAGE_RAIL    = "voltage_rail"
VF_VOLTAGES     = "vf_voltages"
VF_RATIOS       = "vf_ratios"
ENABLE          = "enable"
SELECT          = "select"

# Index mnemonics
lastchar        = -1
module          = 1

# Number of cores/atom modules
cores           = 0
modules         = 0

# Flag for VF on the fly enabled; switch to True when VF on the fy delivered and tested
vf_on_the_fly   = False

def set_voltage(domain, voltage):
    '''
    Sets an arbrtrary (specified) rail voltage

    Arguments:
        domain
            Domain to be set
        voltage
            Voltage to set the specified domain rail to
    
    Returns
        None
    '''

    global cores
    global voltage_domains
    global vf_on_the_fly

    # get_number_cores()

    domain = domain.upper()
    if domain in voltage_domains:
        if RWC in domain:
            
            # pick corenum from end of voltage domain string if present
            if domain[-1].isdigit():
                # Set core voltage if core in range
                corenum = int(domain[lastchar])
                if corenum in globalVars.active_cores:
                    if vf_on_the_fly:
                        logger.info("Setting {0} to {1} by VF on the Fly".format(domain, voltage))
                        set_rwc_voltage_vf(corenum, voltage)
                    else:
                        logger.info("Setting {0} to {1} by DLVR".format(domain, voltage))
                        set_rwc_voltage_dlvr(corenum, voltage)
                # Else, send error
                else:
                    logger.error("{0} out of range of product core count!".format(corenum))
            # If no core number, more logic to decide if parallel search or flat voltage 
            # shoud be set
            else:
                # Need to build parallel search for MTL here
                logger.info("Code out RWC parallel search here")
        elif CMT in domain:
            # pick corenum from end of voltage domain string if present
            if domain[-1].isdigit():
                # Fix logic for fuse disabled cores/modules - CR
                # Set module voltage
                module_num = int(domain[lastchar])
                if module_num in globalVars.active_atoms:
                    if vf_on_the_fly:
                        logger.info("Setting {0} to {1} by VF on the Fly".format(domain, voltage))
                        set_cmt_voltage_vf(module_num, voltage)
                    else:
                        logger.info("Setting {0} to {1} by DLVR".format(domain, voltage))
                        set_cmt_voltage_dlvr(module_num, voltage)
                else:
                    logger.error("{0} out of range of product module count!".format(module_num))
            
            else:
                # Need to build parallel search for MTL here
                print("Code out CMT parallel search here")
            
        elif domain == VCCR:
            if vf_on_the_fly:
                logger.info("Setting {0} to {1} by VF on the Fly".format(domain, voltage))
                set_vccr_voltage_vf(voltage)
            else:
                logger.info("Setting {0} to {1} by DLVR".format(domain, voltage))
                set_vccr_voltage_dlvr(voltage)

        elif domain == VCCGT:
            if vf_on_the_fly:
                logger.info("Setting {0} to {1} by VF on the Fly".format(domain, voltage))
                set_vccgt_voltage_vf(voltage)
            else:
                logger.info("Setting {0} to {1} by SVID".format(domain, voltage))
                set_vccgt_voltage_svid(voltage)

        elif domain == VCCSA:
            if vf_on_the_fly:
                logger.info("Setting {0} to {1} by VF on the Fly".format(domain, voltage))
                set_vccsa_voltage_vf(voltage)
            else:
                logger.info("Setting {0} to {1} by SVID".format(domain, voltage))
                set_vccsa_voltage_svid(voltage)
    # if the domain name is DLVR, we are using DLVR to set the voltage
    # added by Hsin
    elif 'DLVR' in domain:
        set_DLVR_voltage_optomized(domain, voltage)

    else:
        print("Unrecognized voltage domain")

# VF on the Fly voltage set methods
def set_rwc_voltage_vf(corenum, voltage):
    '''
    Sets MTL RWC core voltage by means of VF on the fly (pending)

    Arguments:
        corenum
            Cdie RWC core index; 0 for core0, 1 for core1, etc.
        voltage
            Voltage to set the specified module to
    
    Returns
        None
    '''
    logger.info("Setting core {0} to {1} volts".format(corenum, voltage))

def set_cmt_voltage_vf(module, voltage):
    '''
    Sets MTL CMT module voltage by means of VF on the fly (pending)

    Arguments:
        module
            Cdie CMT module index; 0 for atom0, 1 for atom1
        voltage
            Voltage to set the specified module to
    
    Returns
        None
    '''
    logger.info("Setting core {0} to {1} volts".format(module, voltage))
    pass

def set_vccr_voltage_vf(voltage):
    '''
    Sets MTL VCCR voltage by means of VF on the fly (pending)

    Arguments:
        voltage
            Voltage to set the VCCR rail to
    
    Returns
        None
    '''
    logger.info("Setting vccr to {0} volts".format(voltage))
    pass

def set_vccgt_voltage_vf(voltage):
    '''
    Sets MTL VCC GT rail by means of VF on the fly (pending)

    Arguments:
        voltage
            Voltage to set the VCC GT rail to
    
    Returns
        None
    '''
    logger.info("Setting VCCGT to {0} volts".format(voltage))

def set_vccsa_voltage_vf(voltage):
    '''
    Sets MTL VCC SA voltage by means of VF on the fly (pending)

    Arguments:
        voltage
            Voltage to set the VCC SA rail to
    
    Returns
        None
    '''



    logger.info("Setting VCCSA to {0} volts".format(voltage))

# DLVR voltage set methods
# added by Hsin
# using users.dlvr.powerstate(), until official dlvr script works
def set_DLVR_voltage(condition_name, voltage):
    if not itp.isunlocked():
        itp.unlock()
    _, domain = condition_name.split('_')
    domain = domain.lower()
    if(voltage > MAX_ALLOWED_DLVR_VOLTAGE):
        raise Exception("ERROR: DLVR SET VOLTAGE BIGGER THAN " + str(MAX_ALLOWED_DLVR_VOLTAGE))
    # voltage set command
    print('Setting voltage!')
    dlvr.powerstate( domain=domain, voltage=float(voltage), ps=0, ramp=1, method='tap' )
    time.sleep(0.3)
    # voltage read command (NEVO)
    nevoString = nevoRailNames[domain]
    feedbackV = mtl_voltage_monitor.getVoltageAverage(channelName=nevoString, numSamples=10)
    print("Read Voltage: "+ str(feedbackV))
    adjustedValue = float(voltage)
    
    # GOAL: adjust set voltage until read-back voltage is within +/- 0.0025V
    # note: ideally this difference should be half of the error margin in Fusion. However, we have no way to read the error margin dynamically from fmag for now.
    while(abs(feedbackV - voltage) >= DLVRAllowedDelta):
        #f = open("DLVR_set_voltage.txt", 'a')
        adjustedValue = adjustedValue  - (feedbackV - voltage)*0.5
        # adjust the voltage by the difference*0.8 (to avoid overshooting) in the opposite direction of the voltage
        # if the adjustedValue is bigger than max allowed voltage, its not safe and we should abort.
        if(adjustedValue > MAX_ALLOWED_DLVR_VOLTAGE):
            raise Exception("ERROR: DLVR SET VOLTAGE BIGGER THAN " + str(MAX_ALLOWED_DLVR_VOLTAGE))
        print("V " + domain + " Set:" + str(adjustedValue))

        print('Setting voltage!')
        dlvr.powerstate( domain=domain, voltage=float(adjustedValue), ps=0, ramp=1, method='tap' )
        time.sleep(0.3)
        feedbackV = mtl_voltage_monitor.getVoltageAverage(channelName=nevoString, numSamples=10)
        print("V " + domain + " Feedback:" + str(feedbackV))
        #f.write("V " + domain + " Feedback:" + str(feedbackV) + "\n")
        #f.close()
    

def set_DLVR_voltage_optomized(condition_name, voltage):
    if not itp.isunlocked():
        itp.unlock()
    _, domain = condition_name.split('_')
    domain = domain.lower()
    if(voltage > MAX_ALLOWED_DLVR_VOLTAGE):
        raise Exception("ERROR: DLVR SET VOLTAGE BIGGER THAN " + str(MAX_ALLOWED_DLVR_VOLTAGE))
    elif(voltage < MIN_ALLOWED_DLVR_VOLTAGE):
        raise Exception("ERROR: DLVR SET VOLTAGE LOWER THAN " + str(MAX_ALLOWED_DLVR_VOLTAGE))
    # voltage set command
    print('Setting voltage!')
    dlvr.powerstate( domain=domain, voltage=float(voltage), ps=0, ramp=1, method='tap' )
    time.sleep(0.3)
    # voltage read command (NEVO)
    nevoString = nevoRailNames[domain]
    # set up NEVO here. do it once per voltage call instead of keep calling per loop
    mtl_voltage_monitor.setupNEVO()
    time.sleep(0.1)
    res = mtl_voltage_monitor.i.SelectVoltMonMonitorChannelsByName(nevoString)
    mtl_voltage_monitor.CheckError(res, "SelectVoltMonMonitorChannelsByName", mtl_voltage_monitor.i)
    time.sleep(0.3)
    feedbackV = mtl_voltage_monitor.getVoltageAverage_nosetup(channelName=nevoString, numSamples=10)
    print("Read Voltage: "+ str(feedbackV))
    adjustedValue = float(voltage)
    
    # GOAL: adjust set voltage until read-back voltage is within +/- 0.0025V
    # note: ideally this difference should be half of the error margin in Fusion. However, we have no way to read the error margin dynamically from fmag for now.
    while(abs(feedbackV - voltage) >= DLVRAllowedDelta):
        #f = open("DLVR_set_voltage.txt", 'a')
        adjustedValue = adjustedValue  - (feedbackV - voltage)*0.5
        # adjust the voltage by the difference*0.8 (to avoid overshooting) in the opposite direction of the voltage
        # if the adjustedValue is bigger than max allowed voltage, its not safe and we should abort.
        if(adjustedValue > MAX_ALLOWED_DLVR_VOLTAGE):
            raise Exception("ERROR: DLVR SET VOLTAGE BIGGER THAN " + str(MAX_ALLOWED_DLVR_VOLTAGE))
        print("V " + domain + " Set:" + str(adjustedValue))

        print('Setting voltage!')
        dlvr.powerstate( domain=domain, voltage=float(adjustedValue), ps=0, ramp=1, method='tap' )
        time.sleep(0.3)
        feedbackV = mtl_voltage_monitor.getVoltageAverage_nosetup(channelName=nevoString, numSamples=10)
        print("V " + domain + " Feedback:" + str(feedbackV))
    res = mtl_voltage_monitor.i.Terminate()
    mtl_voltage_monitor.CheckError(res, "Terminate", mtl_voltage_monitor.i)
        #f.write("V " + domain + " Feedback:" + str(feedbackV) + "\n")
        #f.close()

    

def set_rwc_voltage_dlvr(corenum, voltage):
    '''
    Sets MTL RWC core voltage by means of dlvr direct control

    Arguments:
       corenum
            RWC module index; 0 for core0, 1 for core1, etc
        voltage
            Voltage to set the specified core to
    
    Returns
        None
    '''
    logger.info("Setting core {0} to {1} volts".format(corenum, voltage))

    volt_string = str(voltage) + "V"
    dlvr.set_wp(domain="core", voltage=volt_string)

def set_cmt_voltage_dlvr(module, voltage):
    '''
    Sets MTL CMT module voltage by means of dlvr direct control

    Arguments:
        module
            Cdie CMT module index; 0 for atom0, 1 for atom1
        voltage
            Voltage to set the specified module to
    
    Returns
        None
    '''
    logger.info("Setting core {0} to {1} volts".format(module, voltage))

    volt_string = str(voltage) + "V"
    dlvr.set_wp(domain="atom", voltage=volt_string)

def set_vccr_voltage_dlvr(voltage):
    '''
    Sets MTL VCCR voltage by means of DLVR

    Arguments:
        voltage
            Voltage to set the VCCR rail to
    
    Returns
        None
    '''
    logger.info("Setting vccr to {0} volts".format(voltage))

    volt_string = "{0}V".format(voltage)
    dlvr.set_vrci_wp(domain="ring", voltage=volt_string)

# SVID voltage  set methods
def set_vccgt_voltage_svid(voltage):
    '''
    Sets MTL VCC GT voltage by means of SVID

    Arguments:
        voltage
            Voltage to set VCC GT to
    
    Returns
        None
    '''
    logger.info("Setting VCCGT to {0} volts".format(voltage))
    print('Setting voltage!')
    svid.set_sa_svid(voltage, 0x1)
    time.sleep(0.3)
    feedbackV = mtl_voltage_monitor.getVoltageAverage(channelName="VCCGT", numSamples=10)
    adjustedValue = float(voltage)
    # GOAL: adjust set voltage until read-back voltage is within +/- 0.0025V
    # note: ideally this difference should be half of the error margin in Fusion. However, we have no way to read the error margin dynamically from fmag for now.
    while(abs(feedbackV - voltage) >= DLVRAllowedDelta):
        #f = open("DLVR_set_voltage.txt", 'a')
        adjustedValue = adjustedValue  - (feedbackV - voltage)*0.5
        # adjust the voltage by the difference*0.8 (to avoid overshooting) in the opposite direction of the voltage
        # if the adjustedValue is bigger than max allowed voltage, its not safe and we should abort.
        if(adjustedValue > MAX_ALLOWED_DLVR_VOLTAGE):
            raise Exception("ERROR: GT SET VOLTAGE BIGGER THAN " + str(MAX_ALLOWED_DLVR_VOLTAGE))
        print("V " + "GT" + " Set:" + str(adjustedValue))
        #f.write("V " + domain + " Set:" + str(adjustedValue)+"\n")
        print('Setting voltage!')
        svid.set_sa_svid(adjustedValue, 0x1)
        time.sleep(0.3)
        #print('-'*100 + '\n   Reading voltage using NEVO!\n' + '-'*100)
        feedbackV = mtl_voltage_monitor.getVoltageAverage(channelName="VCCGT", numSamples=10)
        print("V " + "GT" + " Feedback:" + str(feedbackV))


def set_vccsa_voltage_svid(voltage):
    '''
    Sets MTL VCC SA voltage by means of SVID

    Arguments:
        voltage
            Voltage to set the VCC SA rail to
    
    Returns
        None
    '''
    logger.info("Setting VCCSA to {0} volts".format(voltage))
    print('Setting voltage!')
    svid.set_sa_svid(voltage)
    time.sleep(0.3)
    feedbackV = mtl_voltage_monitor.getVoltageAverage(channelName="VCCSA", numSamples=10)
    adjustedValue = float(voltage)
    # GOAL: adjust set voltage until read-back voltage is within +/- 0.0025V
    # note: ideally this difference should be half of the error margin in Fusion. However, we have no way to read the error margin dynamically from fmag for now.
    while(abs(feedbackV - voltage) >= DLVRAllowedDelta):
        #f = open("DLVR_set_voltage.txt", 'a')
        adjustedValue = adjustedValue  - (feedbackV - voltage)*0.5
        # adjust the voltage by the difference*0.8 (to avoid overshooting) in the opposite direction of the voltage
        # if the adjustedValue is bigger than max allowed voltage, its not safe and we should abort.
        if(adjustedValue > MAX_ALLOWED_DLVR_VOLTAGE):
            raise Exception("ERROR: SA SET VOLTAGE BIGGER THAN " + str(MAX_ALLOWED_DLVR_VOLTAGE))
        print("V " + "SA" + " Set:" + str(adjustedValue))
        #f.write("V " + domain + " Set:" + str(adjustedValue)+"\n")
        print('Setting voltage!')
        svid.set_sa_svid(adjustedValue)
        time.sleep(0.3)
        #print('-'*100 + '\n   Reading voltage using NEVO!\n' + '-'*100)
        feedbackV = mtl_voltage_monitor.getVoltageAverage(channelName="VCCSA", numSamples=10)
        print("V " + "SA" + " Feedback:" + str(feedbackV))


def set_vnnaon_voltage_svid(voltage):
    '''
    Sets MTL VNNAON voltage by means SVID

    Arguments:
        voltage
            Voltage to set the VNNAON rail to
    
    Returns
        None
    '''
    logger.info("Setting VNNAON to {0} volts".format(voltage))

    volt_string = "{0}V".format(voltage)
	# Set VNNAON with NEVO?

# Mux swithing methods
def switch_mux_to_vnnaon(domain):
    '''
    Switches an arbitrary VNNAON MUX from the IP voltage rail to VNNAON
    Performs necessary steps to perform this switch safely (changes rail voltage, IP frequency, etc.)

    Arguments:
        domain
            Domain of the MUX to be switched

    Returns:
        None
    '''
    # 1. Read VNNAON - Reqs NEVO
    # 2. Read current mux state
    #   a. If mux set to VNNAON
    #       i.   Set IP voltage = VNNAON
    #       ii.  Set mux to IP voltage
    #       iii. Change frequency if needed
    #   b. If mux not set to VNNAON
    #       i.   Set frequency at or below VNNAON threshold
    #       ii.  Set IP voltage to VNNAON
    #       iii. Set mux to VNNAON

    global sram_domains
    global ENABLE
    global SELECT

    current_domain = sram_domains[domain.lower()]

    ratio_pll   = current_domain[PLL]
    enable      = current_domain[ENABLE]
    select      = current_domain[SELECT]
    vf_voltages = current_domain[VF_VOLTAGES]
    vf_ratios   = current_domain[VF_RATIOS]

    # Container for highest corner with fuse voltage less than VNNAON
    corner = 0

    # read vnnaon and current domain voltage from NEVO here
    vnnaon = 0
    
    # Find greatest domain VF point below VNNAON
    while eval("{0}{1}".format(vf_voltages, corner)) < vnnaon:
        corner = corner + 1
    
    current_frequency   = eval(ratio_pll)

    if current_frequency > eval("{0}{1}".format(vf_ratios, corner)):
        logger.info("Set frequency to 'corner' here")
    
    # Set IP voltage to VNNAON
    logger.info("Setting {0} rail equal to VNNAON".format(domain))

    # Enable bit can only be set if select bit set
    eval(select=1)
    eval(enable=1)
    
def switch_mux_from_vnnaon(domain):
    '''
    Switches an arbitrary VNNAON MUX from VNNAON to the IP voltage rail
    Performs necessary steps to perform this switch safely (changes rail voltage, IP frequency, etc.)

    Arguments:
        domain
            Domain of the MUX to be switched

    Returns:
        None
    '''
    global ENABLE
    global SELECT

    current_domain = sram_domains[domain.lower()]

	# Force IP Voltage domain
    enable      = current_domain[ENABLE]
    select      = current_domain[SELECT]

    # Set IP voltage = VNNAON

    eval(select=0)
    eval(enable=0)

# Method to determine cdie RWC core/CMT module counts - Chleck for enabled/disabled cores
def get_number_cores():
    '''
    Determines number of cores in product from itp.cores

    Arguments:
        None

    Returns:
        None
    '''
    global cores
    global modules
    global lastchar

    itp_cores = itp.cores
    
    max_module = 0

    cores = 0
    module_num = 0
    for node in itp_cores:
        #print(node.name)
        if "CMT" not in node.name:
            cores = cores + 1
        else:
            name_array = node.name.split("_")
            if name_array[module][lastchar].isdigit():
                module_num = int(name_array[module][lastchar])
                if module_num > max_module:
                    max_module = int(module_num)
                else:
                    max_module = int(module_num)
    
    modules = module_num + 1

if __name__ == "__main__":
    # Parse CL arguments
    if False:
        parser = argparse.ArgumentParser(description='Set voltage rails')
        parser.add_argument('Voltage domain', metavar='D', type=str, nargs='+',
                        help='A voltage domain to be set')
        parser.add_argument('Voltage', metavar='V', type=float, nargs='+',
                        help='A voltage to be set')

        args = parser.parse_args()

        logger.info(args.accumulate(args.integers))
    
    #set_DLVR_voltage("DLVR_core0",0.9)
    set_DLVR_voltage_optomized("DLVR_core0",0.7)
    #testing = 1
    #switch_mux_to_vnnaon()