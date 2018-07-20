#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import codecs
import re
import xml.etree.ElementTree as ET
from pprint import pprint

infile = sys.argv[1]

def read_plan_file(filename_xml):
    # read xml file
    doc = None
    with codecs.open(infile, 'r', encoding = 'gb2312') as fin:
        content = fin.read().encode('utf-8')
        content = re.sub(r'encoding\s*=\s*["\']gb2312["\']', 'encoding="utf-8"', content)
        doc = ET.fromstring(content)

    # parse xml data to a dict
    plan_dict = {}
    plan_dict['plan_id'] = doc.find(u'短期观测计划编号').text
    plan_dict['plan_type'] = doc.find(u'计划类别').text
    plan_dict['plan_start_time'] = doc.find(u'开始时间').text
    plan_dict['plan_stop_time'] = doc.find(u'结束时间').text
    plan_dict['form_people'] = doc.find(u'制定人').text
    plan_dict['form_time'] = doc.find(u'制定时间').text
    plan_dict['sim_flag'] = doc.find(u'是否仿真').text
    plan_dict['note2'] = doc.find(u'备注2').text

    task_list = []
    for task in doc.findall(u'观测任务列表/观测任务'):
        task_dict = {}
        task_dict['obs_num'] = task.get(u'观测号')
        task_dict['target_name'] = task.get(u'源名称')
        task_dict['proposal_people'] = task.get(u'提案人')
        task_dict['continue_flag'] = task.get(u'是否延续观测')
        task_dict['task_start_time'] = task.find(u'观测开始时间').text
        task_dict['task_stop_time'] = task.find(u'观测结束时间').text
        task_dict['obs_mode'] = task.find(u'观测模式').text
        el = task.find(u'源流量')
        target_fluence = {}
        target_fluence['zone1'] = el.get(u'分区1')
        target_fluence['zone2'] = el.get(u'分区2')
        target_fluence['zone3'] = el.get(u'分区3')
        task_dict['target_fluence'] = target_fluence
        el = task.find(u'数据量')
        data_size = {}
        data_size['zone0'] = el.get(u'分区0')
        data_size['zone1'] = el.get(u'分区1')
        data_size['zone2'] = el.get(u'分区2')
        data_size['zone3'] = el.get(u'分区3')
        task_dict['data_size'] = data_size
        el = task.find(u'姿态机动')
        attitude_control = {}
        attitude_control['control_method'] = el.get(u'控制方式')
        attitude_control['path'] = el.get(u'路径')
        task_dict['attitude_control'] = attitude_control
        task_dict['note1'] = task.find(u'备注1').text
        if 'ASS' != task_dict['obs_mode']:
            el = task.find(u'目标')
            position = {}
            position['ra'] = el.get(u'赤经')
            position['dec'] = el.get(u'赤纬')
            if 'SSDS' == task_dict['obs_mode']:
                position['radius'] = el.get(u'扫描半径')
                position['interval'] = el.get('扫描行间距')
                position['speed'] = el.get('扫描速率')
            task_dict['position'] = position
            if 'Point' == task_dict['obs_mode']:
                task_dict['offaxis_flag'] = task.find(u'偏轴观测').text
                el = task.find(u'是否偏置观测')
                offaxis_pars = {}
                offaxis_pars['value'] = el.get(u'值')
                el2 = el.find(u'姿态四元数')
                offaxis_pars['attitude'] = {'q0': el2.get('q0'),
                        'q1': el2.get('q1'), 'q2': el2.get('q2'), 'q3': el2.get('q3')}
                task_dict['offaxis_pars'] = offaxis_pars
        task_list.append(task_dict)
    plan_dict['task_list'] = task_list

    saa_range_list = []
    for saa_range in doc.findall(u'过SAA区时段列表/时段'):
        saa_range_dict = {}
        saa_range_dict['in_time'] = saa_range.get(u'进SAA区时间')
        saa_range_dict['out_time'] = saa_range.get(u'出SAA区时间')
        saa_range_list.append(saa_range_dict)
    plan_dict['saa_range_list'] = saa_range_list

    # return result
    return plan_dict

def read_range_list(filename_txt):
    range_list = []
    for line in open(filename_txt, 'r'):
        l = line.strip()
        if l: range_list.append(l.split(' '))
    return range_list


# unit test
# plan_dict = read_plan_file(infile)
# pprint(plan_dict)
# pprint(read_range_list(infile))

