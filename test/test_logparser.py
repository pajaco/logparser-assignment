from nose.tools import *
from logparser import logparser 
from cStringIO import StringIO
from datetime import datetime
from collections import namedtuple

# tests for Custom log_container format
def load_fa_container(stream_data):
    log_container = logparser.CustomLog()
    log_container.load(StringIO(stream_data))
    return log_container

def test_empty_stream_adds_no_entry():
    log_container = load_fa_container('')
    assert_false(log_container.entries)


def test_wrong_format_log_entry_is_skipped():
    log_container = load_fa_container('01/01/2012 DEBUG "blah"')
    assert_false(log_container.entries)


def test_entry_integrity_after_parsing():
    stream = "2012-01-01 00:00:01 DEBUG SID:1 BID:2 RID:3 'A'"
    log_container = load_fa_container(stream)

    assert_equal(1, len(log_container.entries))
    entry = log_container.entries[0]
    assert_equal(log_container.LogEntry, type(entry))
    assert_equal("2012-01-01 00:00:01",
                 entry.date.strftime(log_container.date_format))
    assert_equal("DEBUG", entry.loglevel)
    assert_equal("SID:1", entry.sessionid)
    assert_equal("BID:2", entry.businessid)
    assert_equal("RID:3", entry.requestid)
    assert_equal("'A'", entry.message)

    # test repr and str formatting of an entry
    assert_equal(stream, str(entry))
    assert_equal('"%s"' % stream, repr(entry))


def test_mixed_format_log_loads_fa_style_only():
    fa_entry = "2012-01-01 00:00:01 DEBUG SID:1 BID:2 RID:3 'A'"
    stream = "\n".join(['01/01/2012 DEBUG "blah"',
                        fa_entry,
                        '01/01/2012 DEBUG "blah"'])
    log_container = load_fa_container(stream)
    assert_equal(1, len(log_container.entries))
    assert_equal(fa_entry, str(log_container.entries[0]))


def test_line_breaks_in_message_retained():
    entry = "2012-01-01 00:00:00 DEBUG SID:1 BID:2 RID:3 'A\nB'"
    log_container = load_fa_container(entry)
    assert_equal(1, len(log_container.entries))
    assert_equal("'A\nB'", log_container.entries[0].message)


def test_unrelated_empty_lines_are_ignored():
    stream = """
    
2012-01-01 00:00:00 DEBUG SID:1 BID:2 RID:3 'A

B'

2011-12-31 23:58:00 DEBUG SID:1 BID:2 RID:3 'V'

"""
    log_container = load_fa_container(stream)
    #print log_container.entries
    assert_equal(2, len(log_container.entries))
    assert_equal("'A\n\nB'", log_container.entries[0].message)
    assert_equal("'V'", log_container.entries[1].message)


def test_order_of_entries_is_retained():
    # logs must be stored in the order they come
    stream = """2012-01-01 00:00:00 DEBUG SID:1 BID:2 RID:3 'A'
2011-12-31 23:58:00 DEBUG SID:1 BID:2 RID:3 'V'"""
    log_container = load_fa_container(stream)
    assert_equal(2011, log_container.entries[-1].date.year)


# tests for general log_container container
Entry = namedtuple('Entry', ['a', 'b'])


def test_adding_entries_with_no_searchable_fields_raises_error():
    log_container = logparser.LogContainer(['c'])
    entry = Entry(1, '+')
    assert_raises(ValueError, log_container.append, entry)


def test_searching_entries_on_nonsearchable_fields_raises_error():
    log_container = logparser.LogContainer(['a'])
    entry = Entry(1, '+')
    log_container.append(entry)
    assert_raises(ValueError, log_container.find_by, 'b', 1)


def load_container():
    log_container = logparser.LogContainer(['a'])
    entries = [Entry(1, '+'), Entry(2, '-'), Entry(3, '/'), Entry(2, '%')]
    for entry in entries:
        log_container.append(entry)
    return log_container, entries


def test_searching_with_matching_entries():
    log_container, entries = load_container()
    assert_equal([entries[1], entries[3]], log_container.find_by('a', 2))


def test_searching_with_no_matching_entries():
    log_container, entries = load_container()
    assert_equal([], log_container.find_by('a', 10))


def test_range_searching_with_matching_entries():
    log_container, entries = load_container()
    result = log_container.find_by('a', 2, 3)
    assert_equal([entries[1], entries[3], entries[2]], result)


def test_range_searching_with_no_matching_entries():
    log_container, entries = load_container()
    result = log_container.find_by('a', 10, 20)
    assert_equal([], result)
