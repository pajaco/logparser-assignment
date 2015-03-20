from logparser.logparser import (CustomLog,
                                 find_entries_with_log_level,
                                 find_entries_with_business_id,
                                 find_entries_with_session_id,
                                 find_entries_within_date_range)
from logparser.perftester import PerformanceTester
from cStringIO import StringIO

log_sample = """
2012-09-13 16:04:22 DEBUG SID:34523 BID:1329 RID:65d33 'Starting new session'
2012-09-13 16:04:30 DEBUG SID:34523 BID:1329 RID:54f22 'Authenticating User'
2012-09-13 16:05:30 DEBUG SID:42111 BID:319 RID:65a23 'Starting new session'
2012-09-13 16:04:50 ERROR SID:34523 BID:1329 RID:54ff3 'Missing
Authentication token'
2012-09-13 16:05:31 DEBUG SID:42111 BID:319 RID:86472 'Authenticating User'
2012-09-13 16:05:31 DEBUG SID:42111 BID:319 RID:7a323 'Deleting asset
with ID 543234'
2012-09-13 16:05:32 WARN SID:42111 BID:319 RID:7a323 'Invalid asset ID'
"""
log_sample = log_sample * 20000

perf_tester = PerformanceTester()

log_container = CustomLog()
# wrap with tester
find_entries_with_log_level = perf_tester.test(find_entries_with_log_level)
find_entries_with_business_id = perf_tester.test(find_entries_with_business_id)
find_entries_with_session_id = perf_tester.test(find_entries_with_session_id)
find_entries_within_date_range = perf_tester.test(find_entries_within_date_range)
load = perf_tester.test(log_container.load)

load(StringIO(log_sample))

for _ in range(10):
    find_entries_with_log_level(log_container, 'DEBUG')
    find_entries_with_log_level(log_container, 'ERROR')
    find_entries_with_log_level(log_container, 'WARN')

    find_entries_with_business_id(log_container, 'BID:1329')
    find_entries_with_business_id(log_container, 'BID:319')

    find_entries_with_session_id(log_container, 'SID:34523')
    find_entries_with_session_id(log_container, 'SID:42111')

    find_entries_within_date_range(log_container,
                                   '2012-09-13 16:04:22',
                                   '2012-09-13 16:05:30')
    find_entries_within_date_range(log_container,
                                   '2012-09-13 16:04:50',
                                   '2012-09-13 16:05:32')

perf_tester.print_results()
