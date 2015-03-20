from functools import wraps
from datetime import datetime
import gc

class PerformanceTester(object):
    """Tool to measure run time of functions. Use PerformanceTester.test
    function as a decorator to collect performance data"""

    def __init__(self):
        self.stats = {}

    def test(self, f):
        """Decorator to be used on a function under test.
        Collects run time data"""

        @wraps(f)
        def wrapper(*args, **kwds):
            # garbage collection off to prevent from spikes in data
            # copied from timeit module
            gc_state = gc.isenabled()
            gc.disable()
            try:
                start = datetime.now()
                result = f(*args, **kwds)
                end = datetime.now()

                seconds_elapsed = (end - start).total_seconds()
                self.stats.setdefault(f.__name__, []).append(seconds_elapsed)
            finally:
                if gc_state:
                    gc.enable()
            return result

        return wrapper

    def results(self):
        """Aggregates results of tests performed"""
        aggregated = {}
        for func_name, run_times in self.stats.iteritems():
            num_samples = len(run_times)
            min_time = min(run_times)
            max_time = max(run_times)
            avg_time = sum(run_times)/float(num_samples)
            aggregated[func_name] = {
                'num_samples': num_samples,
                'min_time': min_time,
                'max_time': max_time,
                'avg_time': avg_time,
            }
        return aggregated

    def print_results(self):
        """Prints results of test performed"""
        form = ("Function: %s\nNum samples: %d\nMin: %0.20f secs\n"
                   "Max: %0.20f secs\nAverage: %0.20f secs")

        for func_name, result in self.results().iteritems():
            print form % (func_name,
                          result['num_samples'],
                          round(result['min_time'], 2),
                          round(result['max_time'], 2),
                          round(result['avg_time'], 2))
