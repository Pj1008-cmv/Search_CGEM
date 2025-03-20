"""TTK3 API as-is from MTL repo.  Written by Craig Reichelt."""

import sys
import time

# automation code imports
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

# TTK3 imports
path = [
    r'C:\SVShare\user_apps\TTK3',
    r"C:\SVSHARE\User_Apps\TTK3\API\Python"
]
for item in path:
    if not item in sys.path:
        sys.path.append(item)
import GpiosManager

# TTK3 Channel assignments
A = 0
B = 1
H = 7

# Globals for channel names
master      = 1 # CH 1: Master
port80      = 2 # Ch 2: Port80
slave       = 3 # Ch 3: Slave
internal    = 4 # Ch 4: Internal to TTK3
                # CH 5: ??

dir_out = 0
dir_in = 1

# ---
# TTK3 function wrappers


gpioint = GpiosManager.GpiosManager()

def SPI_BIOS_Programmer(file_path):
    '''
    Flashes IFWI given binary file path

    Arguments:
        file_path
            Path to valid IFWI binary

    Returns:
        None
    '''
    global gpioint
    import SPI_Programmer

    try:
        programmer = SPI_Programmer.BiosProgrammer()
        logger.info("Created BIOS programmer object")

        programmer.Open()
        
        logger.info("Detected Chips: ".format(programmer.GetDetectedChips()))
        programmer.DetectChip()

        logger.info(f"Batching IFWI {file_path}")
        programmer.BatchImg(file_path)

        programmer.Verify()

        programmer.Close()
        logger.info("Closed BIOS programmer object")

    except:
        logger.error(("Unexpected error:", sys.exc_info()[0]))
        logger.error(("Unexpected error:", sys.exc_info()[1]))

        ReadCATERR()

def readBiosVersion():
    import SPI_Programmer

    programmer = SPI_Programmer.BiosProgrammer()
    logger.info("Created BIOS programmer object")

    programmer.Open()

    PowerControl(0, "OFF")
    time.sleep(5)
        
    logger.info(f"Detected Chips: {programmer.GetDetectedChips()}")
    programmer.DetectChip()

    version = programmer.ReadBiosVersion()
    logger.info(f"\tTarget board ID:        {version.BoardID}")
    logger.info(f"\tTarget board revision:  {version.BoardRev}")
    logger.info(f"\tBioS version on target: {version.MajorVersion}.{version.MinorVersion}")

    BIOSVersion = {
        "board id": version.BoardID,
        "board rev": version.BoardRev,
        "bios version": version.MajorVersion + "." + version.MinorVersion
    }
    programmer.Close()

    return BIOSVersion

def ReadCATERR():
    '''
    Reads CATERR signal from GPIO

    Arguments:
        None

    Returns:
        caterr_on
            Returns True if CATERR is active
    '''
    import GpiosManager
    gpioint = GpiosManager.GpiosManager()
    cutErrGpio = gpioint.GetGpioObj(4, 7) #E7 - CUTERR
    gpios = [cutErrGpio]
    gpioint.SetGpiosVoltageLevel(gpios, 1, 1.8)

    pltIsOn = FrontPanel("status", 0)
    vs = gpioint.ReadGpios(gpios, 1)
    caterr_on = bool(not vs[0] and pltIsOn)

    logger.info(f"System on: {pltIsOn == 1} CATERR active: {not vs[0]}")
    return caterr_on

def set_powerspliter_port_state(port_num, func):
    '''
    Toggles Power control port <port_num> on or off depending on value of func

    Arguments:
        port_num
            Power control port to be toggled

        func
            "on"
                Toggles port_num on
            "off"
                Toggles port_num off

    Returns:
        state
            current state of port port_num
    '''
    import PowerControl

    powercontrol = PowerControl.PowerControl()

    state = {
        True: "on",
        False: "off"
    }

    devices = {
        0: 'power splitter',
        1: 'ATX',
        2: 'PDU'
    }

    powercontrol.Open()

    try:
        numDevices = powercontrol.GetNumDevices()
        logger.info(f"Found {numDevices} connected power control devices.")
        if numDevices:
            dev = devices[powercontrol.GetDeviceSType()]
            logger.info(f"Device types: {dev}")

            ports = powercontrol.GetNumPorts()
            logger.info(f"Number of ports on {dev}: {ports}")
            for idx in range(ports):
                logger.info(f"{dev} port {idx} state: {state[powercontrol.GetPortState(idx)]}")
            
        if func.lower() == "on":
            powercontrol.PortOn(port_num)
        elif func.lower() == "off":
            powercontrol.PortOff(port_num)

        logger.info(f"Port {port_num} is now {state[powercontrol.GetPortState(port_num)]}")

        return state[powercontrol.GetPortState(port_num)]

    finally:
        powercontrol.Close()

