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
import MySQLdb
import jieba
import jieba.posseg as pseg
import Levenshtein

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

# 指标值替换
def cell_data_clear(cell):
    cell = cell.replace('t','').replace('i','').replace(' ','').replace('\\','').replace(".“",'').replace(" ",'')
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
    datainfo = dict()
    datainfo.clear()
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
            try:
                #　读取每一个单元格encode(“GBK“, ‘ignore’);
                cell = str(data.row_values(rowindex)[cloindex]).decode('utf-8')
            except Exception,e:
                print e
            # cell单元格
            cell = cell_clear(cell)
            # 在字典中进行查找单元格中的值是否存在
            if get_name(cell):
                name = get_name(cell)
                if name:
                    info = {}
                    info.clear()
                    # 坐标（行号）以及信息例如: "1":"白细胞"
                    info[rowindex] = name
                    first.append(info)
                    # 统计每一列有多少个已经匹配到的值
                    flg += 1
        # 记录该列匹配到的列数
        if flg >= 2:
            # 设置列的坐标
            clos.append(cloindex)
            # 将检索到的数据存放到自定义数组
            datainfo[cloindex]=first
            #datainfo.append(dic)
    # 判断ｄｉｃｔ的长度推算出有已经识别出多少列
    length = len(datainfo)
    if length > 0:
        # 读取所有存在指标的列的编号
        data_clos = datainfo.keys()
        money_row_arr = []
        un_monkey_row_arr = []
        single_row_arr = []
        arr = sorted(data_clos)
        if len(data_clos) % 2 == 0:
            for clo in arr:
                # 判断双列的情况是否存在
                if clo + 1 in arr:
                    # 将存在双列的列号存入数组中
                    money_row_arr.append(clo)
                    un_monkey_row_arr.append(clo + 1)
                # 存放但列
                elif clo not in un_monkey_row_arr:
                    single_row_arr.append(clo)
            # 处理双列
            for clo in money_row_arr:
                # 调用处理双列的方法 clo--> 存在指标的列编号,datainfo --> 指标信息 matched_cell -->　已经识别的指标信息 unmatched_cell -->　没有识别的指标信息
                money_row(clo, datainfo, matched_cell, unmatched_cell, data)
            # 处理单列
            for clo in single_row_arr:
                single_row(datainfo, matched_cell, unmatched_cell, clo, data)
        elif len(data_clos) % 2 != 0:
            for clo in arr:
                # 判断双列的情况是否存在
                if clo+1 in arr:
                    # 将存在双列的列号存入数组中
                    money_row_arr.append(clo)
                    un_monkey_row_arr.append(clo+1)
                # 存放但列
                elif clo not in un_monkey_row_arr:
                    single_row_arr.append(clo)
            # 处理双列
            for clo in money_row_arr:
                #调用处理双列的方法 clo--> 存在指标的列编号,datainfo --> 指标信息 matched_cell -->　已经识别的指标信息 unmatched_cell -->　没有识别的指标信息
                money_row(clo, datainfo, matched_cell, unmatched_cell, data)
            # 处理单列
            for clo in single_row_arr:
                single_row(datainfo, matched_cell, unmatched_cell, clo, data)
    info = extra_info(filename)
    data_info ={}
    data_info.clear()
    # 显示列
    data_info = {u"indicators":matched_cell,"extra_info":info,u"unknown_indicators":unmatched_cell}
    return data_info


