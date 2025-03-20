from enum import Enum

'''
The NEST operation status enum contains the status of operation that the NEST agent use to communicate the operation progress and result.
'''

class NestOperationStatus(int, Enum):
    NOT_STARTED = 0,
    RUNNING = 1,
    OPERATION_FINISHED_AND_PASSED = 2,
    OPERATION_FINISHED_AND_FAILED = 3,
    OPERATION_ERROR = 4
