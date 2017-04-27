#!/usr/bin/python
#-*- coding: UTF-8 -*- 
#coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import pandas as pd
import os
import xlrd
import json
import pdb
import MySQLdb


# 字典加载
def load_sta_data(filename):
    std_data_path = '{}{}'.format(os.path.dirname(os.path.abspath(__file__)), filename)
    sta = pd.read_csv(std_data_path)
    sta_tables = sta.as_matrix()
    return sta_tables

#  excle文件加载
def load_excel(filename, byindex=0):
    test_data = xlrd.open_workbook(filename,encoding_override='utf-8')
    sheet = test_data.sheets()[byindex]
    return sheet
    
# 数据字符替换
def cell_clear(cell):
    cell = cell.split("（")[0]
    cell = cell.split("(")[0]#.replace("1",'')
    cell = cell.replace('t','').replace(",","").replace(" ","").replace("“","").replace("<","").replace("，","").replace("\\",'').replace('\'','').replace('*','')
    return cell

# 判断字符串是否存在()
def str_replace(str):
    left = str.find('(')
    if left > 0:
        right = str.find(')')
        if right > 0:
            data = str[left+1:right]
            if data.isalpha():
                return data
    return str

# 数据清理
def data_clear(filename, sheetindex=0):
    # 指标识别成功之后存放到的数组
    matched_cell = []
    # 指标识别失败之后存放的数组
    unmatched_cell = []
    # 已经识别的指标行信息以 字典形式 ({行号：指标}) 信息录入 该数组中
    datainfo = []
    # 存在指标的列
    clos = []
    # 加载exlce文件
    data = load_excel(filename,sheetindex)
    # 每列
    for cloindex in range(data.ncols):
        # 第一列匹配到的指标
        first = []
        # 第二列匹配到的值
        sencde = []
        # 标记每列匹配到的数量
        flg = 0
        # 每行
        for rowindex in range(data.nrows):
            #　读取每一个单元格
            cell = str(data.row_values(rowindex)[cloindex]).encode('utf-8')
            # cell单元格
            cell = cell_clear(cell)
            # 在字典中进行查找单元格中的值是否存在
            if get_alias_count(cell):
                info = {}
                info.clear()
                # 坐标（行号）以及信息例如: "1":"白细胞"
                info[rowindex] = get_name_alias(cell)
                first.append(info)
                # 统计每一列有多少个已经匹配到的值
                flg += 1
        # 记录该列匹配到的列数
        if flg > 1:
            # 设置列的坐标
            clos.append(cloindex)
            # 将检索到的数据存放到自定义数组
            datainfo.append(first)
    # 处理数据
    length = len(datainfo)
    if length > 0:
        if length == 1:
            # 调用处理单列的函数
            single_row(datainfo,matched_cell,unmatched_cell,clos[0],data)
        elif length == 2:
            if clos[0]+1 != clos[1]:
                single_row(datainfo,matched_cell,unmatched_cell,clos[0],data)
                single_row(datainfo,matched_cell,unmatched_cell,clos[1],data)
            else:
                money_row(0,datainfo,matched_cell,unmatched_cell,clos[0],clos[1],data)
        else:
            if length % 2 != 0:
                print "1"
            else:
                # 升序排序
                arr = sorted(clos)
                arr1 = []
                for x in arr:
                    if x+1 in arr:
                        arr1.append(x)
                i = 0
                for y in arr1:
                    #import pdb; pdb.set_trace()
                    money_row(i,datainfo,matched_cell,unmatched_cell,y,y+1,data)
                    #print json.dumps(matched_cell, ensure_ascii=False, indent=4)
                    i=i+2
    info = extra_info(filename)
    data_info ={}
    data_info.clear()
    # 显示列
    data_info = {u"indicators":matched_cell,"extra_info":info,u"unknown_indicators":unmatched_cell}
    return data_info
    #print json.dumps(data_info, ensure_ascii=False, indent=4)