# 双列处理
def money_row(clo,datainfo,matched_cell,unmatched_cell,data):
    first_clo = clo
    scond_clo = clo + 1
    # 第一列指标信息
    arr1 = datainfo.get(first_clo)
    # 第二列指标信息
    arr2 = datainfo.get(scond_clo)
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
        try:
            if x in rows1:
                for y in arr1:
                    # 用于标识已经找到该数据不继续往下执行
                    key = y.keys()[0]
                    if x == key :
                        matched = {}
                        matched.clear()
                        #info = str(data.row_values(x)[first_clo+2])
                        info = cell_data_clear(data.row_values(x)[first_clo+2])
                        matched_name = y.get(key)
                        if info and matched_name:
                            matched[matched_name] = info
                            matched_cell.append(matched)
                            break
                        else:
                            info1 = cell_data_clear(data.row_values(x+1)[first_clo+2])
                            info2 = cell_data_clear(data.row_values(x+2)[first_clo+2])
                            if not info1 and not info2:
                                info = cell_data_clear(data.row_values(x)[first_clo+3])
                                if info:
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
                        info = cell_data_clear(data.row_values(x)[scond_clo+1])
                        matched_name = y.get(key)
                        if info and matched_name:
                            matched[matched_name] = info
                            matched_cell.append(matched)
                            break
                        else:
                            info1 = cell_data_clear(data.row_values(x+1)[first_clo+1])
                            info2 = cell_data_clear(data.row_values(x+2)[first_clo+1])
                            if not info1 and not info2:
                                info = cell_data_clear(data.row_values(x)[first_clo+2])
                                if info:
                                    matched[matched_name] = info
                                    matched_cell.append(matched)
                                    break
            else:
                unmatched = {}
                unmatched.clear()
                unmatched_name = str(data.row_values(x)[first_clo])
                unmatched_info = cell_data_clear(data.row_values(x)[scond_clo+2])
                if unmatched_name and unmatched_info :
                    unmatched[unmatched_name] = unmatched_info
                    unmatched_cell.append(unmatched)
                else:
                    unmatched_info1 = cell_data_clear(data.row_values(x+1)[scond_clo+2])
                    unmatched_info2 = cell_data_clear(data.row_values(x+2)[scond_clo+2])
                    if not unmatched_info1 and not unmatched_info2:
                        unmatched_info = cell_data_clear(data.row_values(x)[scond_clo+3])
                        unmatched[unmatched_name] = unmatched_info
                        unmatched_cell.append(unmatched)
                        break
                unmatched1 = {}
                unmatched1.clear()
                unmatched1_name = str(data.row_values(x)[scond_clo])
                unmatched1_info = cell_data_clear(data.row_values(x)[scond_clo+1])
                if unmatched_name and unmatched_info :
                    unmatched1[unmatched1_name] = unmatched1_info
                    unmatched_cell.append(unmatched1)
                else:
                    unmatched_info1 = cell_data_clear(data.row_values(x+1)[scond_clo+1])
                    unmatched_info2 = cell_data_clear(data.row_values(x+2)[scond_clo+1])
                    if not unmatched_info1 and not unmatched_info2:
                        unmatched_info = cell_data_clear(data.row_values(x)[scond_clo+2])
                        unmatched[unmatched_name] = unmatched_info
                        unmatched_cell.append(unmatched)
                        break
        except Exception:
            pass

