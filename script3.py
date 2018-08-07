#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import MySQLdb as mdb
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description='description')
parser.add_argument("-B", dest = "begin_date", help = "BeginDate")
parser.add_argument("-E", dest = "end_date",   help = "FinalDate")
args = parser.parse_args()


