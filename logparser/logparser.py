"""
Module provides classes that parse logs as streams and offer search
functionality of log entries.

Logs in the assigmnent have the following format:
DATE LOGLEVEL SESSION-ID BUSINESS-ID REQUEST-ID MSG

Examples:
2012-09-13 16:04:22 DEBUG SID:34523 BID:1329 RID:65d33 'Starting new session'
2012-09-13 16:04:30 DEBUG SID:34523 BID:1329 RID:54f22 'Authenticating User'
2012-09-13 16:05:30 DEBUG SID:42111 BID:319 RID:65a23 'Starting new session'
2012-09-13 16:04:50 ERROR SID:34523 BID:1329 RID:54ff3 'Missing
Authentication token'
2012-09-13 16:05:31 DEBUG SID:42111 BID:319 RID:86472 'Authenticating User'
2012-09-13 16:05:31 DEBUG SID:42111 BID:319 RID:7a323 'Deleting asset
with ID 543234'
2012-09-13 16:05:32 WARN SID:42111 BID:319 RID:7a323 'Invalid asset ID'

Logs may may not necessarily be ordered by date and the message field may
contain unescaped newline chars.

It is assumed that positions of fields in an entry never change
"""

from collections import namedtuple
import bisect
import re
from datetime import datetime
import sys

class LogContainer(object):
    """
    LogContainer stores log entries allows searching for ranges of entries
    based on log field values.

    Usage:

        log_container = LogContainer(['field_a', 'field_b'])

    allows to query for entries on fields 'field_a' and 'field_b':

        log_container.find_by('field_a', 1)

        searches for all entries which field_a has value 1

        log_container.find_by('field_a', 1, 10)

        searches for all entries which field_a has value between 1 and 10
        (boundary values included)

    Class provides access to a list of its entries, eg:

        for entry in log_container.entries:
            print entry

    Log entries fields are assumed to be accessible as attributes.

    Adding entries:
        Entry = namedtuple('Entry', 'field_a field_b')
        entry = Entry(1, 2)
        log_container.append(entry)

    Entries are stored in the same order as in the original log.
    """

    def __init__(self, searchable_fields=None):
        """Create LogContainer instance"""

        self._entries = []
        # searchable_fields is assumed to store names of fields present
        # in each log entry
        self._searchable_fields = searchable_fields or []
        # buckets are always sorted lists which store pointers to entries
        # and allow efficient search
        self._buckets = dict([(field, []) for field in self._searchable_fields])

    _converters = { }

    @property
    def entries(self):
        """Provide access to entries"""
        return self._entries[:]

    def _marshall_value(self, field_name, value):
        converter = self._converters.get(field_name)
        if converter:
            return converter(value)
        return value

    def append(self, entry):
        """Appends log entry to end"""

        self._entries.append(entry)

        # add reference to row into sorted buckets
        last_index = len(self._entries) - 1
        for field in self._searchable_fields:
            # insert entry reference into bucket while preserving sorting
            # sort order: field value, then the entry index
            try:
                sortable_value = self._marshall_value(field,
                                                      getattr(entry, field))
            except AttributeError:
                raise ValueError("Entry %s doesn't have field '%s'"
                                 % (entry, field))
            bisect.insort_right(self._buckets[field],
                                (sortable_value, last_index))

    def find_by(self, field_name, value, value_to=None):
        """
        Find all log entries which field_name has given value.

        If value_to arg is given then all entries which specified field is
        within the given range will be returned.

        When searching for range the result includes values equal to both
        boundary parameters

        Passing 'field_name' that isn't one of the searchable fields specified
        in the class's constructor raises ValueError.
        """

        found = []
        value = self._marshall_value(field_name, value)
        if value_to:
            value_to = self._marshall_value(field_name, value_to)
        else:
            value_to = value
        try:
            bucket = self._buckets[field_name]
        except KeyError:
            raise ValueError(
                "Field %s doesn't exist or doesn't support search" 
                % field_name)

        # find first occurrence of value
        low = bisect.bisect_left(bucket, (value, 0))
        # find last occurrence of value_to
        high = bisect.bisect_right(bucket,
                                   (value_to, len(self._entries)),
                                   lo=low)

        # find referenced entries
        found = [self._entries[i] for _, i in bucket[low:high]]
        return found