def read_powersplitter_port_state(port_num):
    '''
    Reads state of specified power splitter port number.

    Arguments:
        port_num
            Power control port to be toggled

    Returns:
        state
            current state of port port_num
    '''
    import PowerControl

    powercontrol = PowerControl.PowerControl()

    state = {
        True: "on",
        False: "off"
    }
    powercontrol.Open()
    try:
        return state[powercontrol.GetPortState(port_num)]
    finally:
        powercontrol.Close()

def device():
    '''
    Returns data for attached TTK3 type devices. May include PowerSplitters as well.

    Arguments: 
        None

    Returns:
        devicelist
            Dictionary in the following format:
            
            device 1 serial nmumber: device 1 firmware revision, device 1 hardware revision
            device 2 serial nmumber: device 2 firmware revision, device 2 hardware revision
            etc.
    '''
    import Ttk3Device
    from Ttk3Device import DeviceType

    devicelist = {}

    ttkDeviceApi =Ttk3Device.Ttk3Device()

    logger.info("Checking TTK3 connection:\n")
    logger.info("TTK3 USB device is connected: " + str(ttkDeviceApi.IsDeviceConnected(DeviceType.TTK3)))
    logger.info("TTK3 driver is installed: " + str(ttkDeviceApi.IsDriverInstalled(DeviceType.TTK3)))
    logger.info("TTK3 USB device is connected and driver is installed: " + str(ttkDeviceApi.IsDeviceConnectedAndDriverInstalled(DeviceType.TTK3)))

    #read number connected devices
    numConnectedDevices = ttkDeviceApi.GetNumConnectedDevices()

    #read SN for each device
    for i in range(numConnectedDevices):
        deviceSerial = ttkDeviceApi.GetDeviceSeriaNumberByIndex(i)
        
        ttkDeviceApi.OpenIndex(i)
        deviceFirmware = hex(ttkDeviceApi.GetFirmwareRevision())
        deviceHardwareRev = ttkDeviceApi.GetHardwareRevision()

        logger.info(f"Found device {deviceSerial} with hardware rev {deviceHardwareRev} and firmware {deviceFirmware}")

        devicelist[deviceSerial] = [deviceFirmware, deviceHardwareRev]
        ttkDeviceApi.Close()

    return devicelist

def read_POST(verbose=True):
    '''
    Returns current platform POST code

    Arguments:
        None

    Returns:
        postcode
            Port 80 POST Code
    '''
    import Port80
    try:
        if verbose:
            logger.info(f"starting POST state read...")
        
        port80 = Port80.Port80()
        port80.Open()

        postcode = (port80.Read())
        port80.Close

        return postcode

    except:
        logger.error(sys.exec_info()[0])
        logger.error(sys.exec_info()[1])

