#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import MySQLdb as mdb
import csv
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='description')
parser.add_argument("obs_id_file", help = "CSV file of obs_id list")
parser.add_argument("-w", dest = "owner_file", help = "CSV file of owner list")
parser.add_argument("-o", dest = "outfile", help = "CSV file of output", default = "output.csv")
parser.add_argument("--host", dest = "mysql_host", help = "mysql_host", default = "localhost")
parser.add_argument("--user", dest = "mysql_user", help = "mysql_user", default = "hxmt_user")
parser.add_argument("--passwd", dest = "mysql_passwd", help = "mysql_passwd", default = "hxmt_passwd")
parser.add_argument("--dbname", dest = "mysql_dbname", help = "mysql_dbname", default = "hxmt")
args = parser.parse_args()

def leap_second(gps_second):
    if gps_time < 1025136015:
        return 15
    elif gps_time < 1119744016:
        return 16
    elif gps_time < 1167264017:
        return 17
    else:
        return 18

def gps_to_utc_str(gps_second):
    utc_second = gps_second - leap_second(gps_second)
    utc_datetime = datetime(1980, 1, 6, 0, 0, 0) + timedelta(seconds = utc_second);
    return utc_datetime.strftime('%m/%d/%Y %H:%M:%S')

def hxmt_met_to_utc_str(hxmt_met):
    gps_second = 1009411215.0 + hxmt_met
    return gps_to_utc_str(gps_second)

# read owner_dict
owner_dict = {}
with open(args.owner_file, 'r') as fin:
    for row in csv.reader(fin, delimiter=',', quotechar='"'):
        (group, obs_id) = row
        owner_dict[obs_id.strip()] = group.strip()

# read obs_id_list
obs_id_list = []
for line in open(args.obs_id_file, 'r'):
    obs_id_list.append(line.strip())

if not obs_id_list:
    print 'obs_id_list is empty'
    exit(1)

# generate where clause
where_clause = ''
for idstr in obs_id_list:
    if not where_clause:
        where_clause = 'thing = "%s"' % idstr
    else:
        where_clause += ' or thing = "%s"' % idstr

# read_database
# TODO: change the headers
header = ['thing', 'legs', 'arms']
output_rows = []
try:
    con = mdb.connect(args.mysql_host, args.mysql_user, args.mysql_passwd, args.mysql_dbname)
    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute('select * from limbs where ' + where_clause)
    for row in cur.fetchall():
        # TODO: generate and append rows in output_rows
        thing = row['thing']
        legs = str(row['legs'])
        arms = str(row['arms'])
        orow_list = [thing, legs, arms]
        output_rows.append(orow_list)

except mdb.Error, e:
    print "MySQL Error %d: %s" % (e.args[0],e.args[1])
    exit(1)
finally:
    if con: con.close()

if not output_rows:
    print 'found nothing from database'
    exit(1)

# write data
with open(args.outfile, 'w') as fout:
    csv_writer = csv.writer(fout, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    # write header
    header += ['id']
    print ', '.join(header)
    csv_writer.writerow(header)
    # write rows
    for (idx, row) in enumerate(output_rows, start = 1):
        orow = [str(idx)] + row
        print ', '.join(orow)
        csv_writer.writerow(orow)

