from asyncio.windows_events import NULL
from concurrent import futures
from google.protobuf import empty_pb2
import grpc
import winreg
import Python_pb2
import Python_pb2_grpc
import stdout_redirects
import stoppable_thread
import iterable_queue
import traceback
import sys
import threading
import uuid
import os
import time
import logging
import __main__

class InterruptableEvent(threading.Event):
    def wait(self, timeout=None):
        wait = super().wait  # get once, use often
        while not wait(0.01):  pass

evtServerStop = InterruptableEvent()
evtExit = InterruptableEvent()

def setup_logging(enable_logging):
    loggerInstance = logging.getLogger(__name__)
    if enable_logging:
        loggerInstance.setLevel(logging.DEBUG)
        scriptPath = os.path.dirname(os.path.realpath(__file__))
        file_handler = logging.FileHandler(os.path.join(scriptPath, 'PythonServer.log'), encoding='utf-8')
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
        file_handler.setFormatter(formatter)
        loggerInstance.addHandler(file_handler)
    else:
        loggerInstance.addHandler(logging.NullHandler())
    return loggerInstance

def log_to_file(loggerInstance, level, message):
    if not isinstance(loggerInstance.handlers[0], logging.NullHandler):
        getattr(loggerInstance, level)(message)

def execute_command(command, token, responseQueue, locals, loggerInstance):
    try:
        stdout_redirects.redirect(token, responseQueue)
        try:
            try:
                command_to_eval = compile(command, "<stdin>", "eval", dont_inherit=True)
            except:
                # try to compile the command for exec instead, as this will
                # handle the case where the command does not return a value
                command_to_eval = compile(command, "<stdin>", "exec", dont_inherit=True)
            result = eval(command_to_eval, locals)
            if result is not None:
                responseQueue.add_response(Python_pb2.PythonResponse(token=token, result=str(result)))
        except Exception:
            print(traceback.format_exc())
            responseQueue.add_response(Python_pb2.PythonResponse(token=token, exception=traceback.format_exc()))

    except Exception as e:
        log_to_file(loggerInstance, 'error', f"Unexpected error in execute_command: {str(e)}")
    finally:
        stdout_redirects.stop_redirect()
        responseQueue.close()

