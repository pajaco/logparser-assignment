# logparser-assignment
Assignment given to me as part of recruitment process

# Spec

Example log entries:
```
 2012-09-13 16:04:22 DEBUG SID:34523 BID:1329 RID:65d33 'Starting new session'
 2012-09-13 16:04:30 DEBUG SID:34523 BID:1329 RID:54f22 'Authenticating User'
 2012-09-13 16:05:30 DEBUG SID:42111 BID:319 RID:65a23 'Starting new session'
 2012-09-13 16:04:50 ERROR SID:34523 BID:1329 RID:54ff3 'Missing
Authentication token'
 2012-09-13 16:05:31 DEBUG SID:42111 BID:319 RID:86472 'Authenticating User'
 2012-09-13 16:05:31 DEBUG SID:42111 BID:319 RID:7a323 'Deleting asset
with ID 543234'
 2012-09-13 16:05:32 WARN SID:42111 BID:319 RID:7a323 'Invalid asset ID'
```

1) Write a program in the language of your choice that reads the log
entries from a file and stores them in appropriate data structures. The
data should be stored in memory, ie. only use standard in memory data
structures, not an external database. We would like to see
demonstrations of good practice: e.g. good variable and function naming,
code documentation and unit tests.

2) Using the code from (1) write functions that:

* returns all log lines with a given log level
* returns all log lines belonging to a given business
* returns all log lines for a given session id
* returns all log lines within a given date range

3) Write a profiling class that can be used to collect basic performance
statistics about different functions. The class should calculate the
time taken for a function to execute. The class should store the
execution times for each decorated function in a dictionary and
calculate the maximum, minimum and average execution times. At the end
of a profiling run print out a test report for the profiled functions.

Example output:
```
  Function: getLogLevel
  NumSamples: 12
  Min: 0.02 secs
  Max: 0.34 secs
  Average: 0.09 secs
```
