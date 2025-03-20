import time
from datetime import datetime
from nest_operation import NestOperation
from nest_operation_status import NestOperationStatus
from scratchpad_register_communication import *

class NestClientOperations(ScratchpadRegisterCommunication):
    stop_waiting = False

    def abort(self):
        '''
        Abort NEST agent and exit.
        '''
        self.__start_operation(NestOperation.ABORT)

    def stop_operation(self):
        self.stop_waiting = True

    def select_list(self, content_list_index: int):
        '''
        Select a new active content list.
        
        Parameters
        ----------
        content_list_index : int
            Index of content list to be executed.
        '''
        self.__start_operation(NestOperation.SELECT_LIST, content_list_index)

    def update_mask(self, batch_mask_updates: dict):
        '''
        Update the content list mask if batch_mask_updates param is not null.
        
        Parameters
        ----------
        batch_mask_updates : dict
            Dictionary of all batch mask updates where:
            * Key = Index into bit mask table.
            * Value = Bit Mask of tests that will go into the list.
        '''
        for mask_index, content_mask in batch_mask_updates.items():
            self.__start_operation(NestOperation.UPDATE_MASK, 0, mask_index, content_mask)

    def run_list(self):
        '''
        Run the current content list.
        '''
        print('Clearing target_to_host scratchpad.')
        self.clear_scratchpad2()
        self.__start_operation(NestOperation.RUN_LIST)

    def wait_for_batch_completion(self):
        '''
        Wait for the batch to complete by monitoring the target_to_host scratchpad register.
        '''
        self.stop_waiting = False
        running = False
        previous_content_index = -1
                
        print('Waiting for target to complete the batch execution.')
        try:
            while not self.stop_waiting:
                # Read target to host scratchpad
                status, content_index, protocol = self.get_values_from_target_to_host_scratchpad(False)

                # Do nothing. Empty value (0x00000000) in target to host scratchpad
                if status == content_index == protocol == 0:
                    continue

                # Confirm valid protocol version before processing
                if protocol != NEST_MARKER_PROTOCOL_VERSION:
                    raise RuntimeError('The target agent returned a protocol version of 0x{0:0{1}X} which is not supported by NEST.'.format(protocol, 1))
                    
                if status == NestOperationStatus.NOT_STARTED:
                    if previous_content_index < content_index:
                        self.__print_operation_status(NestOperationStatus(status).name)                    
                        running = False
                        previous_content_index = content_index

                elif status == NestOperationStatus.RUNNING:
                    if not running or previous_content_index < content_index:
                        self.__print_operation_status(NestOperationStatus(status).name, content_index)
                        running = True
                        previous_content_index = content_index

                elif status == NestOperationStatus.OPERATION_FINISHED_AND_PASSED:
                    self.__print_operation_status(NestOperationStatus(status).name, content_index)
                    return

                elif status == NestOperationStatus.OPERATION_FINISHED_AND_FAILED:
                    self.__print_operation_status(NestOperationStatus(status).name, content_index)
                    return

                elif status == NestOperationStatus.OPERATION_ERROR:
                    self.__print_operation_status(NestOperationStatus(status).name, content_index)
                    return

                else:
                    self.__print_operation_status('UNDEFINED', content_index)
                    raise RuntimeError('The target agent returned a status of {} which is not supported by NEST.'.format(status))

                # Sleep for a short time before checking the register again.
                time.sleep(.01)
        finally:
            self.stop_waiting = False

    def __start_operation(self, operation: int, content_list_index: int = 0, mask_index: int = 0, content_mask: int = 0):
        '''
        Start a NEST operation
        Clear SCR1. Then Clear SCR3.
        Write SCR1 = Register containing the operation data to be started.
        Wait for SCR1 == SCR3. /// Wait for acknowledgement of the operation.
        Clear SCR1. Then Clear SCR3.
        
        Parameters
        ----------
        operation : int
            Operation to run.
        content_list_index : int (Specific for Operation 1)
            Index of content list to be executed.
        mask_index : int (Specific for Operation 2)
            Index into bit mask table.
        content_mask : int (Specific for Operation 2)
            Bit Mask of tests that will go into the list.
        '''
        print('Before operation, clearing SCR1, then SCR3.')
        self.clear_scratchpad1()
        self.clear_scratchpad3()

        print('Sending operation to target: {} - {}'.format(NestOperation(operation).value, NestOperation(operation).name))
        self.update_host_to_target_scratchpad(operation, content_list_index, mask_index, content_mask)

        print('Waiting for target to acknowledge the operation start.')
        while(not self.scratchpad1_match_scratchpad3()):
            time.sleep(0.01)

        print('After operation, clearing SCR1, then SCR3.')
        self.clear_scratchpad1()
        self.clear_scratchpad3()

    def __print_operation_status(self, operation_status_name: str, content_index: int = None):
        '''
        Print the NEST operation status
        
        Parameters
        ----------
        operation_status_name : int
            Name of the NEST operation status.
        content_list_index : int (Specific for Operation 1)
            Index of content.
        '''
        if content_index is None:
            print('{}::'.format(operation_status_name))
        else:
            current_date_time_iso_format = datetime.now().isoformat()
            print('{}::{}::{}'.format(operation_status_name, content_index, current_date_time_iso_format))
        