class CustomLog(LogContainer):
    """
    Class enforces format provided in the assignment

    It provides CustomLog.load() method which parses the log stream.
    Empty lines that aren't part of entry message or lines not conforming to
    the format are ignored
    """

    def __init__(self):
        searchable_fields = ['date', 'loglevel', 'sessionid', 'businessid']
        super(CustomLog, self).__init__(searchable_fields)
        self._converters['date'] = self._datetime_converter
        self._converters['loglevel'] = self._loglevel_converter
        self._converters['sessionid'] = self._xid_converter
        self._converters['businessid'] = self._xid_converter

    date_format = "%Y-%m-%d %H:%M:%S"

    # customisation in __repr__ for nice printing
    class LogEntry(namedtuple('LogEntry',
                              ['date', 'loglevel', 'sessionid',
                               'businessid', 'requestid', 'message'])):
        """Provides lightweight read-only type for log entries"""

        __slots__ = ()

        def __str__(self):
            return ' '.join([self.date.strftime(CustomLog.date_format),
                             self.loglevel,
                             self.sessionid,
                             self.businessid,
                             self.requestid,
                             self.message])

        def __repr__(self):
            return '"%s"' % self.__str__()

    _message_boundary = "'"

    # regexp for parsing entries - only captures 1st line of
    # a multiline log entry
    _entry_re = re.compile((
        r'(?P<date>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) '
        r'(?P<loglevel>\w+) '
        r'(?P<sessionid>SID:\d+) '
        r'(?P<businessid>BID:\d+) '
        r'(?P<requestid>RID:[0-9a-f]+) '
        r'(?P<message>%s.*)') % _message_boundary,
    )

    def _loglevel_converter(self, loglevel):
        if "ERROR" == loglevel:
            return 2
        if "WARN" == loglevel:
            return 4
        if "DEBUG" == loglevel:
            return 8
        raise ValueError("Unknown loglevel")

    def _datetime_converter(self, date):
        return (date - datetime(1970, 1, 1)).total_seconds()

    def _xid_converter(self, xid):
        return xid[4:]

    def load(self, data):
        """Loads log from stream and populates itself"""

        # log stream is read one line at a time
        # the processing loop delays adding the entry until a potentially
        # multiline message is complete
        # if a new entry is recognised while the old one is still incomplete
        # then the old one is never added to the container
        entry_data = {}
        for line in data:
            # lines contain newline chars that are stripped at the end of full
            # entry but retained when part of the entry
            match = self._entry_re.match(line)
            if match:
                entry_data = dict(
                    date=datetime.strptime(match.group('date'),
                                           self.date_format),
                    loglevel=match.group('loglevel'),
                    sessionid=match.group('sessionid'),
                    businessid=match.group('businessid'),
                    requestid=match.group('requestid'),
                    message=match.group('message'))

                if entry_data['message'][-1] == self._message_boundary:
                    # message complete in one line
                    self.append(self.LogEntry(**entry_data))
                    entry_data = {}
                else:
                    # add back the newline that regexp dropped
                    # it's part of the message
                    entry_data['message'] += '\n'

            elif entry_data:
                stripped = line.rstrip() 
                if not stripped or stripped[-1] != self._message_boundary:
                    # part of the message field
                    entry_data['message'] += line
                else:
                    # it's the last line of entry
                    entry_data['message'] += stripped
                    # create entry
                    self.append(self.LogEntry(**entry_data))
                    entry_data = {}


# functions requested in the assignment that query by particular fields

def find_entries_with_log_level(log_container, log_level):
    """Finds entries with the specified log level."""
    return log_container.find_by('loglevel', log_level)

def find_entries_with_business_id(log_container, business_id):
    """Finds entries with the specified business id"""
    return log_container.find_by('businessid', business_id)

def find_entries_within_date_range(log_container, date_from, date_to):
    """Finds entries within the range of dates specified"""
    if isinstance(date_from, str):
        date_from = datetime.strptime(date_from, log_container.date_format)
    if isinstance(date_to, str):
        date_to = datetime.strptime(date_to, log_container.date_format)
    return log_container.find_by('date', date_from, date_to)

def find_entries_with_session_id(log_container, session_id):
    """Finds entries with the specified session id"""
    return log_container.find_by('sessionid', session_id)