def reservedGPIO(gpio, direction, value):
    '''
    Allows control of reserved GPIOs:

        GPIO	                Value
        CLR_CMOS	            0
        FP_RESET	            1
        J0	                    2
        D13	                    3
        D12	                    4
        H1	                    5
        D7	                    6
        D3	                    7
        D2	                    8
        H0	                    9
        K3	                    10
        K2	                    11
        K1	                    12
        J3	                    13
        H2	                    14
        A1	                    15
        F0	                    16
        D1	                    17
        SLP_S3	                18
        CATERR	                19
        SLP_S0	                20
        SLP_S4	                21
        PWRGOOD	                22
        PWRBTN	                23
        PLT_GPIO1	            24
        PLT_GPIO2	            25
        PLT_GPIO3	            26
        PLT_GPIO4	            27
        PLT_GPIO5	            28
        SLP_S5	                29
        PLT_GPIO6	            30
        QSPI_EXT1_OUT_EN	    31
        QSPI_EXT2_OUT_ENB	    32
        I2C0_EN	                33
        CO_V33_MAIN_PWR_ERR	    34
        QSPI_UNI_OE	            35
        MCU_QSPI1_QS_OE_N	    36
        IO_EXP_6424_RESET_N	    37
        CO_IO_EXP_INT_N	        38
        I2C2_EN	                39
        I2C1_EN	                40
        QSPI1_PWR_EN	        41
        QSPI_EXT_PWR_EN	        42
        UNI_QSPI_PWR_EN	        43
        UART1_EN_N	            44
        UART2_EN	            45
        BT_EN	                46
        TGT_MCLR_N	            47
        BUTTON_2	            48
        BUTTON_3	            49
        LED_MAIN_INIT_DONE_N	50
        LED_MAIN_ALARM_N	    51
        HW_REV_1	            52
        HW_REV_0	            53
        HW_REV_2	            54
        HW_REV_3	            55
        SEG_A	                56
        SEG_B	                57
        SEG_C	                58
        SEG_D	                59
        SEG_E	                60
        SEG_F	                61
        SEG_G	                62
        LAN_RST_N	            63
        LAN_INT_N	            64
        SEG_DP	                65
        DIG_0	                66
        DIG_1	                67
        DIG_2	                68
        DIG_3	                69
        MAIN_MCLR_N	            70
        DEV_TO_UNI_N	        71
        DEV_OUT_EN_N	        72
        GREEN_LED_N	            73
        YELLOW_LED_N	        74
        RED_LED_N	            75
        WHITE_LED_N	            76
        LED_TGT_ALARM_N	        77
        LED_TGT_INIT_DONE_N	    78
        QSPI1_OUT_EN	        79


    Arguments:
        gpio
            reserved GPIO to be modified
        
        direction:
            "in": configfure GPIO as INPUT
            "out": configure GPIO as OUTPUT

    Returns:
        None
    '''
    
    reserved_gpio = {
        'CLR_CMOS': 0,
        'FP_RESET': 1,
        'J0': 2,
        'D13': 3,
        'D12': 4,
        'H1': 5,
        'D7': 6,
        'D3': 7,
        'D2': 8,
        'H0': 9,
        'K3': 10,
        'K2': 11,
        'K1': 12,
        'J3': 13,
        'H2': 14,
        'A1': 15,
        'F0': 16,
        'D1': 17,
        'SLP_S3': 18,
        'CATERR': 19,
        'SLP_S0': 20,
        'SLP_S4': 21,
        'PWRGOOD': 22,
        'PWRBTN': 23,
        'PLT_GPIO1': 24,
        'PLT_GPIO2': 25,
        'PLT_GPIO3': 26,
        'PLT_GPIO4': 27,
        'PLT_GPIO5': 28,
        'SLP_S5': 29,
        'PLT_GPIO6': 30,
        'QSPI_EXT1_OUT_EN': 31,
        'QSPI_EXT2_OUT_ENB': 32,
        'I2C0_EN': 33,
        'CO_V33_MAIN_PWR_ERR': 34,
        'QSPI_UNI_OE': 35,
        'MCU_QSPI1_QS_OE_N': 36,
        'IO_EXP_6424_RESET_N': 37,
        'CO_IO_EXP_INT_N': 38,
        'I2C2_EN': 39,
        'I2C1_EN': 40,
        'QSPI1_PWR_EN': 41,
        'QSPI_EXT_PWR_EN': 42,
        'UNI_QSPI_PWR_EN': 43,
        'UART1_EN_N': 44,
        'UART2_EN': 45,
        'BT_EN': 46,
        'TGT_MCLR_N': 47,
        'BUTTON_2': 48,
        'BUTTON_3': 49,
        'LED_MAIN_INIT_DONE_N': 50,
        'LED_MAIN_ALARM_N': 51,
        'HW_REV_1': 52,
        'HW_REV_0': 53,
        'HW_REV_2': 54,
        'HW_REV_3': 55,
        'SEG_A': 56,
        'SEG_B': 57,
        'SEG_C': 58,
        'SEG_D': 59,
        'SEG_E': 60,
        'SEG_F': 61,
        'SEG_G': 62,
        'LAN_RST_N': 63,
        'LAN_INT_N': 64,
        'SEG_DP': 65,
        'DIG_0': 66,
        'DIG_1': 67,
        'DIG_2': 68,
        'DIG_3': 69,
        'MAIN_MCLR_N': 70,
        'DEV_TO_UNI_N': 71,
        'DEV_OUT_EN_N': 72,
        'GREEN_LED_N': 73,
        'YELLOW_LED_N': 74,
        'RED_LED_N': 75,
        'WHITE_LED_N': 76,
        'LED_TGT_ALARM_N': 77,
        'LED_TGT_INIT_DONE_N': 78,
        'QSPI1_OUT_EN': 79
    }

    gpio_dir = {
        'in': 0,
        'out': 1
    }

    import GpiosManager

    gpioint = GpiosManager.GpiosManager()
    
    gpio = gpioint.GetReservedGpioObj(reserved_gpio[gpio.upper()])
    gpio.Open()
    logger.info(gpio.GetDirection())


    if gpio in ['CLR_CMOS', 'FP_RESET', 'PWRBTN']:
        gpioint.SetGpiosDirection([gpio], 1, 1)
    elif gpio in ['CATERR', 'PWRGOOD']:
        gpioint.SetGpiosDirection([gpio], 1, 0)
    else:
        gpioint.SetGpiosDirection([gpio], 1, gpio_dir[direction.lower()])

    if direction.lower() == "out":
        if value:
            gpioint.SetGpios([gpio], 1)
        else:
            gpioint.ClearGpios([gpio], 1)

