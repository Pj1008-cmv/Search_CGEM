import json
from types import SimpleNamespace

import grpc
import PythonAPI_pb2
import PythonAPI_pb2_grpc


class PythonApiResponse:
    """An object representing the JSON payload returned by PythonApiGrpcService.

    Attributes:
        api_name: The name of the API that returned this response.
        success: A boolean indicating whether or not the API call was successful.
        data: The data returned by a successful API call.
        error: An error message explaining why the API call failed if success is
            False. Otherwise, None.
    """

    def __init__(self, api_name: str, success: bool):
        self.api_name = api_name
        self.success = success
        self.data = None
        self.error = None


_channel = None


def ServiceRequest(name: str, payload: str) -> PythonApiResponse:
    """Handles a request to the Python API.

    Handles a Python API request by invoking PythonApiGrpcService.ServiceRequest
    through a gRPC connection.

    Args:
        name: The name of the API to be invoked.
        payload: The request payload to provide to the API.

    Returns:
        A PythonApiResponse
    """

    global _channel

    if _channel is None:
        _channel = grpc.insecure_channel("localhost:54802")
    stub = PythonAPI_pb2_grpc.PythonApiServiceStub(_channel)
    response = stub.ServiceRequest(
        PythonAPI_pb2.PythonApiRequest(apiName=name, jsonPayload=payload)
    )

    # Convert JSON object into a Python object
    return json.loads(
        response.jsonPayload, object_hook=lambda d: SimpleNamespace(**d)
    )