# 单列别名数据操作,参数为excle数据
def single_row(datainfo,matched_cell,unmatched_cell,clo,data):
    # 从已经识别的指标行信息读取第一个数组信息作为下面遍历单列的数组集合
    arr = datainfo.get(clo)
    # 存放已经识别的指标信息的行数所存放的行号
    rows = []
    # 将数组集合中读取所有的行数
    for x in arr:
        rows.append(x.keys()[0])
    # 将行数组进行升序 排序
    sort_rows = sorted(rows)
    # 从行数组中读取第一个元素作为开始的标志
    start = rows[0]
    # 从行数组中读取最后一个元素作为结束的标志
    end = rows[len(rows)-1]
    # 利用start以及end 开始遍历
    for x in range(start,end+1):
        # 判断生成行是否在原有的行中存在
        if x in rows:
            # 遍历数据读取指标名词
            for y in arr:
                key = y.keys()[0]
                #
                if key == x :
                    # 将匹配到的数据 按照字典的形式存放的 已识别指标的集合中
                    matched = {}
                    matched.clear()
                    # 指标名
                    matched_name = y.get(key)
                    # 指标值
                    matched_info = str(data.row_values(x)[clo + 1])
                    if matched_name and matched_info :
                        # 读取数据
                        matched[matched_name] = matched_info
                        matched_cell.append(matched)
                        break
                    elif matched_name and not matched_info:
                        info1 = data.row_values(x + 1)[clo + 1]
                        info2 = data.row_values(x + 2)[clo + 1]
                        # 如果该行之后的第一行和第二行都为空,就读取该行之后的一列
                        if not info1 and not info2:
                            matched_info = str(data.row_values(x)[clo + 2])
                            # 判断该行之后的一列是否有值
                            if matched_info :
                                matched[matched_name] = matched_info
                                matched_cell.append(matched)
                                break;
            # 如果指标不存在将该信息存入未识别的指标里
            else:
                unmatched = {}
                unmatched.clear()
                unmatched_name = str(data.row_values(x)[clo])
                unmatched_info = str(data.row_values(x)[clo + 1])
                if unmatched_name and unmatched_info:
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
    data = load_excel(filename,0)
    age = ""
    sexy = ""
    check_time = ""
    report_time = ""
    name = ""
    hospital = ""
    check_timepat = '(?:采.*?时间|检验日期|本采集时间|采样时间|核收时间).*?(\d{2,4}.*?\d{1,2}.*?\d{1,2})'.decode("utf8")
    sexypat = '男|女'.decode("utf8")
    agepat = '.*\d{1,}岁|年 龄.*\d{1,}|年齡.*\d{1,}|年龄.*\d{1,}|.*[男|女]\d{1,}'.decode("utf8")
    report_timepat = '报.*?[时间|日期].*?(\d{2,4}.*?\d{1,2}.*?\d{1,2})'.decode("utf8")
    namepat = '姓名.([\\u4e00-\\u9fa5]{2,4})'.decode("utf8")
    hospitalpat = '(.*医院)'.decode("utf8")
    # 每列
    for cloindex in range(data.ncols):
        # 每行
        for rowindex in range(data.nrows):
            try:
                #　读取每一个单元格encode(“GBK“, ‘ignore’);
                cell = str(data.row_values(rowindex)[cloindex]).decode('utf-8')
                if cell:
                    cell = cell.replace(" ","")
                    if not age:
                        if re.search(agepat,cell):
                            age = re.search(agepat,cell).group(0)
                            age = re.compile('\d{1,}').search(age).group(0)
                            #continue
                    if not sexy:
                        if re.search(sexypat,cell):
                            sexy = re.search(sexypat,cell).group(0)
                            #continue
                    if not check_time:
                        if re.search(check_timepat,cell):
                            check_time = re.search(check_timepat,cell).group(1)
                            #continue
                    if not report_time:
                        if re.search(report_timepat,cell):
                            report_time = re.search(report_timepat,cell).group(1)
                            #continue
                        else:
                            if cell.find("姓名") != -1:
                                textSeg = jieba_posseg(cell)
                                for (word,tag) in textSeg:
                                    if word == u"姓名":
                                        continue
                                    if tag in ["nr", "n"] and flag:
                                        candidate.append(word)
                                #截取候选词前后的词
                                for can in candidate:
                                    start = ori.find(can) - 5
                                    end = start + 5
                                    if ori[start : end].find("姓名".decode('utf-8')) != -1:
                                        # 找到
                                        name = can
                    if not name:
                        #import pdb; pdb.set_trace()
                        if re.search(namepat,cell):
                            name = re.search(namepat,cell).group(1)
                            #continue
                    if not hospital:
                        if re.search(hospitalpat,cell):
                            hospital = re.search(hospitalpat,cell).group()
                            #continue
            except Exception,e:
                print e
    
    dict_word={u'姓名':name,u'性别':sexy,u'年龄':age,u'检验日期':check_time,u'报告日期':report_time,u'医院名称':hospital}
    return dict_word

from django.db import connection
# 通过别名在数据库进行查询是否存在
def get_alias_count (alias):
    #connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='root',db='medical_basic',port=3306,charset='utf8')
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
    #connection=MySQLdb.connect(host='127.0.0.1',user='root',passwd='root',db='medical_basic',port=3306,charset='utf8')
    sql = "select test_idx_name from medical_test_index_alias_dict where test_idx_alias = '"+alias+"'"
    cursor=connection.cursor()
    row = cursor.execute(sql)
    line_first = cursor.fetchone()
    if line_first > 0 :
        return line_first[0]
    cursor.close()
    connection.close()
    return ""