# 双列处理
def money_row(i,datainfo,matched_cell,unmatched_cell,first_clo,scond_clo,data):
    # 第一列指标信息
    arr1 = datainfo[i]
    # 第二列指标信息
    arr2 = datainfo[i+1]
    # 读取第一列的存在的指标的行存放到数组中
    rows1 = []
    for x in arr1:
        key1 = x.keys()[0]
        rows1.append(key1)
    # 读取第一列的存在的指标的行存放到数组中
    rows2 = []
    for x in arr2:
        key2 = x.keys()[0]
        rows2.append(key2)
    # 将俩列数组进行都进行升序排序,需要比较出俩个数组中最小的值作为数组遍历的开始,最大值作为数组遍历的结束标志
    rows1.sort()
    rows2.sort()
    # 默认开始为第一列行数组的第一位
    start = rows1[0]
    # 默认结束为第一列数组的最后一位
    end = rows1[len(rows1)-1]
    if rows1[0] > rows2[0] :
        start = rows2[0]
    if rows1[len(rows1)-1] > rows2[len(rows2)-1] :
        end = rows2[0]
    for x in range(start,end+1):
        #flg = False
        # 判断集合中的key原数据是否存在
        if x in rows1:
            for y in arr1:
                # 用于标识已经找到该数据不继续往下执行
                key = y.keys()[0]
                if x == key :
                    matched = {}
                    matched.clear()
                    info = str(data.row_values(x)[first_clo+2])
                    matched_name = y.get(key)
                    if info and matched_name:
                        matched[matched_name] = info
                        matched_cell.append(matched)
                        break
        # 判断集合中的key原数据是否存在
        elif x in rows2:
            for y in arr2:
                key = y.keys()[0]
                if x == key :
                    matched = {}
                    matched.clear()
                    info = str(data.row_values(x)[scond_clo+1])
                    matched_name = y.get(key)
                    if info and matched_name:
                        matched[matched_name] = info
                        matched_cell.append(matched)
                    break
        else:
            unmatched = {}
            unmatched.clear()
            unmatched_name = str(data.row_values(x)[first_clo])
            unmatched_info = str(data.row_values(x)[first_clo+2])
            if unmatched_name and unmatched_info :
                unmatched[unmatched_name] = unmatched_info
                unmatched_cell.append(unmatched)
            unmatched1 = {}
            unmatched1.clear()
            unmatched1_name = str(data.row_values(x)[scond_clo])
            unmatched1_info = str(data.row_values(x)[scond_clo+1])
            if unmatched_name and unmatched_info :
                unmatched1[unmatched1_name] = unmatched1_info
                unmatched_cell.append(unmatched1)
# 单列别名数据操作,参数为excle数据
def single_row(datainfo,matched_cell,unmatched_cell,clo,data):
    # 从已经识别的指标行信息读取第一个数组信息作为下面遍历单列的数组集合
    arr = datainfo[0]
    #　数据去重
    arrs = remove_repeat(arr)
    # 存放已经识别的指标信息的行数所存放的行号
    rows = []
    # 将数组集合中读取所有的行数
    for x in arrs:
        rows.append(x.keys()[0])
    # 指标值所存在的列ID
    # int(clo)=int(clo)+1
    # 将行数组进行升序 排序
    sort_rows = sorted(rows)
    #rows.sort()
    #print u"行数组为:"
    #print rows
    # 从行数组中读取第一个元素作为开始的标志
    start = rows[0]
    # 从行数组中读取最后一个元素作为结束的标志
    end = rows[len(rows)-1]
    # 利用start以及end 开始遍历
    for i in range(start,end+1):
        if i in rows:
            for j in arrs:
                # 数组中key值
                key = j.keys()[0]
                # 判断集合中的key原数据是否存在
                if key == i:
                    # 将匹配到的数据 按照字典的形式存放的 已识别指标的集合中
                    matched = {}
                    matched.clear()
                    #info = str(data.row_values(i)[clo+1]).encode('utf-8')
                    info = str(data.row_values(i)[clo+1])
                    if info :
                        # 读取数据
                        matched_name = j.get(key)
                        matched[matched_name] = info
                        matched_cell.append(matched)
                        break
        else:
            unmatched = {}
            unmatched.clear()
            #unmatched_name = str(data.row_values(i)[clo]).encode('utf-8')
            unmatched_name = str(data.row_values(i)[clo])
            #unmatched_info = str(data.row_values(i)[clo+1]).encode('utf-8')
            unmatched_info = str(data.row_values(i)[clo+1])
            if unmatched_name and unmatched_info :
                unmatched[unmatched_name] = unmatched_info
                unmatched_cell.append(unmatched)

