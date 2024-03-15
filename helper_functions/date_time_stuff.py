# this module contains helper functions for date and time handling

from datetime import datetime as dt

def datenum(date, time):
    """Convert date and time to a number, equivalent to the datenum function in matlab
    date: int, date in the format YYYYMMDD
    time: int, time in the format HHMMSS
    return: float, date number (1 is 1.1.0001 00:00:00, 1.5 is 1.1.0001 12:00:00, ...)"""
    date = str(date)
    time = str(time)
    try:
        assert len(time) == 6
    except AssertionError:
        # the first digits are missing. Fill up at the left side with 0 until 6 digits exist
        time = '0'* (6 - len(time)) + time

    d = dt.strptime(date + ' ' + time, '%Y%m%d %H%M%S')
    return d.toordinal() + d.hour/24 + d.minute/(24*60) + d.second/(24*60*60)
    # return 366 + d.toordinal() + (d - dt.fromordinal(d.toordinal())).total_seconds()/(24*60*60)