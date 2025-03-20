import json
import Aguila


def GetTestSequenceNumber() -> int:
    """Return the value of the current test sequence number from the TestInstanceService

    The handler for this API call is TestInstanceServiceGetTestSequenceNumberHandler.

    Args:
        None

    Returns:
        The value of the current test sequence number.

    Raises:
        Exception: An error was encountered while handling the request.
    """

    result = Aguila.ServiceRequest(
        "TestInstanceService.GetTestSequenceNumber",
        json.dumps({})
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data


def GetTestInstanceName() -> str:
    """Return the name of the current test instance from the TestInstanceService

    The handler for this API call is TestInstanceServiceGetTestInstanceNameHandler.

    Args:
        None

    Returns:
        The name of the current test instance.

    Raises:
        Exception: An error was encountered while handling the request.
    """

    result = Aguila.ServiceRequest(
        "TestInstanceService.GetTestInstanceName",
        json.dumps({})
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data
