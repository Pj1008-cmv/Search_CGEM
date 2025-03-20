from enum import Enum

'''
The NEST operation enum contains the operations that the NEST agent can perform on the Target machine.
'''

class NestOperation(int, Enum):
    ABORT = 0,
    SELECT_LIST = 1,
    UPDATE_MASK = 2,
    RUN_LIST = 3