def GPIOs(gpio, direction, value):
    '''
    

    Arguments:
        gpio
            GPIO to be manipulated

        direction
            data direction for the indicated GPIO
                in for IN
                out for OUT

        value
            value to be written to the specified GPIO; will be ignored if direction set to IN

    Returns:
    '''
    import GpiosManager

    gpiodir = {
        'in': 0,
        'out': 1
    }

    gpioint = GpiosManager.GpiosManager()

def FrontPanel(function, time):
    '''
        Either presses power or reset button for time ms or reads current platform status

    Arguments:
        function
            'power'
                Presses power button on front panel header
            'reset'
                Presses reset button on front panel header
            'status'
                Reads current platform status
                    True
                        Platform is ON
                    False
                        Platform is OFF

        time
            Time in ms to perform the specified function. Will be ignored for 'status'.

    Returns:
        pltStatus
            True
                Platform is ON
            False
                Platform is OFF
    '''
    import FrontPanel

    platStatus = {
        True: "ON",
        False: "OFF"
    }

    try:
        logger.info("start...")

        pltInterface = FrontPanel.FrontPanel()

        pltInterface.Open()

        if function.lower() == 'power':
            logger.info(f"Pressing front panel Power for {time} milliseconds")
            pltInterface.Power(time)

        elif function.lower() == 'reset':
            logger.info(f"Pressing front panel Reset for {time} milliseconds")
            pltInterface.Reset(time)

        elif function.lower() == 'status':
            pltStatus = pltInterface.GetFrontPanelStatus()
            logger.info(f"Platform is currently {platStatus[pltStatus]}")
        else:
            logger.error("Invalid function for Front Panel")

        pltInterface.Close()


        if function.lower() == 'status':
            return pltStatus

    except:
        logger.error(sys.exec_info()[0])
        logger.error(sys.exec_info()[1])

def readI2C(address, offset, bytes):
    '''
    Wrapper for reading I2C via TTK3; creates I2cControl objsect from I2cControl library in TTK3 API, opens I2C object, reads from <address> for <bytes>
    bytes, parses bytecode to unicode, and returns result

    Parameters
        address
            Address to start reading from over I2C bus
        bytes
            Number of bytes to be read from starting address

    Returns
        Unicode string of 
    '''
    import GpiosManager, I2cControl, codecs
    
    global A
    global B
    global H

    global master
    global port80
    global slave
    global internal

    global dir_in
    global dir_out

    i2c = I2cControl.I2cControl()
    
    gpioint = GpiosManager.GpiosManager()
    gpio1 = gpioint.GetGpioObj(B, 12) #B12->I2C0_EN GPIO, B13->I2C1, H7->I2C2
    gpios = [gpio1]
    gpioint.SetGpiosDirection(gpios, 1, dir_out)
    gpioint.SetGpios(gpios, 1)

    i2c.Open()
    i2c.SelectI2cNumber(1)
    retval = i2c.ReadWithOffset(address, offset, bytes)
    i2c.Close()

    retval = retval.hex()

    logger.info(f"Found value {retval}")

    try:
        retstr = codecs.decode(retval, "hex").decode("ASCII")
    except:
        retstr = ''

    logger.info(f"Returning ASCII decoded string {retstr}")

    return retstr

def MouseEmu(buffer):
    '''
    Sends a string of commands from a buffer passed as an argument
    
    Max Value: 32767

    button (
        1 - Left button
        2 - right button
        4 - middle button
        0 - release
    )
    Wheel (int between -127 and 127)

    Arguments:
        buffer
            A list of actions to be performed by the mouse

    Returns:
        None
    '''
    import MouseEmulator

