#!/usr/bin/env python

import os
import re
from datetime import datetime, timedelta

def check_error(filename):
    content = None
    with open(filename) as fin: content = fin.read()
    if re.search(r'ERROR.*Read\s+Configure\s+File\s+Error', content, re.I):
        return True
    else:
        return False

def read_ip(filename):
    content = None
    with open(filename) as fin: content = fin.read()
    m = re.search(r'\s*inet addr:(\d+\.\d+\.\d+\.\d+)\s+Bcast:\d+\.\d+\.\d+\.\d+\s+Mask:\d+\.\d+\.\d+\.\d+\s*', content, re.I)
    if m:
        return m.group(1)
    else:
        return None

target_dir = '/scratchfs/hxmt/hdpc/Sub'
ref_target = re.compile(r'SubJob-(ID\d+-\d+-\w+).sh.out.(\d+).\d', re.I)

filelist = [x for x in os.listdir(target_dir) if ref_target.match(x)]
filelist.sort()

filelist_selected = []
start_date = datetime(2018, 9, 1)
for x in filelist:
    m = re.match(r'SubJob-ID\d+-(\d\d\d\d\d\d\d\d)-\w+.sh.out.\d+.\d', x, re.I)
    filedate = datetime.strptime(m.group(1), '%Y%m%d')
    if filedate >= start_date:
        filelist_selected.append(x)

for x in filelist_selected:
    if not check_error(os.path.join(target_dir, x)): continue
    m = ref_target.match(x)
    col1 = m.group(1)
    col2 = m.group(2)
    col3 = read_ip(os.path.join(target_dir, x))
    print x, col1, col2, col3


