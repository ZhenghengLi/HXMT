#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
import re
import xml.etree.ElementTree as ET

infile = sys.argv[1]

content = None
with codecs.open(infile, 'r', encoding = 'gb2312') as fin:
    content = fin.read().encode('utf-8')
    content = re.sub(r'encoding.*=.*["\']gb2312["\']', 'encoding="utf-8"', content)

root = ET.fromstring(content)
for task_list in root.findall(u'观测任务列表'):
    for task in task_list.findall(u'观测任务'):
        print task.get(u'提案人')


