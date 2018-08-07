#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Constants Begin
OutputBufferPath = '/mnt/parastor/hxmtdata/work/DPGS_WORKSPACE/OutputBuffer'
# Constants End

import os
import re
import argparse
import MySQLdb as mdb
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='description')
parser.add_argument("-B", dest = "begin_date_str", help = "BeginDate")
parser.add_argument("-E", dest = "end_date_str",   help = "FinalDate")
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
    print x