def KBEmu():
    '''
    

    Arguments:

    Returns:
    '''
    import KeyBoardEmulator

# ---
# Additional functionality

def wait_until_specified_POST_code(target_post_code, timeout_s=300, per_iteration_delay_s=0.1, post_delay_s=2):
    counter = 0
    last_code = ''
    while(True):
        time.sleep(per_iteration_delay_s)
        counter += per_iteration_delay_s
        post_code = read_POST(verbose=False)
        # printing out each new post code that is encountered
        if post_code != last_code:
            logger.info(f'New POST code: {post_code}')
            last_code = post_code
        if post_code == "0080":
            logger.info(f'reached 0080! will power cycle.')
            set_powerspliter_port_state(0, "off")
            time.sleep(5)
            set_powerspliter_port_state(0, "on")
        # testing for loop break condtisions
        if post_code == target_post_code:
            logger.info(f'reached {target_post_code}!  Delaying {post_delay_s} sec to allow system to settle.')
            time.sleep(post_delay_s)
            break
        elif counter == timeout_s:
            msg = f'Unable to reach POST code {target_post_code} in {timeout_s} seconds'
            logger.error(f'{msg} - Raising exception to stop execution.')
            raise Exception(msg)

def wait_until_specified_POST_code_SOC(target_post_code, timeout_s=300, post_delay_s=2):
    counter = 0
    last_code = ''
    while(True):
        time.sleep(1)
        counter += 1
        post_code = read_POST(verbose=False)
        # printing out each new post code that is encountered
        if post_code != last_code:
            logger.info(f'New POST code: {post_code}')
            last_code = post_code
        # testing for loop break condtisions
        if post_code == target_post_code:
            logger.info(f'reached {target_post_code}!  Delaying {post_delay_s} sec to allow system to settle.')
            time.sleep(post_delay_s)
            break
        if post_code == "0080":
            logger.info(f'reached 0080! will power cycle.')
            set_powerspliter_port_state(0, "off")
            time.sleep(5)
            set_powerspliter_port_state(0, "on")
            
        if post_code == "6F4C":
            logger.warning("TTk3 in bad state will try to restart TTK3")
            set_powerspliter_port_state(3, "off")
            time.sleep(15)
            logger.info("Powering on TTK3")
            set_powerspliter_port_state(3, "on")
            set_powerspliter_port_state(0, "on")
            # os.system(r'C:\SVSHARE\User_Apps\PowerSplitter\PowerSplitterCL.exe portpower 2 True')
            break
        if post_code == "0000":
            logger.warning("System posted to 0000 powering off TTK3 and Target to recover")
            set_powerspliter_port_state(3,"off")
            time.sleep(5)
            set_powerspliter_port_state(3,'on')
            set_powerspliter_port_state(2,"off")
            time.sleep(5)
            set_powerspliter_port_state(2,"on")
            logger.warning("Powering on TTK3")
            set_powerspliter_port_state(0, "off")
            time.sleep(5)
            set_powerspliter_port_state(0, "on")
            logger.warning("Powering Target ON")
            break
        if post_code == "FFFF":
            logger.warning("System posted to FFFF. Power Cycling the target")
            logger.warning("Powering off TTK3")
            set_powerspliter_port_state(3,"off")
            time.sleep(5)
            set_powerspliter_port_state(3,'on')
            logger.warning("Powering on TTK3")
            logger.warning("Powering Target OFF")
            set_powerspliter_port_state(0, "off")
            time.sleep(5)
            set_powerspliter_port_state(0, "on")
            logger.warning("Powering Target ON")
            break
        if post_code == "EC07":
            logger.warning("System posted to EC07. Power Cycling the target")
            set_powerspliter_port_state(2,"off")
            time.sleep(5)
            set_powerspliter_port_state(2,"on")
            set_powerspliter_port_state(3,"off")
            time.sleep(5)
            set_powerspliter_port_state(3,'on')
            logger.warning("Powering off TTK3")
            set_powerspliter_port_state(0, "off")
            time.sleep(5)
            set_powerspliter_port_state(0, "on")     
            break    
        elif counter == timeout_s:
            msg = f'Unable to reach POST code {target_post_code} in {timeout_s} seconds'
            logger.error(f'{msg} - Raising exception to stop execution.')
            raise Exception(msg)


if __name__ == "__main__":
    plain_text = readI2C(0xAC, 0x0, 0x50)
    print(plain_text)