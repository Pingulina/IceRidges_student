# this module contains helper functions for date and time handling
import numpy as np
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


def datestr(date_num, format='YYYYMMDD'):
    """Convert a date number to a string, equivalent to the datestr function in matlab
    date_num: float, date number (1 is 1.1.0001 00:00:00, 1.5 is 1.1.0001 12:00:00, ...)
    return: str, date in the format YYYYMMDD"""
    # if date_num is an array, convert each element
    if type(date_num) == list:
        return [datestr(d, format) for d in date_num]
    elif type(date_num) == np.ndarray:
        return np.array([datestr(d, format) for d in date_num])
    d = dt.fromordinal(int(date_num))
    if format == 'YYYYMMDD':
        return format_YYYYMMDD(d)
    elif format == 'YYYY.MM.DD':
        return format_dot_date_reverse(d)
    elif format == 'DD.MM.YYYY':
        return format_dot_date(d)
    elif format == 'DD.MM.YY':
        return format_dot_date_short(d)
    else:
        raise ValueError('The format ' + format + ' is not supported.')
    

def datestr_hour(date_num, format='YYYYMMDDHHmmss'):
    """Convert a date number to a string, equivalent to the datestr function in matlab, include the hour
    date_num: float, date number (1 is 1.1.0001 00:00:00, 1.5 is 1.1.0001 12:00:00, ...)
    return: str, date in the format YYYYMMDDHH"""
    d = dt.fromordinal(int(date_num))
    hours = int((date_num - int(date_num))*24)
    d = d.replace(hour=hours)
    minutes = int(((date_num - int(date_num))*24 - hours)*60)
    seconds = int((((date_num - int(date_num))*24 - hours)*60 - minutes)*60)
    d = d.replace(minute=minutes)
    d = d.replace(second=seconds)
    if format == 'YYYYMMDDHHmmss':
        return d.strftime('%Y%m%d%H%M%S')
    elif format == 'YYYY-MM-DD HH:mm:ss':
        return d.strftime('%Y-%m-%d %H:%M:%S')
    elif format == 'DD.MM.YYYY HH:mm:ss':
        return d.strftime('%d.%m.%Y %H:%M:%S')
    elif format == 'HH:mm:ss':
        return d.strftime('%H:%M:%S')
    else:
        raise ValueError('The format ' + format + ' is not supported.')
   

def format_YYYYMMDD(dateNum:int):
    """Convert a date string to the format YYYYMMDD
    dateNum: int, dateNum
    return: str, date in the format YYYYMMDD"""
    return dateNum.strftime('%Y%m%d')

def format_dot_date_reverse(dateNum:int):
    """Convert a date string to the format YYYY.MM.DD
    dateNum: int, dateNum
    return: str, date in the format YYYY.MM.DD"""
    return dateNum.strftime('%Y.%m.%d')

def format_dot_date(dateNum:int):
    """Convert a date string to the format DD.MM.YYYY
    dateNum: int, dateNum
    return: str, date in the format DD.MM.YYYY"""
    return dateNum.strftime('%d.%m.%Y')

def format_dot_date_short(dateNum:int):
    """Convert a date string to the format DD.MM.YY
    dateNum: int, dateNum
    return: str, date in the format DD.MM.YY"""
    return dateNum.strftime('%d.%m.%y')