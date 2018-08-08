#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Constants Begin
OutputBufferPath = '/mnt/parastor/hxmtdata/work/DPGS_WORKSPACE/OutputBuffer'
ArchivePath ='/hxmt/data/Mission/HXMT/Archive_20170616'
LocalCatalogPath = '/mnt/parastor/hxmtdata/work/DPGS_WORKSPACE/LocalCatalog'
RunLogPath = '/mnt/parastor/hxmtdata/work/DPGS_WORKSPACE/TaskRunner/Sub'
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

def file_comp(file1, file2, file3):
    return True

def find_runlog(task_id):
    ref_all = re.compile(task_id, re.I)
    all_files = [x for x in RunLogPath if ref_all.match(x)]
    if not all_files: return None
    ref_sh  = re.compile(r'\.sh$')
    ref_err = re.compile(r'\.sh\.err\.')
    ref_out = re.compile(r'\.sh\.out\.')
    sh_fn, sh_t = '', 0
    err_fn, err_t = '', 0
    out_fn, err_t = '', 0
    for x in all_files:
        x_path = os.path.join(RunLogPath, x)
        x_time = os.path.getmtime(x_path)
        if ref_sh.match(x) and x_time > sh_t:
            sh_fn, sh_t = x_path, x_time
        elif ref_err.match(x) and x_time > err_t:
            err_fn, err_t = x_path, x_time
        elif ref_out.match(x) and x_time > out_t:
            out_fn, out_t = x_path, x_time
    if not sh_fn and not err_fn and not out_fn:
        return (sh_fn, out_fn, err_fn)
    else:
        return None

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
    if len(row) < 1:
        print 'no row with task_id ' + task_id + ' found from database'
        continue
    elif len(row) > 1:
        print 'found multiple rows for task_id ' + task_id + ' from database'
        continue
    local_file = os.path.join(LocalCatalogPath, row[0]['local_file'].strip())
    archived_file = os.path.join(ArchivePath, row[0]['archived_file'].strip())
    buffer_file = x
    found_local = True
    found_archived = True
    if not os.path.isfile(local_file):
        found_local = False
        print 'not found file ' + local_file
    if not os.path.isfile(archived_file):
        found_archived = False
        print 'not found file ' + archived_file
    if not found_local or not found_archived: continue
    if file_compare(buffer_file, local_file, archived_file):
        runlog = find_runlog(task_id)
        if not runlog:
            print 'no runlog found'
            continue
        # TODO do runlog file checking and moving work here
    else:
        print 'differences among the three files found'
        continue





