import ctypes
import threading

'''
Timeout class that raise a TimeoutError when time has expired.
'''

class Timeout():
	def __init__(self, timeout, exception = TimeoutError):
		self._exception = exception
		self._caller_thread = threading.current_thread()
		self._timeout = timeout
		self._timer = threading.Timer(self._timeout, self.raise_caller)
		self._timer.daemon = True
		self._timer.start()

	def __enter__(self):
		try:
			yield
		finally:
			self._timer.cancel()
		return self

	def __exit__(self, type, value, traceback):
		self._timer.cancel()
		
	def raise_caller(self):
		ret = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self._caller_thread._ident), ctypes.py_object(self._exception))
		if ret == 0:
			raise ValueError("Invalid thread ID")
		elif ret > 1:
			ctypes.pythonapi.PyThreadState_SetAsyncExc(self._caller_thread._ident, None)
			raise SystemError("PyThreadState_SetAsyncExc failed")