# 读取指标名
def get_name(cell=""):
    if cell:
        name = ""
        #　从数据库中进行匹配
        name = get_name_alias(cell)
        if name :
            return name
        # 判断该ｃｅｌｌ中是否存在中文
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        match = zh_pattern.search(cell)
        if match :
            #connection = MySQLdb.connect(host='127.0.0.1', user='root', passwd='root', db='medical_basic', port=3306,charset='utf8')
            sql = "select test_idx_name,test_idx_alias from medical_test_index_alias_dict"
            cursor = connection.cursor()
            rows = cursor.execute(sql)
            # 读取数据库中所有记录,已key(别名)->value(标准名)的形式存入字典中
            dic_key = dict()
            for row in cursor.fetchall():
                dic_key[row[1]] = row[0]
            # 所有的别名信息用来与cell进行编辑距离的匹配
            keys = dic_key.keys()
            dic_result = dict()
            # 遍历所有的别名信息与cell进行编辑距离匹配
            for key_data in keys:
                id = Levenshtein.distance(str(cell),str(key_data))
                if id <= 2:
                    dic_result[key_data] = id
            # 读取匹配后的距离,然后读取信息
            arr_id = dic_result.values()
            if len(arr_id) > 0:
                arr_id.sort()
                id = arr_id[0]
                for dic in dic_result:
                    if id == dic_result[dic]:
                        name = dic_key.get(dic)
            return name
    return ""
#方法-jieba词性标注
#传入-txt字符串
#输出-结果列表=[ [词，词性] ... ...]
def jieba_posseg(txt):
    seg_list = pseg.cut(txt)
    res_list = []
    for w in seg_list:
        res_list.append([w.word,w.flag])
    return res_list

if __name__ == '__main__':
    #prefix_20170425163447_1707.jpg.xls
    #data = data_clear("data_clear_test/17.xlsx")
    #print json.dumps(data,ensure_ascii=False,indent=4)
    #get_name()
    # 单列 5、6、8、9、13、24、2(无法识别 原因：中英文()有括号)、10(原因GBK无法编码)、(11 数据找不到)、14(找不到数据 原因：指标乱码)、16(原因：无法读取数据,GBK编码)、21(数据不全面)、(22 找不到数据 原因：有空列)、(23 找不到数据  原因：乱码)、
    # 双排 7 、17、19、
    # 中英文 1、25、
    # 11、12、14、15、18、19、20、23
    #arr99 = [1,2,5,6,7,8,9,10,13,17,19,21,24]
    #data_clear("E:\\xls\\1.xlsx")
    '''files = os.listdir("data_clear_test/")
    file_name = []
    str_name = ["xls","xlsx"]
    for file in files:
        index = str(file).rindex(".")
        if index != -1:
            star = str(file)[index+1:len(file)]
            if star in str_name:
                file_name.append(file)
    for file_path in file_name:
        print file_path
        file_path_info = "data_clear_test/"+file_path
        try:                                                                                                                                                                                                                                                                    
            data = data_clear(file_path_info)
            file_data = open(file_path+".txt", "w")
            file_data.write(json.dumps(data, ensure_ascii=False, indent=4))
            print  file_path+".txt-->ok"
            file_data.close()
        except:                                                                                                                     
            print file_path+"-->err"
            pass'''
    '''for i in range(1,24):                                                                            
        print "ii->>"+str(i)
        str1 = "data_clear_test/"+str(i)
        str1 = str1+".xlsx"
        print str1
        file_name = str(i)+".txt"
        try:
            data = data_clear(str1)
            file_data = open(file_name,"w")
            file_data.write(json.dumps(data,ensure_ascii=False,indent=4))
            print  file_name+"-->ok"
            file_data.close()
        except:
            print  file_name + "-->err"
            pass'''