# 列表去重,然后重新排序
def remove_repeat(data_list):
    arr = []
    # 跳出循环标志
    flg = False
    for x in data_list:
        key1 = x.keys()[0]
        name1 = x.get(key1)
        i = 0
        #import pdb; pdb.set_trace()
        for y in data_list:
            key2 = y.keys()[0]
            name2 = y.get(key2)
            if name1 == name2:
                i = i + 1
            if i > 1:
                flg = True
                break
            cell = {}
            # 清空处理
            cell.clear()
            cell[key2] = name2
            arr.append(cell)
        # 如果存在一个就跳出循环
        if flg:
            break
    return arr

# 读取身份信息
def extra_info(filename):
    peopleinfo = pd.read_excel(filename)
    tables = peopleinfo.as_matrix()
    age = ""
    sexy = ""
    check_time = ""
    report_time = ""
    name = ""
    hospital = ""
    for i in tables:
        for j in i:
            check_timepat = '(?:采.*?时间|检验日期|本采集时间|采样时间|核收时间).*?(\d{2,4}.*?\d{1,2}.*?\d{1,2})'.decode("utf8")
            sexypat = '男|女'.decode("utf8")
            agepat = '.*\d{1,}岁|年 龄.*\d{1,}|年齡.*\d{1,}|年龄.*\d{1,}|.*[男|女]\d{1,}'.decode("utf8")
            report_timepat = '报.*?[时间|日期].*?(\d{2,4}.*?\d{1,2}.*?\d{1,2})'.decode("utf8")
            namepat = '姓名.([\\u4e00-\\u9fa5]{2,4})'.decode("utf8")
            hospitalpat = '(.*医院)'.decode("utf8")
            try:
                if re.search(agepat,j):
                    age = re.search(agepat,j).group(0)
                    age=re.compile('\d{1,}').search(age).group(0)
            except:
                continue
            try:
                if re.search(sexypat,j):
                    sexy = re.search(sexypat,j).group(0)
            except:
                continue
            try:
                if re.search(check_timepat,j):
                    check_time = re.search(check_timepat,j).group(1)
            except:
                continue
            try:
                if re.search(report_timepat,j):
                    report_time = re.search(report_timepat,j).group(1)
            except:
                continue
            try:
                if re.search(namepat,j):
                    name = re.search(namepat,j).group(1)
            except:
                continue
            try:
                if re.search(hospitalpat,j):
                    hospital = re.search(hospitalpat,j).group(0)
            except:
                continue
    dict_word={u'姓名':name,u'性别':sexy,u'年龄':age,u'检验日期':check_time,u'报告日期':report_time,u'医院名称':hospital}
    return dict_word

from django.db import connection
# 通过别名在数据库进行查询是否存在
def get_alias_count (alias):
    
    sql = "select count(*) from medical_test_index_alias_dict where test_idx_alias = '"+alias+"'"
    cursor=connection.cursor()
    row = cursor.execute(sql)
    line_first = cursor.fetchone()
    data =  line_first[0]
    cursor.close()
    connection.close()
    if data > 0:
        return True
    return False

# 通过别名在数据库读取相对于的名字
def get_name_alias(alias):
    
    sql = "select test_idx_name from medical_test_index_alias_dict where test_idx_alias = '"+alias+"'"
    cursor=connection.cursor()
    row = cursor.execute(sql)
    line_first = cursor.fetchone()
    data =  line_first[0]
    cursor.close()
    connection.close()
    return data

if __name__ == '__main__':
    data_clear("E:/xls/5.xlsx")
    # 单列 5、6、8、9、13、24、2(无法识别 原因：中英文()有括号)、10(原因GBK无法编码)、(11 数据找不到)、14(找不到数据 原因：指标乱码)、16(原因：无法读取数据,GBK编码)、21(数据不全面)、(22 找不到数据 原因：有空列)、(23 找不到数据  原因：乱码)、
    # 双排 7 、17、19、
    # 中英文 1、25、
    # 11、12、14、15、18、19、20、23
    #arr99 = [1,2,5,6,7]
    #data_clear("E:\\xls\\1.xlsx")
    '''for i in arr99:
        print "ii->>"+str(i)
        str1 = "E:/xls/"+str(i)
        str1 = str1+".xlsx" 
        print str1
        data_clear(str1)'''
    # 没有数据：11、12、14、15、18、20、22、23、3
    # 有问题：4(数组越界)、10、(编码)、16(编码)、
    # 没有问题1、2、5、6、7、8、(9)、10(不全面)、13、17、19、21、24、