class PythonServiceImpl(Python_pb2_grpc.PythonServiceServicer):

    def __init__(self, loggerInstance):
        self.__dict__.update(globals())
        self.__runningOperations = []
        self.__threadPoolExecutor = futures.ThreadPoolExecutor(max_workers=10)
        self.serverId = uuid.uuid4()
        self.loggerInstance = loggerInstance
        log_to_file(self.loggerInstance, 'info', f"Starting Server with ID [{self.serverId}]")
    
    def __AddRunningOperation(self, token):
        log_to_file(self.loggerInstance, 'info', f"[{token}] Added to running operations.")
        self.__runningOperations.append(token)

    def __RemoveRunningOperation(self, token, isTimeout):
        log_to_file(self.loggerInstance, 'info', f"[{token}] Removed from running operations. Timeout=[{isTimeout}]")
        self.__runningOperations.remove(token)

    def Execute(self, request, context):
        log_to_file(self.loggerInstance, 'info', f"[{request.token}] Received Execute with command: {request.command}, and timeout: {request.timeoutSec} seconds")
        
        try:
            queue = iterable_queue.IterableQueue(request.timeoutSec)
            
            execThread = stoppable_thread.StoppableThread(execute_command, (request.command, request.token, queue, self.__dict__, self.loggerInstance), request.token)
            self.__AddRunningOperation(request.token)
            execThread.start()
           
            isTimeout = False
            try:
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Waiting for response")
                for response in queue:
                    yield response
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Response complete")
            except TimeoutError as e:
                log_to_file(self.loggerInstance, 'error', f"[{request.token}] TimeoutError: {e}")
                isTimeout = True
                execThread.stop()
                log_to_file(self.loggerInstance, 'error', f"[{request.token}] Thread stopped")
                yield Python_pb2.PythonResponse(token=request.token, timeout=str(e))
                log_to_file(self.loggerInstance, 'error', f"[{request.token}] Yielded timeout response")
            finally:
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Removing running operation")
                self.__RemoveRunningOperation(request.token, isTimeout)
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Removed running operation")
        except Exception as e:
            log_to_file(self.loggerInstance, 'error', f"Unhandled exception in Execute: {str(e)}")
    
    def ExecuteNonBlocking(self, request, context):
        self.__AddRunningOperation(request.token)
        self.__threadPoolExecutor.submit(self.ExecuteNonBlockingImpl, request)
        return empty_pb2.Empty()
   
    def RunScript(self, request, context):
        log_to_file(self.loggerInstance, 'info', f"[{request.token}] Received RunScript with file: {request.scriptPath}, and timeout: {request.timeoutSec} seconds")

        try:
            queue = iterable_queue.IterableQueue(request.timeoutSec)
            
            dir_path = os.path.dirname(request.scriptPath)
            if dir_path not in sys.path:
                sys.path.insert(0, dir_path)

            command = f"exec(open(r\"{request.scriptPath}\", 'r', encoding='utf-8-sig').read())"
            execThread = stoppable_thread.StoppableThread(execute_command, (command, request.token, queue, self.__dict__, self.loggerInstance), request.token)
            self.__AddRunningOperation(request.token)
            execThread.start()

            isTimeout = False
            try:
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Waiting for response")
                for response in queue:
                    yield response
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Response complete")
            except TimeoutError as e:
                log_to_file(self.loggerInstance, 'error', f"[{request.token}] TimeoutError: {e}")
                isTimeout = True
                execThread.stop()
                log_to_file(self.loggerInstance, 'error', f"[{request.token}] Thread stopped")
                yield Python_pb2.PythonResponse(token=request.token, timeout=str(e))
                log_to_file(self.loggerInstance, 'error', f"[{request.token}] Yielded timeout response")
            finally:
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Removing running operation")
                self.__RemoveRunningOperation(request.token, isTimeout)
                log_to_file(self.loggerInstance, 'info', f"[{request.token}] Removed running operation")
        except Exception as e:
            log_to_file(self.loggerInstance, 'error', f"Unhandled exception in RunScript: {str(e)}")

    def RunScriptNonBlocking(self, request, context):
        self.__AddRunningOperation(request.token)
        self.__threadPoolExecutor.submit(self.RunScriptNonBlockingImpl, request)
        return empty_pb2.Empty()
    
    def ShutdownServer(self, request, context):
        log_to_file(self.loggerInstance, 'info', "Received ShutdownServer request")
        self.__threadPoolExecutor.shutdown(wait=False)
        evtExit.set()
        evtServerStop.set()
        return empty_pb2.Empty()

    def RestartServer(self, request, context):
        log_to_file(self.loggerInstance, 'info', "Received RestartServer request")
        self.__threadPoolExecutor.shutdown(wait=False)
        evtServerStop.set()
        log_to_file(self.loggerInstance, 'info', "Server restart complete")
        return empty_pb2.Empty()

    def Ping(self, request, context):
        log_to_file(self.loggerInstance, 'info', "Received Ping request")
        return Python_pb2.PingResponse(serverId=str(self.serverId))

    def GetRunningOperations(self, request, context):
        rp = Python_pb2.GetRunningOperationsResponse()
        rp.tokens.extend(self.__runningOperations)
        return rp

    def ExecuteNonBlockingImpl(self, request):
        log_to_file(self.loggerInstance, 'info', f"[{request.token}] Received ExecuteNonBlocking with command: {request.command}, and timeout: {request.timeoutSec} seconds")
        
        isTimeout = False
        try:
            queue = iterable_queue.IterableQueue(request.timeoutSec)
            
            execThread = stoppable_thread.StoppableThread(execute_command, (request.command, request.token, queue, self.__dict__, self.loggerInstance), request.token)
            execThread.start()
            
            try:
                for response in queue:
                    pass # Ignore because client is not awaiting responses
            except TimeoutError as e:
                isTimeout = True
                execThread.stop() # If timeout occurs we cancel the thread. 
        except Exception as e:
            log_to_file(self.loggerInstance, 'error', f"Unhandled exception in ExecuteNonBlocking: {str(e)}")
        finally:
            self.__RemoveRunningOperation(request.token, isTimeout)

    def RunScriptNonBlockingImpl(self, request):
        log_to_file(self.loggerInstance, 'info', f"[{request.token}] Received RunScriptNonBlocking with file: {request.scriptPath}, and timeout: {request.timeoutSec} seconds")

        isTimeout = False
        try:
            queue = iterable_queue.IterableQueue(request.timeoutSec)
            
            dir_path = os.path.dirname(request.scriptPath)
            if dir_path not in sys.path:
                sys.path.insert(0, dir_path)

            command = f"exec(open(r\"{request.scriptPath}\", 'r', encoding='utf-8-sig').read())"
            execThread = stoppable_thread.StoppableThread(execute_command, (command, request.token, queue, self.__dict__, self.loggerInstance), request.token)
            execThread.start()
            
            try:
                for response in queue:
                    pass # Ignore because client is not awaiting responses
            except TimeoutError as e:
                isTimeout = True
                execThread.stop() # If timeout occurs we cancel the thread. 

        except Exception as e:
            log_to_file(self.loggerInstance, 'error', f"Unhandled exception in RunScriptNonBlocking: {str(e)}")
        finally:
            self.__RemoveRunningOperation(request.token, isTimeout)

