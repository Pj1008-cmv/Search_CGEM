import time
from timeout import Timeout
from nest_client_operations import *

active_nest_client = None

def run_nest(timeoutMs: float, content_list_index: int, batch_mask_updates: dict = None):
  '''
  Starts a new NEST batch.

  Parameters
        ----------
        timeoutMs : float
            Number of milliseconds to expire after the start time.
        content_list_index : int        
            Index of the content group which have the contents to be run by the Nest agent.
            If content_list_index < 0 then run batch for the current selected content list.
        batch_mask_updates : dictionary
            Dictionary containing the batch mask updates of the content objects with Enabled statuses that are different than as it was during GenerateBatchingFilesOnTarget where:
            * Key = Index into bit mask table.
            * Value = Bit Mask of tests that will go into the list.
  '''
  global active_nest_client
  if active_nest_client is not None:
    raise Exception("A NestClient is already running.")

  active_nest_client = NestClient()
  active_nest_client.run_nest(timeoutMs, content_list_index, batch_mask_updates)
  # Clear active client on completion.
  active_nest_client = None
  
def stop_nest():
  '''
  Stop waiting for messages from any running NEST batch. This function will block until any running
  run_nest(...) call has returned. It will return immediately if there is no batch running.
  '''
  global active_nest_client
 
  if active_nest_client is None:
    return

  active_nest_client.stop_nest()

'''
NEST agent client

The NEST agent is an executable that is run from the EFI console. Typically it uses MerlinX to execute content.
For details on the NEST implementation, see: https://dev.azure.com/MIT-STA/STA_Tools/_wiki/wikis/STA_Tools.wiki/29856/NEST
'''
class NestClient():
    _nestClientOperations = None

    def run_nest(self, timeoutMs: float, content_list_index: int, batch_mask_updates: dict = None):
        '''
        Sends a command to the Nest agent running on the target to run the list with the mask changes provided.

        Parameters
        ----------
        timeoutMs : float
            Number of milliseconds to expire after the start time.
        content_list_index : int        
            Index of the content group which have the contents to be run by the Nest agent.
            If content_list_index < 0 then run batch for the current selected content list.
        batch_mask_updates : dictionary
            Dictionary containing the batch mask updates of the content objects with Enabled statuses that are different than as it was during GenerateBatchingFilesOnTarget where:
            * Key = Index into bit mask table.
            * Value = Bit Mask of tests that will go into the list.
        '''
        
        try:
            with Timeout(timeoutMs / 1000):
                self._nestClientOperations = NestClientOperations()

                # Select the content list indicated into content_list_index param if its greater than or equal to zero
                if content_list_index >= 0:
                    self._nestClientOperations.select_list(content_list_index)
            
                # Update the content list mask if batch_mask_updates param is not null
                if batch_mask_updates is not None:
                    self._nestClientOperations.update_mask(batch_mask_updates)

                # Run the current content list
                self._nestClientOperations.run_list()
                
                # Wait for batch completion
                self._nestClientOperations.wait_for_batch_completion()
        except (ValueError, RuntimeError, TimeoutError) as err:
            print('Error while excuting nest_client.run_nest: {0}'.format(err))
        finally:
          self._nestClientOperations = None
            
    def stop_nest(self):
      '''
      Stops run_nest from waiting for any target-to-host messages, then blocks until run_nest is no
      longer running. It is very important to call this when a NEST batch is aborted without
      completing naturally, otherwise run_nest may be consuming target-to-host messages while
      in another thread disconnected from the test method, corrupting results for the current run.
      '''
      if self._nestClientOperations is None:
        return

      self._nestClientOperations.stop_operation()
      # wait for self.nestClientOpeations to be None indicating run_nest(..) is not running
      while True:
          if self._nestClientOperations is None:
            return
          time.sleep(.005)

