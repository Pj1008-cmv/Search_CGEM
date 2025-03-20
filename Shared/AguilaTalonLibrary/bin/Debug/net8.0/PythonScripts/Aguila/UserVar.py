import json
import Aguila

def GetUserVar(user_var_name: str):
    """Return the value of the user variable specified by the user_var_name argument.

    The handler for this API call is UserVarReadHandler.

    Args:
        user_var_name: The full name of the UserVar (e.g. Module1::ModUserVars.Var1)

    Returns:
        The value of the specified user var full name.

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        variable doesn't exist, etc., will be returned by the handler.  This information
        is included in the exception.
    """

    if user_var_name is None:
        raise TypeError("UserVarName must not be None.")
    result = Aguila.ServiceRequest(
        "UserVar.Read",
        json.dumps(
            {
                "UserVarFullName": user_var_name,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
    return result.Data

def SetUserVar(user_var_name: str, user_var_value: object):
    """Sets the value specified by the user_var_value argument to the user variable specified by the user_var_name argument.

    The handler for this API call is UserVarReadHandler.

    Args:
        user_var_name: The full name of the UserVar (e.g. Module1::ModUserVars.Var1)
        user_var_value: The UserVar value to be set

    Returns:
        None

    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        variable doesn't exist, etc., will be returned by the handler.  This information
        is included in the exception.
    """

    if user_var_name is None:
        raise TypeError("UserVarName must not be None.")
    
    if user_var_value is None:
        raise TypeError("UserVarValue must not be None.")

    result = Aguila.ServiceRequest(
        "UserVar.Write",
        json.dumps(
            {
                "UserVarFullName": user_var_name,
                "UserVarValue": user_var_value,
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
