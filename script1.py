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

def leap_second(gps_time):
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

now_datetime = datetime.now()
now_time_str = now_datetime.strftime('%m/%d/%Y %H:%M:%S')
now_date_str = now_datetime.strftime('%Y%m%d')

# read owner_dict
owner_dict = {}
with open(args.owner_file, 'r') as fin:
    for row in csv.reader(fin, delimiter=',', quotechar='"'):
        (group, obs_id) = row
        owner_dict[obs_id.strip()] = group.strip()

# read obs_id_list
obs_id_list = []
for line in open(args.obs_id_file, 'r'):
    l = line.strip()
    if not l: continue
    if l[0] == '#': continue
    obs_id_list.append(l)

if not obs_id_list:
    print 'obs_id_list is empty'
    exit(1)

# generate where clause
where_clause = ''
for idstr in obs_id_list:
    if not where_clause:
        where_clause = 'obs_id = "%s"' % idstr
    else:
        where_clause += ' or obs_id = "%s"' % idstr

obs_id_found_list = []
obs_id_without_owner_list = []

# read_database
header = ['数据级别', '标示', '名字', '生成时间', '观测起始时间',
        '观测起始时间2', '观测结束时间', '观测结束时间2', '是否公开',
        '数据归属', '时长', '观测号', '目标名', '源坐标', '提案id', '创建人',
        '是否偏轴', '扫描半径', '扫描间隔', '扫描速度']
name_dict = {'Q': '小天区观测', 'L': '定点观测', 'Z': '巡天观测'}
output_rows = []
try:
    con = mdb.connect(args.mysql_host, args.mysql_user, args.mysql_passwd, args.mysql_dbname)
    cur = con.cursor(mdb.cursors.DictCursor)
    cur.execute('select * from taskmanager_obs_list_store where ' + where_clause)
    for row in cur.fetchall():
        # fetch fields
        obs_id               = row['obs_id']
        obs_mode             = row['obs_mode']
        ensured_start_time   = row['ensured_start_time']
        ensured_end_time     = row['ensured_end_time']
        target               = row['target']
        ra_t                 = row['ra_t']
        dec_t                = row['dec_t']
        proposal             = row['proposal']
        pi                   = row['pi']
        offset_flag          = row['offset_flag']
        radius               = row['radius']
        interval             = row['interval']
        speed                = row['speed']
        # check
        obs_id_found_list.append(obs_id)
        owner = ''
        if owner_dict.has_key(proposal):
            owner = owner_dict[proposal]
        else:
            obs_id_without_owner_list.append([obs_id, proposal])
        # do extra calculations
        marking = obs_id + '_' + now_date_str
        obs_mode_name = name_dict[obs_mode]
        data_level = '1L'
        gen_time = now_time_str
        start_time_utc = hxmt_met_to_utc_str(ensured_start_time)
        end_time_utc = hxmt_met_to_utc_str(ensured_end_time)
        open_flag = 0
        obs_duration = ensured_end_time - ensured_start_time
        target_pos = ', '.join([str(ra_t), str(dec_t)])

        orow_list = [data_level, marking, obs_mode_name, gen_time, start_time_utc,
                ensured_start_time, end_time_utc, ensured_end_time, open_flag,
                owner, obs_duration, obs_id, target, target_pos, proposal, pi,
                offset_flag, radius, interval, speed]
        output_rows.append(orow_list)

except mdb.Error, e:
    print "MySQL Error %d: %s" % (e.args[0],e.args[1])
    exit(1)
finally:
    if con: con.close()

if not output_rows:
    print 'found nothing from database'
    exit(1)

obs_id_not_found_list = []
for x in obs_id_list:
    if x not in obs_id_found_list:
        obs_id_not_found_list.append(x)
if obs_id_not_found_list:
    print "Warning, the following obs_id are not found in the database:"
    print '-' * 20
    for x in obs_id_not_found_list:
        print x
    print '-' * 20

if obs_id_without_owner_list:
    print "Warning, the following obs_id with proposal has no owner found:"
    print '-' * 20
    for x in obs_id_without_owner_list:
        print ', '.join(x)
    print '-' * 20

# write data
with open(args.outfile, 'w') as fout:
    csv_writer = csv.writer(fout, delimiter=',', quotechar='"')
    # write header
    header = ['id'] + header
    # print ', '.join(header)
    csv_writer.writerow(header)
    # write rows
    for (idx, row) in enumerate(output_rows, start = 1):
        orow = [str(x) for x in [idx] + row]
        # print ', '.join(orow)
        csv_writer.writerow(orow)

