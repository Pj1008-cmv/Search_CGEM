import statistics
import sys
import threading
import time
from collections import defaultdict

# imports, local
if (toplevel:=r'C:\TestPrograms\applications.validation.circuit-margin.tpdev.aguila.meteorlake-tp\datacollection_python_rework') not in sys.path:
    sys.path.append(toplevel)
import generic_product.utilities.logger as logger

class ProfilingRunner():

    THREAD_ITERATION_DELAY = 0.01

    def __init__(self):
        self.thread_running = False
        self.worker_thread = None
        self.raw_data = defaultdict(list)

    def start_profiling(self, raw_data_point_fns: list):
        self.raw_data.clear()  # discard data from dictionary
        print("Starting Profiling")
        # print("DEBUG:MITCH: Starting Profiling", flush=True)
        # print("Is my code being registered?")
        # print("raw_data_point_fns" + str(raw_data_point_fns))        
        self.thread_running = True
        self.worker_thread = threading.Thread(
            name = "profiling_worker",
            target = self._monitor_worker,
            args = [raw_data_point_fns]
        )
        # print("Is thread_start being called??", flush=True)        
        self.worker_thread.start()
        print("starting worker thread")

    def _monitor_worker(self, raw_data_point_fns: list):
        print("Is monitor worker being called?", flush=True)        
        while self.thread_running:
            print("Is while loop being called?", flush=True)            
            for fn in raw_data_point_fns:
                print("HSIN TESTING: " + str(raw_data_point_fns))
                print("HSIN TESTING: " + str(fn))                
                key = f'{fn.__module__}.{fn.__name__}'
                raw_data_pt = fn()
                self.raw_data[key].append(raw_data_pt)
                # print raw data point to log
                print(f'{key}: {raw_data_pt}', flush=True)
                logger.info(f'{key}: {raw_data_pt}')
                # print raw data point to ITUFF?  TODO
            # time.sleep(self.THREAD_ITERATION_DELAY)

    def stop_profiling(self):
        # print("DEBUG:MITCH: Stop Profiling", flush=True)
        print("Stopping Profiling")
        self.thread_running = False
        time.sleep(self.THREAD_ITERATION_DELAY*1.5)
        self.worker_thread.join()
        self.print_summary_statistics()

    def print_summary_statistics(self):
        # print("DEBUG:MITCH: Profiling Statistics", flush=True)
        print("Profiling Statistics")
        for profiled_cond, raw_data in self.raw_data.items():
            if raw_data == []:
                # print("DEBUG:MITCH: No profiled data", flush=True)
                logger.warning(f'No profiled data for condition {profiled_cond}')
                continue
            # calculate summary statistics
            # print("DEBUG:MITCH: Profiling Statistics For Loop", flush=True)
            profiled_max = max(raw_data)
            profiled_min = min(raw_data)
            profiled_avg = statistics.mean(raw_data)
            profiled_count = len(raw_data)
            profiled_stdev = statistics.stdev(raw_data) if len(raw_data) >= 2 else 0
            # print to log
            # logger.info(f'Profiled data summary statistics: {profiled_cond}')
            print(f'Profiled data summary statistics: {profiled_cond}')
            # logger.info(f'        {profiled_max=}')
            print("Profile Max :", profiled_max)
            # logger.info(f'        {profiled_min=}')
            print("Profile Min :", profiled_min)
            # logger.info(f'        {profiled_avg=}')
            print("Profile Avg :", profiled_avg)
            # logger.info(f'        {profiled_count=}')
            # print("Profile Count :", profiled_count)
            # logger.info(f'        {profiled_stdev=}')
            # print("Profile Std Dev :", profiled_stdev)
            # print to ITUFF? TODO
        # print("DEUG:MITCH: Outside For loop in statistics", flush=True)

if __name__ == '__main__':
    print('finished import')
