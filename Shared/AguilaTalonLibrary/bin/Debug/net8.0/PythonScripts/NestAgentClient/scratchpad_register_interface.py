'''
This Python script is intended to be used as an example guide on how to implement a specific scratchpad register interface.

NOTE: This example source file will work just for ICX product. Please update with the correct registers for another specific product.
'''

def write_host_to_target_scratchpad(value):
    '''
    Writes the value provided to the host_to_target scratchpad register.
    '''
    try:
        # Writing the host_to_target scratchpad register for ICX product
        # itp.uncores[0].state.regbus.CFG32.NCDECS_CR_BIOSNONSTICKYSCRATCHPAD5_CFG = value
        raise RuntimeError('Using write_host_to_target_scratchpad example implementation.\nPlease update with the correct registers for a specific product.\nFor details on the NEST implementation, see: https://dev.azure.com/MIT-STA/STA_Tools/_wiki/wikis/Aguila%20Dev%20Wiki/24423/NEST')
    except:
        print('Got an error while executing write_host_to_target_scratchpad')


def read_host_to_target_scratchpad():
    '''
    Reads the value from the host_to_target scratchpad register.

    Returns the contents of the host_to_target scratchpad register.
    '''
    try:
        # Reading the host_to_target scratchpad register for ICX product
        # return int(itp.uncores[0].state.regbus.CFG32.NCDECS_CR_BIOSNONSTICKYSCRATCHPAD5_CFG)
        raise RuntimeError('Using read_host_to_target_scratchpad example implementation.\nPlease update with the correct registers for a specific product.\nFor details on the NEST implementation, see: https://dev.azure.com/MIT-STA/STA_Tools/_wiki/wikis/Aguila%20Dev%20Wiki/24423/NEST')
    except:
        return 0

def write_target_to_host_scratchpad(value):
    '''
    Writes the value provided to the target_to_host scratchpad register.
    '''
    try:
        # Writing to target_to_host scratchpad register for ICX product
        # itp.uncores[0].state.regbus.CFG32.NCDECS_CR_BIOSNONSTICKYSCRATCHPAD6_CFG = value
        raise RuntimeError('Using write_target_to_host_scratchpad example implementation.\nPlease update with the correct registers for a specific product.\nFor details on the NEST implementation, see: https://dev.azure.com/MIT-STA/STA_Tools/_wiki/wikis/Aguila%20Dev%20Wiki/24423/NEST')
    except:
        print('Got an error while executing write_target_to_host_scratchpad')

def read_from_target_to_host_scratchpad():
    '''
    Reads the value from the target_to_host scratchpad register.

    Returns the contents of the target_to_host scratchpad register.
    '''
    try:
        # Reading the target_to_host scratchpad register for ICX product
        # return int(itp.uncores[0].state.regbus.CFG32.NCDECS_CR_BIOSNONSTICKYSCRATCHPAD6_CFG)
        raise RuntimeError('Using read_from_target_to_host_scratchpad example implementation.\nPlease update with the correct registers for a specific product.\nFor details on the NEST implementation, see: https://dev.azure.com/MIT-STA/STA_Tools/_wiki/wikis/Aguila%20Dev%20Wiki/24423/NEST')
    except: 
        return 0

def write_to_target_working_scratchpad(value):
    '''
    Writes the value provided to the target_working scratchpad register.
    '''
    try:
        # Writing to target_working scratchpad register for ICX product
        # itp.uncores[0].state.regbus.CFG32.NCDECS_CR_BIOSNONSTICKYSCRATCHPAD4_CFG = value
        raise RuntimeError('Using write_to_target_working_scratchpad example implementation.\nPlease update with the correct registers for a specific product.\nFor details on the NEST implementation, see: https://dev.azure.com/MIT-STA/STA_Tools/_wiki/wikis/Aguila%20Dev%20Wiki/24423/NEST')
    except:
        print('Got an error while executing write_to_target_working_scratchpad')

def read_from_target_working_scratchpad():
    '''
    Reads the value from the target_working scratchpad register.

    Returns the contents of the target_working scratchpad register.
    '''
    try:
        # Reading the target_working scratchpad register for ICX product
        # return int(itp.uncores[0].state.regbus.CFG32.NCDECS_CR_BIOSNONSTICKYSCRATCHPAD4_CFG)
        raise RuntimeError('Using read_from_target_working_scratchpad example implementation.\nPlease update with the correct registers for a specific product.\nFor details on the NEST implementation, see: https://dev.azure.com/MIT-STA/STA_Tools/_wiki/wikis/Aguila%20Dev%20Wiki/24423/NEST')
    except:
        return 0
