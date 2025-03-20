"""Wrapper around Nevo VFT python API."""

# imports, std lib
from enum import Enum
import sys

# NEVO
if (nevopath:=r'C:\VFT64\PythonScripts') not in sys.path:
    sys.path.append(nevopath)
from VFTWrapperClass import VFTWrapper

# local imports
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger
from generic_product.utilities.singleton import Singleton

def read_value(channel_selection, min=0.0, max=2.0, attempt=1) -> dict:
    """If channel selection not yet selected, do so;  read/return value.
    Convinence function.
    """
    n = Nevo()
    channel_selection = n.normalize_channel_selection_argument(channel_selection)
    if not n.check_channels_selected(channel_selection):
        n.select_channel(channel_selection)
    readback = n.read_value(channel_selection, log_vals=False)
    if all(min < v < max for v in readback.values()):
        logger.info(f'After {attempt} attempts:')
        n.log_readback(readback)
        # return a single float if there's only one channel
        if len(channel_selection) == 1:
            return readback[channel_selection[0]]
        # if there are multiple channels, return the dict
        return readback
    return read_value(channel_selection, min, max, attempt+1)


class NevoStates(Enum):
    UNINITIALIZED = 1
    INITIALIZED = 2
    ENUMERATED = 3
    CHANNEL_SELECTED = 4
    TERMINATED = 1

class Nevo(Singleton):
    """Singleton wrapper for Nevo voltage monitor.

    - `__new__` and `__init__` are called on first instantiation, within `lot_start.py`
    - `terminate()` is called in `lot_end.py`
    - `read_voltage_point()` allows selection and reading of voltage channel

    States:
        start state, Nevo.terminate()
            v
    1. NevoStates.UNINITIALIZED
            |
        Nevo.initialize()
            |
            v
    2. NevoStates.INITIALIZED
            |
        Nevo.enumerate()
            |
            v
    3. NevoStates.ENUMERATED
            |
        Nevo.select_channel(channel_selection)
            |
            v
    4. NevoStates.CHANNEL_SELECTED

        ** ready to read voltage!
    """

    _performed_first_init = False
    _vftwrapper = None
    _state = NevoStates.UNINITIALIZED
    _channels_selected = set() 

    def __init__(self):
        """Instantiation, initialization, enumeration code from C:\VFT64\PythonScripts\VmonScript.py"""
        if not self._performed_first_init:
            self._vftwrapper = VFTWrapper()
            self._performed_first_init = True
        if self._state == NevoStates.UNINITIALIZED:
            self.initialize()
            self.enumerate()

    def __del__(self):
        logger.info('Nevo object being deleted')
        if self._state != NevoStates.TERMINATED:
            self.terminate()

    def initialize(self, init_ini_filepath:str = r'C:\vft64\OsirisHal.ini') -> None:
        res = self._vftwrapper.Init(init_ini_filepath)
        self.check_error(res, 'Init', raiseerror=True)
        self._state = NevoStates.INITIALIZED

    def enumerate(self) -> None:
        """Enumerates all available NEVO channels (from C:\VFT64\PythonScripts\VmonScript.py)"""
        if self._state == NevoStates.UNINITIALIZED:
            raise RuntimeError('Error - need to initialize Nevo prior to channel enumeration')
        elif self._state != NevoStates.INITIALIZED:
            return
        channelnames, channelids = [], []
        res, id, name, type = self._vftwrapper.GetFirstActiveVmonChannel()
        self.check_error(res, "GetFirstActiveVmonChannel", raiseerror=True)
        while(id != 255):
            channelids.append(id)
            channelnames.append(name)
            res, id, name, type = self._vftwrapper.GetNextActiveVmonChannel()
            self.check_error(res, "GetNextActiveVmonChannel", raiseerror=True)
        if (len(channelnames) == 0):
            msg = "No channels found during NEVO enumeration process."
            logger.error(msg)
            raise RuntimeError(msg)
        logger.info('Here are all active channels found: ' + str(channelnames))
        self._state = NevoStates.ENUMERATED

    @staticmethod
    def normalize_channel_selection_argument(channel_selection):
        """Ensures all channel selection arguments are contained within list."""
        if type(channel_selection) == str:
            channel_selection = [channel_selection]
        if type(channel_selection) != list:
            logger.error(msg:='`channel_selection` argument must either be str or list of str.')
            raise RuntimeError(msg)
        return channel_selection        

    def select_channel(self, channel_selection) -> None:
        """Selects channel(s) for reading.  (From C:\VFT64\PythonScripts\VmonScript.py)"""
        if self._state not in {NevoStates.ENUMERATED, NevoStates.CHANNEL_SELECTED}:
            logger.error(msg:='Cannot perform channel selection unless Nevo has been initialized/enumerated.')
            raise RuntimeError(msg)
        channel_selection = self.normalize_channel_selection_argument(channel_selection)
        res = self._vftwrapper.SelectVoltMonMonitorChannelsByName(channel_selection)
        self.check_error(res, f"SelectVoltMonMonitorChannelsByName({channel_selection!r})", raiseerror=True)
        self._state = NevoStates.CHANNEL_SELECTED
        self._channels_selected = set(channel_selection)

    def check_channels_selected(self, channel_selection) -> bool:
        """Verifies that all channels within argument have already been selected."""
        return all(ch in self._channels_selected for ch in channel_selection)

    @staticmethod
    def log_readback(readback_dict) -> None:
        """Logs values read from channels."""
        logger.info('Voltage read:')
        for ch, v in readback_dict.items():
            logger.info(f'    {ch:>8}: {v:.5f}V')

    def read_value(self, channel_selection, log_vals=True) -> dict:
        """Reads specified channel(s) and returns dict mapping channel(s) to read value(s)."""
        # argument, object-state checking
        if self._state != NevoStates.CHANNEL_SELECTED:
            logger.error(msg:='Cannot read voltage before channel selection.')
            raise RuntimeError(msg)
        channel_selection = self.normalize_channel_selection_argument(channel_selection)
        if not self.check_channels_selected(channel_selection):
            logger.error(msg:=f'One or more channels specified ({channel_selection}) have not been selected ({self._channels_selected}).')
            raise RuntimeError(msg)
        # perform voltage read
        res, val = self._vftwrapper.GetVoltMonVoltAvgByName(channel_selection)
        self.check_error(res, f"GetVoltMonVoltAvgByName({channel_selection!r})")
        # format for output and return
        readback = {channel : float(voltage) for channel, voltage in zip(channel_selection, val)}
        if log_vals:
            self.log_readback(readback)
        return readback
        
    def terminate(self) -> None:
        """Terminates connection to NEVO."""
        res = self._vftwrapper.Terminate()
        self.check_error(res, "Terminate")
        self._state = NevoStates.UNINITIALIZED
        logger.info('Nevo object being destroyed -- successfully terminated.')

    def check_error(self, res, action, raiseerror=False) -> bool:
        """From C:\VFT64\PythonScripts\VmonScript.py: checks response from Nevo"""
        if( res == 0):
            return False
        logger.error(f"{action} failed")
        res, err = self._vftwrapper.GetSinai2LastError()
        if(res == 0):
            logger.error(err)
        else:
            logger.error("Can't get last error from Sinai")
        if raiseerror:
            raise RuntimeError()
        return True

if __name__ == '__main__':
    print('finished import')