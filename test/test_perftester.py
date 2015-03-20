from nose.tools import *
from logparser.perftester import PerformanceTester
import time

def test_performance_tester():
    perf_tester = PerformanceTester()

    sleeps = [0.0, 0.1]
    @perf_tester.test
    def test_fn1():
        time.sleep(sleeps.pop(0))

    @perf_tester.test
    def test_fn2():
        pass

    # 1st call
    test_fn1()
    
    results = perf_tester.results()
    assert_equal(['test_fn1'], results.keys())
    result = results['test_fn1']
    assert_equal(1, result['num_samples'])
    assert_equal(result['min_time'], result['max_time'])
    assert_equal(result['min_time'], result['avg_time'])

    # 2nd call
    test_fn1()

    result = perf_tester.results()['test_fn1']
    assert_equal(2, result['num_samples'])
    assert_not_equal(result['min_time'], result['max_time'])
    # assert_almost_equal?
    assert_equal(result['avg_time'],
                 (result['min_time'] + result['max_time']) / 2.0)

    # other function call
    test_fn2()

    # both stats should be present
    assert_true('test_fn1' in perf_tester.results())
    assert_true('test_fn2' in perf_tester.results())
