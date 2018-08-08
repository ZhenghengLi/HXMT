#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Constants Begin
OutputBufferPath = '/mnt/parastor/hxmtdata/work/DPGS_WORKSPACE/OutputBuffer'
ArchivePath ='/hxmt/data/Mission/HXMT/Archive_20170616'
# Constants End

import os
import re
import argparse
import MySQLdb as mdb
from datetime import datetime, timedelta

#### functions Begin ####

def fetch_row(task_id, host, user, passwd, dbname):
    try:
        con = mdb.connect(host, user, passwd, dbname)
        cur = con.cursor(mdb.cursors.DictCursor)
        cur.execute('select task_id, local_file, archived_file from file_info_t where task_id = "%s"' % task_id)
        return cur.fetchall()
    except mdb.Error, e:
        print "MySQL Error %d: %s" % (e.args[0],e.args[1])
        exit(1)
    finally:
        if con: con.close()

#### functions End   ####

parser = argparse.ArgumentParser(description='description')
parser.add_argument("-B", dest = "begin_date_str", help = "BeginDate")
parser.add_argument("-E", dest = "end_date_str",   help = "FinalDate")
parser.add_argument("--host", dest = "mysql_host", help = "mysql_host", default = "localhost")
parser.add_argument("--user", dest = "mysql_user", help = "mysql_user", default = "hxmt_user")
parser.add_argument("--passwd", dest = "mysql_passwd", help = "mysql_passwd", default = "hxmt_passwd")
parser.add_argument("--dbname", dest = "mysql_dbname", help = "mysql_dbname", default = "hxmt")
args = parser.parse_args()

date_fmt = '%Y%m%d'
begin_date = datetime.strptime(args.begin_date_str, date_fmt)
end_date = datetime.strptime(args.end_date_str, date_fmt)

ref_date = re.compile(r'\d{8}')
folder_list =[]
for folder in [x for x in os.listdir(OutputBufferPath) if ref_date.match(x)]:
    cur_date = datetime.strptime(folder, date_fmt)
    if cur_date >= begin_date and cur_date <= end_date:
        folder_list.append(os.path.join(OutputBufferPath, folder))

ref_file = re.compile(r'ID\d+-\d+-\w+\.fits', re.I)
file_list = []
for folder in folder_list:
    file_list += [os.path.join(folder, x) for x in os.listdir(folder) if ref_file.match(x)]

if not file_list:
    print 'do not find any files in between ' + args.begin_date_str + ' and ' + args.end_date_str

for x in file_list:
    basename = os.path.basename(x)
    task_id = basename[:-5]
    row = fetch_row(task_id, args.mysql_host, args.mysql_user, args.mysql_passwd, args.mysql_dbname)
    print task_id, len(row)


