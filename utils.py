#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz

def leap_second_gps(gps_time):
    if gps_time < 1025136015:
        return 15
    elif gps_time < 1119744016:
        return 16
    elif gps_time < 1167264017:
        return 17
    else:
        return 18

def leap_second_utc(utc_time):
    if utc_time < 1025136015 - 15:
        return 15
    elif utc_time < 1119744016 - 16:
        return 16
    elif utc_time < 1167264017 - 17:
        return 17
    else:
        return 18

def gps_to_utc_str(gps_second):
    utc_second = gps_second - leap_second_gps(gps_second)
    utc_datetime = datetime(1980, 1, 6, 0, 0, 0) + timedelta(seconds = utc_second);
    return utc_datetime.strftime('%Y-%m-%dT%H:%M:%S')

def utc_str_to_gps(utc_str):
    utc_datetime = datetime.strptime(utc_str, '%Y-%m-%dT%H:%M:%S')
    utc_seconds = (utc_datetime - datetime(1980, 1, 6, 0, 0, 0)).total_seconds()
    gps_seconds = utc_seconds + leap_second_utc(utc_seconds)
    return gps_seconds

def hxmt_met_to_utc_str(hxmt_met):
    gps_second = 1009411215.0 + hxmt_met
    return gps_to_utc_str(gps_second)

def utc_str_to_hxmt_met(utc_str):
    gps_time = utc_str_to_gps(utc_str)
    return gps_time - 1009411215.0

def utc_dt_to_hxmt_met(utc_dt):
    utc_seconds = (utc_dt - datetime(1980, 1, 6, 0, 0, 0)).total_seconds()
    gps_seconds = utc_seconds + leap_second_utc(utc_seconds)
    return gps_seconds - 1009411215.0

