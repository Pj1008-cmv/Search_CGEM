import threading 
import ctypes
import logging
   
class StoppableThread(threading.Thread): 
    def __init__(self, target, args, name): 
        threading.Thread.__init__(self, target=target, args=args, name=name) 

    def get_id(self): 
  
        # returns id of the respective thread 
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
   
    def stop(self): 
        thread_id = self.get_id() 
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
            logging.error('Exception raise failure') 