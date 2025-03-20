from datetime import timedelta
import json
import Aguila

def StartBuffering(com_port: int) -> None:
    """Start buffering data received from the COM port specified by the com_port argument.
    Buffering must be started before any read operations (ReadBytes, ReadString, FindString)
    can be performed. Buffering is stopped automatically on UnitEnd and when a serial port
    is reconfigured.

    The handler for this API call is SerialServiceStartBufferingHandler.

    Args:
        com_port: The number of the COM port to buffer data from. This port must have already been configured,
                  typically via the ConfigureSerialPort test method.

    Returns:
        None

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        COM port is not configured. A message describing the error is included in the exception.
    """

    if com_port is None:
        raise TypeError("com_port must not be None.")
    result = Aguila.ServiceRequest(
        "Serial.BufferControl",
        json.dumps(
            {
                "ComPort": com_port,
                "BufferingEnabled": True
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)

def StopBuffering(com_port: int) -> None:
    """Stop buffering data received from the COM port specified by the com_port argument.
    All buffered data is cleared, and subsequent read operations will fail unless buffering
    is started again.

    The handler for this API call is SerialServiceStartBufferingHandler.

    Args:
        com_port: The number of the COM port to stop buffering. This port must have already been configured,
                  typically via the ConfigureSerialPort test method.

    Returns:
        None

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        COM port is not configured. A message describing the error is included in the exception.
    """

    if com_port is None:
        raise TypeError("com_port must not be None.")
    result = Aguila.ServiceRequest(
        "Serial.BufferControl",
        json.dumps(
            {
                "ComPort": com_port,
                "BufferingEnabled": False
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)

def ReadBytes(com_port: int) -> bytearray:
    """Return unread data from the COM port specified by the com_port argument as a bytearray.

    The handler for this API call is SerialServiceReadBytesHandler.

    Args:
        com_port: The number of the COM port from which data should be read. This port must have already been configured,
                  typically via the ConfigureSerialPort test method.

    Returns:
        A bytearray containing the data read from the COM port. This will be empty if there is no unread data.

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        COM port is not configured. A message describing the error is included in the exception.
    """
    
    if com_port is None:
        raise TypeError("com_port must not be None.")
    result = Aguila.ServiceRequest(
        "Serial.ReadBytes",
        json.dumps(
            {
                "ComPort": com_port,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
    return bytearray.fromhex(result.Data)

def ReadString(com_port: int) -> str:
    """Return unread data from the COM port specified by the com_port argument as a string.

    The handler for this API call is SerialServiceReadStringHandler.

    Args:
        com_port: The number of the COM port from which data should be read. This port must have already been configured,
                  typically via the ConfigureSerialPort test method.

    Returns:
        A string containing the data read from the COM port. This will be empty if there is no unread data.

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        COM port is not configured. A message describing the error is included in the exception.
    """

    if com_port is None:
        raise TypeError("com_port must not be None.")
    result = Aguila.ServiceRequest(
        "Serial.ReadString",
        json.dumps(
            {
                "ComPort": com_port,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data

def FindString(com_port: int, reg_ex_pattern: str, timeout: timedelta) -> str:
    """Wait for the regular expression pattern specified by the reg_ex_pattern argument in the data received from the COM port
    specified by the com_port argument.

    The handler for this API call is SerialServiceFindStringHandler.

    Args:
        com_port: The number of the COM port from which data should be read. This port must have already been configured,
                  typically via the ConfigureSerialPort test method.
        reg_ex_pattern: The regular expression pattern to search for in the data received from the COM port.
                  The pattern will be matched in a case-insensitive mode.
        timeout: The maximum amount of time to wait for the pattern to be found. This may not exceed 10 minutes
                  on PPV systems due to DRT service limitations.

    Returns:
        A string containing the data read from the COM port that matches the regular expression pattern.

    Raises:
        Exception: An error or timeout was encountered while handling the request. For instance, the
        COM port is not configured or operation timed out waiting for the regular expression to match
        serial data. A message describing the error is included in the exception.
    """

    if reg_ex_pattern is None:
        raise TypeError("reg_ex_pattern must not be None.")
    if reg_ex_pattern == "":
        raise ValueError("reg_ex_pattern must not be an empty string.")
    if timeout is None:
        raise TypeError("timeout must not be None.")
    if timeout.total_seconds() <= 0:
        raise ValueError("timeout must be greater than 0.")
    if com_port is None:
        raise TypeError("com_port must not be None.")

    result = Aguila.ServiceRequest(
        "Serial.FindString",
        json.dumps(
            {
                "RegExPattern": reg_ex_pattern,
                "TimeoutSeconds": timeout.total_seconds(),
                "ComPort": com_port,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data

def WriteBytes(com_port: int, data: bytearray) -> None:
    """Write byte data to the COM port specified by the com_port argument.

    The handler for this API call is TBD.

    Args:
        com_port: The number of the COM port to which data should be written. This port must have already been configured,
                  typically via the ConfigureSerialPort test method.
        data: A bytearray containing the data to be written to the COM port.

    Returns:
        None

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        COM port is not configured. A message describing the error is included in the exception.
    """

    if com_port is None:
        raise TypeError("com_port must not be None.")
    if data is None:
      raise TypeError("data must not be None.")
    if len(data) == 0:
      raise ValueError("data must not be empty.")
    result = Aguila.ServiceRequest(
        "Serial.WriteBytes",
        json.dumps(
            {
                "ComPort": com_port,
                "DataToWriteHex": data.hex()
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)

def WriteString(com_port: int, data: str) -> None:
    """Write string data to the COM port specified by the com_port argument.

    The handler for this API call is TBD.

    Args:
        com_port: The number of the COM port to which data should be written. This port must have already been configured,
                  typically via the ConfigureSerialPort test method.
        data: A string containing the data to be written to the COM port.

    Returns:
        None

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        COM port is not configured. An message describing the error is included in the exception.
    """

    if com_port is None:
        raise TypeError("com_port must not be None.")
    if data is None:
      raise TypeError("data must not be None.")
    if len(data) == 0:
      raise ValueError("data must not be empty.")
    result = Aguila.ServiceRequest(
        "Serial.WriteString",
        json.dumps(
            {
                "ComPort": com_port,
                "DataToWrite": data
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
