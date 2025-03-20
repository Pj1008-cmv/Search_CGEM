import datetime
import json
import Aguila


def WriteProfileData(timeStamp: datetime.datetime, condition: str, average: float, minimum: float, 
                     maximum: float, standardDeviation: float, sampleCount: int):
    """
    Writes profile data to the profiler.
    
    The handler for this API call is ProfileDataWriteHandler.
    
    Args:
        timeStamp: Time the data was collected. This marks the end of the profile data collection period. The beginning of the period is determined by the time the previous profile data was written.
        condition: The condition of the profile data.
        average: The average of the profile data.
        minimum: The minimum of the profile data.
        maximum: The maximum of the profile data.
        standardDeviation: The standard deviation of the profile data.
        sampleCount: The sample count of the profile data.
        
    Returns: None
    
    Raises:
        Exception: An error was encountered while handling the request. For instance, the
        input data is invalid, etc., will be returned by the handler.
    """
    
    if not isinstance(timeStamp, datetime.datetime):
        raise TypeError("TimeStamp must be a datetime object.")
    if not isinstance(condition, str):
        raise TypeError("Condition must be a string.")
    if not isinstance(average, float):
        raise TypeError("Average must be a float.")
    if not isinstance(minimum, float):
        raise TypeError("Minimum must be a float.")
    if not isinstance(maximum, float):
        raise TypeError("Maximum must be a float.")
    if not isinstance(standardDeviation, float):
        raise TypeError("StandardDeviation must be a float.")
    if not isinstance(sampleCount, int):
        raise TypeError("SampleCount must be an integer.")

    # Convert datetime object to ISO 8601 formatted strings
    timeStamp_iso = timeStamp.isoformat()

    result = Aguila.ServiceRequest(
        "Profiler.Write",
        json.dumps(
            {
                "TimeStamp": timeStamp_iso,
                "Condition": condition,
                "Average": average,
                "Minimum": minimum,
                "Maximum": maximum,
                "StandardDeviation": standardDeviation,
                "SampleCount": sampleCount
            }
        ),
    )

    if not result.Success:
        raise Exception(result.Error)