def StartServer(loggerInstance, max_retries=5, retry_delay=0.1):
    for attempt in range(max_retries):
        try:
            server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=[
                ('grpc.max_send_message_length', -1),
                ('grpc.max_receive_message_length', -1)
            ])
            Python_pb2_grpc.add_PythonServiceServicer_to_server(PythonServiceImpl(loggerInstance), server)
            
            port = server.add_insecure_port('127.0.0.1:0')
            write_port_to_registry(port)
            server.start()
            
            log_to_file(loggerInstance, 'info', f'Server Started on port {port}')
            print(f'Server Started on port {port}')
            sys.stdout.flush()
            return server, port
        except Exception as e:
            if attempt < max_retries - 1:
                log_to_file(loggerInstance, 'warning', f'Failed to start server on attempt {attempt + 1}. Retrying in {retry_delay} seconds...')
                time.sleep(retry_delay)
            else:
                log_to_file(loggerInstance, 'error', f'Failed to start server after {max_retries} attempts.')
                raise e

def write_port_to_registry(port):
    try:
        key_path = r"Software\Intel\Aguila"
        key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS)
        winreg.SetValueEx(key, "PythonServerPort", 0, winreg.REG_SZ, str(port))
        winreg.CloseKey(key)
        print(f"Successfully wrote port {port} to HKCU\\{key_path}")
    except WindowsError as e:
        print(f'Error writing PythonServerPort to registry: {str(e)}')

def StopServer(server, loggerInstance):
    try:
        log_to_file(loggerInstance, 'info', 'Stopping server...')
        server.stop(grace=5)
        server.wait_for_termination(timeout=10)
        log_to_file(loggerInstance, 'info', 'Server stopped successfully')
        print('Server Stopped')
    except Exception as e:
        log_to_file(loggerInstance, 'error', f'Error stopping server: {str(e)}')
        print(f'Error stopping server: {str(e)}')

def main(enable_logging=True):
    aguila_python_logger = setup_logging(enable_logging)
    
    try:
        stdout_redirects.enable_proxy()
 
        while not evtExit.is_set():
            server, port = StartServer(aguila_python_logger)
            evtServerStop.wait()
            evtServerStop.clear()
            StopServer(server, aguila_python_logger)
    except KeyboardInterrupt:
        print('Keyboard Interrupt')
        log_to_file(aguila_python_logger, 'info', 'Keyboard Interrupt')
        StopServer(server, aguila_python_logger)
    except Exception as ex:
        log_to_file(aguila_python_logger, 'error', traceback.format_exc())

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Python Server with optional logging")
    parser.add_argument('--no-log', action='store_true', help="Disable logging")
    args = parser.parse_args()
    main(not args.no_log)