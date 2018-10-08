#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import MySQLdb as mdb
import csv
from datetime import datetime, timedelta
import pytz
from utils import *

parser = argparse.ArgumentParser(description='description')
parser.add_argument("--taskid", dest = "taskid", help = "TaskID")
parser.add_argument("--dataid", dest = "dataid", help = "DataID")
parser.add_argument("--bgnutc", dest = "bgnutc", help = "Begin of UTC time with format YYYY-mm-ddTHH:MM:SS")
parser.add_argument("--endutc", dest = "endutc", help = "End of UTC time with format YYYY-mm-ddTHH:MM:SS")
parser.add_argument("-o", dest = "outfile", help = "CSV file of output", default = "output.csv")
parser.add_argument("--host", dest = "mysql_host", help = "mysql_host", default = "localhost")
parser.add_argument("--user", dest = "mysql_user", help = "mysql_user", default = "hxmt_user")
parser.add_argument("--passwd", dest = "mysql_passwd", help = "mysql_passwd", default = "hxmt_passwd")
args = parser.parse_args()


bgnutc_dt, endutc_dt = None, None
if args.bgnutc and args.endutc:
    bgnutc_dt = datetime.strptime(args.bgnutc, '%Y-%m-%dT%H:%M:%S')
    endutc_dt = datetime.strptime(args.endutc, '%Y-%m-%dT%H:%M:%S')
    if endutc_dt < bgnutc_dt:
        print "bad input utc time range"
        exit(1)
elif args.bgnutc and not args.endutc:
    bgnutc_dt = datetime.strptime(args.bgnutc, '%Y-%m-%dT%H:%M:%S')
    endutc_dt = bgnutc_dt + timedelta(days = 7)
elif not args.bgnutc and args.endutc:
    endutc_dt = datetime.strptime(args.endutc, '%Y-%m-%dT%H:%M:%S')
    bgnutc_dt = endutc_dt - timedelta(days = 7)
else:
    endutc_dt = datetime.now()
    bgnutc_dt = endutc_dt - timedelta(days = 7)

bgnutc_met = utc_dt_to_hxmt_met(bgnutc_dt)
endutc_met = utc_dt_to_hxmt_met(endutc_dt)

where_clause = ''
if args.taskid:
    where_clause = 'task_id = "%s"' % args.taskid
else:
    where_clause = 'time_start > %d and time_end < %d' % (bgnutc_met, endutc_met)
    if args.dataid:
        where_clause += ' and data_id = %s' % args.dataid

print where_clause

def fetch_task_info_list(where_c):
    try:
        con = mdb.connect(args.mysql_host, args.mysql_user, args.mysql_passwd, 'hhds')
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute('select task_id, data_id, time_start, time_end, finished_status from task_info_list where ' + where_c)
        return cur.fetchall()
    except mdb.Error, e:
        print "MySQL Error %d: %s" % (e.args[0],e.args[1])
        exit(1)
    finally:
        if con: con.close()

def fetch_input_file_ids(taskid):
    try:
        con = mdb.connect(args.mysql_host, args.mysql_user, args.mysql_passwd, 'hhds')
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute('select input_file_id from task_input_list where task_id = "%s"' % taskid)
        rows = cur.fetchall()
        if not rows:
            print "no row found for task_id %s from task_input_list" % taskid
            exit(1)
        if len(rows) > 1:
            print "multiple rows found for task_id %s from task_input_list" % taskid
            exit(1)
        return rows[0]['input_file_id'].split(',')
    except mdb.Error, e:
        print "MySQL Error %d: %s" % (e.args[0],e.args[1])
        exit(1)
    finally:
        if con: con.close()

print fetch_input_file_ids(args.taskid)

