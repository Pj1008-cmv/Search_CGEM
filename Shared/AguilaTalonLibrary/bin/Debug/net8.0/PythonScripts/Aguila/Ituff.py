import json
from enum import Enum

import Aguila


class TokenUnit(str, Enum):
    STR = "str",
    BINARY = "binary",
    HEX = "hex",
    NUM = "num"


class TokenLevel(str, Enum):
    LEVEL_0 = "level0",
    LEVEL_2 = "level2"


class TokenSocket(str, Enum):
    SOCKET_1 = "socket1",
    SOCKET_2 = "socket2",
    ALL      = "all"


def WriteToken(
    token_name: str,
    token_value: str,
    unit: TokenUnit = None,
    level: TokenLevel = None,
    include_test_sequence_number = True,
    socket: TokenSocket = None,
) -> str:
    """Logs an ITUFF token value to the ITUFF log file.

    Logs to ITUFF using the provided token name and value, formatted according
    to the provided unit and level. To support DUT-DUT testing strategy, the token
    can be written to a specific DUT if required.

    The handler for this API call is ItuffWriteTokenHandler.

    Args:
        token_name: The ITUFF TNAME under which to log the given value.
        token_value: The token value to log.
        unit: An optional measurement unit for the token data/value. Use 'bin'
            or 'hex' to log integer values as binary or hexadecimal tokens,
            respectively. Use 'num' to log integer value as mrslt. None will log
            value as string/strgval.
        level:An optional parameter for the level of the log message.  0, 2 or
            None are the only levels allowed. None defaults to level 2.
        include_test_sequence_number: A boolean flag to include the test sequence number 
            prepended to the tname. Example with it included: 2_tname_85_MyTestName. 
            Example without it included: 2_tname_MyTestName.  It is by default True so python
            based messages are consistent with TM bases messages.
        socket: An optional parameter to support the DUT-DUT testing strategy and represents the socket
            of the DUT to write the ITUFF token to, either TokenSocket.SOCKET_1, TokenSocket.SOCKET_2
            or TokenSocket.ALL (both TokenSocket.SOCKET_1 and TokenSocket.SOCKET_2).  None will
            result in the token being logged to all DUTs.

    Returns:
        The output written to ITUFF.

    Raises:
        TypeError: An argument with the wrong type was provided.
        Exception: An error was encountered while handling the request.
    """

    if not isinstance(token_name, str):
        raise TypeError("TokenName must be a string.")
    if not isinstance(token_value, str):
        raise TypeError("TokenValue must be a string.")
    if unit is not None and not isinstance(unit, TokenUnit):
        raise TypeError("Unit must be a TokenUnit.")
    if level is not None and not isinstance(level, TokenLevel):
        raise TypeError("Level must be a TokenLevel.")
    if socket is not None and not isinstance(socket, TokenSocket):
        raise TypeError("Socket must be a TokenSocket.")
    result = Aguila.ServiceRequest(
        "Ituff.WriteToken",
        json.dumps(
            {
                "TokenName": token_name,
                "TokenValue": token_value,
                "Unit": unit,
                "Level": level,
                "IncludeTestSequenceNumber": include_test_sequence_number,
                "Socket": socket,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data


def WriteUDDTokens(
    token_name: str,
    identifier_name: str,
    udd_values: list,
    delimiter: str = ',',
    level: TokenLevel = None,
    socket: TokenSocket = None,
) -> str:
    """
    Logs data to ITUFF using a UDD type providing a token name, UDD identifier name, list of data strings
    and a delimiter at the provided level.  To support DUT-DUT testing strategy, the token can be written
    to a specific DUT if required.

    The handler for this API call is ItuffWriteUDDTokensHandler.

    Args:
        token_name: The ITUFF TNAME under which to log the given value.
        identifier_name: The identifier name of the UDD Type.
        udd_values: A list of string data items.  There must be the same number of data items as
            there are columns in the UDD Type definition.
        delimiter:  A string containing a single character to be used as a delimiter.
        level:An optional parameter for the level of the log message.  0, 2 or
            None are the only levels allowed. None defaults to level 2.
        socket: An optional parameter to support the DUT-DUT testing strategy and represents the socket
            of the DUT to write the ITUFF token to, either TokenSocket.SOCKET_1, TokenSocket.SOCKET_2
            or TokenSocket.ALL (both TokenSocket.SOCKET_1 and TokenSocket.SOCKET_2).  None will
            result in the token being logged to all DUTs.

    Returns:
        The output written to ITUFF.

    Raises:
        TypeError: An argument with the wrong type was provided.
        Exception: An error was encountered while handling the request.

    """
    
    if not isinstance(token_name, str):
        raise TypeError("TokenName must be a string.")
    if not isinstance(identifier_name, str):
        raise TypeError("IdentifierName must be a string.")
    if not isinstance(udd_values, list):
        raise TypeError("UddValues must be a list of string.")
    if not isinstance(delimiter, str) or len(delimiter) != 1:
        raise TypeError("Delimiter must be a string of one character length.")
    if level is not None and not isinstance(level, TokenLevel):
        raise TypeError("Level must be a TokenLevel.")
    if socket is not None and not isinstance(socket, TokenSocket):
        raise TypeError("Socket must be a TokenSocket.")
    result = Aguila.ServiceRequest(
        "Ituff.WriteUDDTokens",
        json.dumps(
            {
                "TokenName": token_name,
                "IdentifierName" : identifier_name,
                "UddValues" : udd_values,
                "Delimiter" : delimiter,
                "Level": level,
                "Socket": socket,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data


def WriteMetaDataTokens(
    token_name: str,
    meta_data_definition: str,
    meta_data_values: str,
    level: TokenLevel = None,
    socket: TokenSocket = None,
) -> str:
    """
    Logs data to ITUFF using the methodology defined in the String-Parsing Metadata Reference.
    The _meta_data_values_ will be validated against the _meta_data_definition_ provided.  To support DUT-DUT
    testing strategy, the token can be written to a specific DUT if required.

    The handler for this API call is ItuffWriteMetaDataTokensHandler.

    Args:
        token_name: The ITUFF TNAME under which to log the given value.
        meta_data_definition: The meta-data definition.  If a UDD type is used in the definition,
            the name will be validated with the UDD types defined using the LotStart test method.
            They will have been registered with the DatalogService.
        meta_data_values: The meta-data in the JSON format that conforms to the meta data definition.
        level:An optional parameter for the level of the log message.  0, 2 or
            None are the only levels allowed. None defaults to level 2.
        socket: An optional parameter to support the DUT-DUT testing strategy and represents the socket
            of the DUT to write the ITUFF token to, either TokenSocket.SOCKET_1, TokenSocket.SOCKET_2
            or TokenSocket.ALL (both TokenSocket.SOCKET_1 and TokenSocket.SOCKET_2).  None will
            result in the token being logged to all DUTs.
    Returns:
        The output written to ITUFF.

    Raises:
        TypeError: An argument with the wrong type was provided.
        Exception: An error was encountered while handling the request.
    """
    
    if not isinstance(token_name, str):
        raise TypeError("TokenName must be a string.")
    if not isinstance(meta_data_definition, str):
        raise TypeError("MetaDataDefinitionString must be a string.")
    if not isinstance(meta_data_values, str):
        raise TypeError("MetaDataValues must be a string.")
    if level is not None and not isinstance(level, TokenLevel):
        raise TypeError("Level must be a TokenLevel.")
    if socket is not None and not isinstance(socket, TokenSocket):
        raise TypeError("Socket must be a TokenSocket.")
    result = Aguila.ServiceRequest(
        "Ituff.WriteMetaDataTokens",
        json.dumps(
            {
                "TokenName": token_name,
                "MetaDataDefinitionString" : meta_data_definition,
                "MetaDataValues" : meta_data_values,
                "Level": level,
                "Socket": socket,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data


