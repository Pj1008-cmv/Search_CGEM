from nest_operation import NestOperation
from nest_operation_status import NestOperationStatus
import scratchpad_register_interface

NEST_MARKER_PROTOCOL_VERSION = 0xD

class ScratchpadRegisterCommunication:
    def update_host_to_target_scratchpad(self, operation, content_list_index = 0, mask_index = 0, content_mask = 0):
        '''
        Writes the provided values to the host_to_target scratchpad register.

        Note that the protocol value in the register is controlled by this class and cannot be specified. 
        Target side batch file would check the protocol version and would return an error if it is not supported.
        
        Parameters
        ----------
        operation : int
            Indicates the operation to be executed by the target side agent
                0 = Abort NEST agent and exit
                1 = Select the set of 3 files to be executed base on the index provide. NEST agent will create Runlist.txt from <index>.txt
                2 = Update Runlist.txt using Runlist.lst, Runlist.msk and downloaded Mask (Multiple Step Operation). Updates should always be in relation to original .msk and .lst files.
                3 = Setup complete and run list. Run previously created Runlist.txt
        content_list_index : int (Specific for Operation 1)
            Index of content list to be executed. Can handle 16,777,216 content lists max.
        mask_index : int (Specific for Operation 2)
            Index into bit mask table. Can handle 256 content lists max.
        content_mask : int (Specific for Operation 2)
            Bit Mask of tests that will go into the list.
        '''

        '''
        Bits 0:3 - Operation
        Bits 4:27 - Operation Specific
            Operation 0: Not Used
            Operation 1: Content List Index
            Operation 2: 
                Bits 4:11 - Mask Index
                Bits 12: 27 - Content Mask
            Operation 3: Not Used
        Bits 28:31 - NEST Marker and Protocol Version
        '''
        if operation < 0 or operation > 3:
            raise ValueError('The operation value must be between 0 and 3. The value {} is not valid.'.format(operation))

        operation_specific = 0
        if operation == 1:
            if content_list_index < 0 or content_list_index > 16777215:
                raise ValueError('The content list index value must be between 0 and 16777215. The value {} is not valid.'.format(content_list_index))
            operation_specific = content_list_index
        elif operation == 2:
            if mask_index < 0 or mask_index > 255:
                raise ValueError('The mask index value must be between 0 and 255. The value {} is not valid.'.format(mask_index))
            operation_specific = mask_index | (content_mask << 8)

        register_value = operation | (operation_specific << 4) | (NEST_MARKER_PROTOCOL_VERSION << 28)
        
        print('Values writing to target_to_host scratchpad:')
        self.__print_host_to_target_scratchpad(register_value, operation, content_list_index, mask_index, content_mask, NEST_MARKER_PROTOCOL_VERSION)

        scratchpad_register_interface.write_host_to_target_scratchpad(register_value)

    def get_values_from_host_to_target_scratchpad(self, print_read_values = True):
        '''
        Reads the host_to_target scratchpad and parse out the data.
        
        Parameters
        ----------
        print_read_values : bool
            Indicates if the read values should be printed to standard out.

        Returns
        -------
        data : tuple(int, int, int, int)
            operation: int
                0 = Abort NEST agent and exit
                1 = Select the set of 3 files to be executed base on the index provide. NEST agent will create Runlist.txt from <index>.txt
                2 = Update Runlist.txt using Runlist.lst, Runlist.msk and downloaded Mask (Multiple Step Operation). Updates should always be in relation to original .msk and .lst files.
                3 = Setup complete and run list. Run previously created Runlist.txt
            content_list_index: int (Specific for Operation 1)
                Index of content list to be executed. Can handle 16,777,216 content lists max.
            mask_index: int (Specific for Operation 2)
                Index into bit mask table. Can handle 256 content lists max.
            content_mask: int (Specific for Operation 2)
                Bit Mask of tests that will go into the list.
            protocol: int 
                Target side batch file would check the protocol version and would return an error if it is not supported.
        '''

        '''
        Bits 0:3 - Operation
        Bits 4:27 - Operation Specific
            Operation 0: Not Used
            Operation 1: Content List Index
            Operation 2: 
                Bits 4:11 - Mask Index
                Bits 12: 27 - Content Mask
            Operation 3: Not Used
        Bits 28:31 - NEST Marker and Protocol Version
        '''
        register_value = scratchpad_register_interface.read_host_to_target_scratchpad()

        operation = register_value & self.__get_bit_mask(4)
        operation_specific = (register_value >> 4) & self.__get_bit_mask(24)
        content_list_index = 0
        mask_index = 0
        content_mask = 0
        if operation == 1:
            content_list_index = operation_specific
        elif operation == 2:
            mask_index = (operation_specific) & self.__get_bit_mask(8)
            content_mask = (operation_specific >> 8) & self.__get_bit_mask(16)
        protocol = (register_value >> 28) & self.__get_bit_mask(4)

        if print_read_values:
            print('Values parsed from host_to_target scratchpad:')
            self.__print_host_to_target_scratchpad(register_value, operation, content_list_index, mask_index, content_mask, protocol)

        return operation, content_list_index, mask_index, content_mask, protocol

    def copy_scratchpad1_to_scratchpad3(self):
        '''
        Copies the values from scratchpad1 to scratchpad3. This is used by the agent similator to indicate
        that it has received the instructions from the host.
        '''
        scratchpad1 = scratchpad_register_interface.read_host_to_target_scratchpad()
        scratchpad_register_interface.write_to_target_working_scratchpad(scratchpad1)

    def scratchpad1_match_scratchpad3(self):
        '''
        Determines if the value in scratchpad1 matches the value in scratchpad3. This will indicate that the agent
        has received the instructions from the host.

        Returns
        -------
        is_match : bool
        True if the two scratchpads match, else False.
        '''
        scratchpad1 = scratchpad_register_interface.read_host_to_target_scratchpad()
        scratchpad3 = scratchpad_register_interface.read_from_target_working_scratchpad()
        return scratchpad1 == scratchpad3

    def clear_scratchpad1(self):
        '''
        Clear the scratchpad1.
        '''
        scratchpad_register_interface.write_host_to_target_scratchpad(0x0)

    def clear_scratchpad2(self):
        '''
        Clear the scratchpad2.
        '''
        scratchpad_register_interface.write_target_to_host_scratchpad(0x0)

    def clear_scratchpad3(self):
        '''
        Clear the scratchpad3.
        '''
        scratchpad_register_interface.write_to_target_working_scratchpad(0x0)
        
    def get_values_from_target_to_host_scratchpad(self, print_read_values = True):
        '''
        Reads the host_to_target scratchpad and parse out the data.

        Parameters
        ----------
        print_read_values : bool
            Indicates if the read values should be printed to standard out.

        Returns
        -------
        data : tuple(int, int, int)
            status: int
                Indicates the status of the target side agent
                    0 = Not started
                    1 = Running
                    2 = Operation Finished And Passed
                    3 = Operation Finished And Failed
                    4 = Operation Error
            content index: int
                Index of the content.
            protocol: int
                NEST Marker and Protocol Version
        '''
        
        '''
        Bits 0:7 - Status 
            0 = Not started
            1 = Running
            2 = Operation Finished And Passed
            3 = Operation Finished And Failed
            4 = Operation Error
        Bits 8:27 - Content Index
        Bits 28:31 - NEST Marker and Protocol Version
        '''
        register_value = scratchpad_register_interface.read_from_target_to_host_scratchpad()
        status = register_value & self.__get_bit_mask(8)
        content_index = (register_value >> 8) & self.__get_bit_mask(16)
        protocol = (register_value >> 28) & self.__get_bit_mask(4)

        if print_read_values:
            print('Values parsed from target_to_host scratchpad:')
            self.__print_from_target_to_host_scratchpad(register_value, status, content_index, protocol)

        return status, content_index, protocol

    def __print_host_to_target_scratchpad(self, register_value, operation, content_list_index, mask_index, content_mask, protocol):
        print('\traw value: 0x{0:0{1}X}'.format(register_value, 8))
        print('\toperation: {} - {}'.format(NestOperation(operation).value, NestOperation(operation).name))
        if operation == 1:
            print('\tcontent_list_index: {}'.format(content_list_index))
        elif operation == 2:
            print('\tmask_index: {}'.format(mask_index))
            print('\tcontent_mask: 0x{0:0{1}X}'.format(content_mask, 4))
        print('\tprotocol: 0x{0:0{1}X}'.format(protocol, 1))

    def __print_from_target_to_host_scratchpad(self, register_value, status, content_index, protocol):
        print('\traw value: 0x{0:0{1}X}'.format(register_value, 8))
        print('\tstatus: {} - {}'.format(NestOperationStatus(status).value, NestOperationStatus(status).name))
        print('\tcontent_index: {}'.format(content_index))
        print('\tprotocol: 0x{0:0{1}X}'.format(protocol, 1))

    def __get_bit_mask(self, num_of_bits):
        return ~(-1 << num_of_bits)
