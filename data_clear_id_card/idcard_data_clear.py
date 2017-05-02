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
import docx2txt
import jieba
import jieba.posseg as pseg
import jieba.analyse

class result_info():
    result = ""
    result_data = ""

# 数据格式清洗
def data_clear(txt):
    txt = txt.replace(" ","")
    txt = txt.replace("\n", "")
    txt = txt.replace("\r", "")
    txt = txt.replace("\t", "")
    txt = txt.replace("丨", "")
    txt = txt.replace("|", "")
    txt = txt.replace("A","4")
    txt = txt.replace(" ","").replace("MWmHI","").replace("M","")
    txt = txt.strip("\r\n")
    txt = txt.lstrip("\r\n")
    txt = txt.rstrip("\r\n")
    return txt
# 主函数
def main(filename):
    try:
        return data_clear_main(filename)
    except Exception,e:
        print e
        data_info = list()
        dic = dict()
        dic["姓名"] = ""
        dic["公民身份号码"] = ""
        dic["性别"] = ""
        dic["出生"] = ""
        dic["住址"] = ""
        dic["参考地址"] = ""
        dic["民族"] = ""
        data_info.append(dic)
        return data_info
# 数据清理主函数
def data_clear_main(filename):
    # 文件转换
    txt = docx2txt.process(filename)

    txt = data_clear(txt)
    # 分词
    res1 = jieba_posseg(txt)
    data_info = list()
    dic = dict()

    name = get_name(txt,res1)
    dic["姓名"] = name

    id_card = get_idcard(txt)
    dic["公民身份号码"] = id_card.result
    #print  id_card.result_data

    dic["性别"] = get_sex(id_card.result)

    dic["出生"] = get_birthday(txt,id_card.result)

    dic["住址"] = get_address(txt)

    dic["参考地址"] = get_address_test(id_card=id_card.result)

    dic["民族"] = get_nation(txt)

    data_info.append(dic)
    #print get_sex(id_card.result)
    return data_info
# get_idcard
def get_idcard(ori=""):
    if not ori:
        return ""
    else:
        length = 18
        start = len(ori)
        start = start - length
        end = len(ori)
        id_card = ori[start:end]

        result_data = ori[0:ori.rfind("公")]
        result = result_info()
        result.result = id_card
        result.result_data = result_data

        return result
# get_sex
def get_sex(ori=""):
    # id_card length
    length = 18
    if not ori:
        return ""
    elif len(ori) == length :
        sex = "男"
        sex_id = int(ori[16:17])
        if sex_id > 0:
            if sex_id % 2 == 0:
                sex = "女"
        return sex

# get_address
# ori->SourceString
# str->SplitSTring
# id_card->idCard
def get_address(ori="",str="",id_card=""):
    if ori:
        start = ori.find("住址")
        if start == -1:
            start = ori.find("住")
            if start == -1:
                start = ori.find("址")
                if start != -1:
                    start = start + 1
            else:
                start = start + 2
        else:
            start = start + 2
        end = ori.find("公民身份号码")
        if end == -1:
            end = ori.find("公民身份号")
            if end == -1:
                end = ori.find("公民身份")
                if end == -1:
                    end = ori.find("公民身")
                    if end == -1:
                        end = ori.find("公民")
                        if end == -1:
                            end = ori.find("公")
        if end != -1 and start != -1:
            address = ori[start:end]
            return address
        return ""
    elif str:
        str.find("住址")
        pass
    elif id_card:
        pass
# get_address_test
def get_address_test(id_card=""):
    city_id = id_card[0:6]
    return ""
# get_address_idnex
#def get_address_index():

#get_nation
# ori --> sourceString
# str --> splitSTring
def get_nation(ori="",str=""):
    if ori:
        #import  pdb;pdb.set_trace()
        start = ori.find("民族")
        if start == -1:
            start1 = ori.find("民")
            start1_last = ori.rfind("民")
            if start1 == start1_last:
                start1 = -1
            start2 = ori.find("族")
            if start1 != -1 and start2 != -1 and start1 < start2 :
                start = start1 + 2
            elif start2 != -1 and start2 != -1 and start1 > start2:
                start = start2 + 1
            elif start1 == -1 and start2 != -1:
                start = start2 + 1
            elif start2 == -1 and start1 != -1:
                start = start2 + 2
        else:
            start = start + 2
        end = ori.find("出生")
        if end == -1:
            end1 = ori.find("出")
            end2 = ori.find("生")
            if end1 != -1 and end2 != -1 and end1 < end2 :
                end = end1
            elif end1 != -1 and end2 != -1 and end1 > end1 :
                end = end2 - 1
            elif end1 != -1 and end2 == -1:
                end = end1
            elif end2 != -1 and end1 == -1:
                end = end2 - 1
        nation = ""
        if start != -1 and end != -1:
            nation = ori[start:end]
            #print nation
        elif start != -1:
            nation = ori[start:start+1]
        elif end != -1:
            nation = ori[end-1:end]
        return nation
    elif str:
        pass

# get_birthday
def get_birthday(ori="",id_card=""):
    # id_card
    length = 18
    if not ori:
        return ""
    elif len(id_card) == length:
        # get birthday
        birthday = id_card[6:14]
        year = birthday[0:4]
        month = birthday[4:6]
        month = month.lstrip("0")
        day = birthday[6:len(birthday)]
        day = day.lstrip("0")
        bir = year+"年"+month+"月"+day+"日"
        return bir
# 读取名字
def get_name(ori="",textSeg=[]):
    if textSeg == []:
        return ""
    else:
        # 数据清洗
        ori = data_clear(ori)
        # jieba分词
        textSeg = jieba_posseg(ori)
        if ori.find("姓名".decode('utf-8')) != -1:
            # 如果包含姓名
            # 找出nr，n词性
            for (word,tag) in textSeg:
                if word == "姓名".encode('utf-8'):
                    # 开始
                    start = ori.find(word)
                    start = start + 2
                    # 判断性别是否存在
                    end = ori.find("性别".encode('utf-8'))
                    if end == -1:
                        end = ori.find("性".encode('utf-8'))
                    if end != -1 and start != -1:
                        return ori[start:end]
        elif ori.find("姓".decode('utf-8')) != -1:
            for (word,tag) in textSeg:
                if word == "姓".encode('utf-8'):
                    # 开始
                    start = ori.find(word)
                    start = start + 2
                    # 判断性别是否存在
                    end = ori.find("性别".encode('utf-8'))
                    if end == -1:
                        end = ori.find("性".encode('utf-8'))
                    if end != -1 and start != -1:
                        return ori[start:end]
        elif ori.find("名".decode('utf-8')) != -1:
            for (word,tag) in textSeg:
                if word == "名".encode('utf-8'):
                    # 开始
                    start = ori.find(word)
                    start = start + 1
                    # 判断性别是否存在
                    end = ori.find("性别".encode('utf-8'))
                    if end == -1:
                        end = ori.find("性".encode('utf-8'))
                    if end != -1 and start != -1:
                        return ori[start:end]
        return ""
# jieba分词
def jieba_posseg(text):
    seg_list = pseg.cut(text)
    res_list = []
    for w in seg_list:
        res_list.append([w.word,w.flag])
    return res_list

if __name__ == "__main__":
    #path = "testdata/Id_card_20170502114310_4159.jpg.docx"
    #data = data_clear_main(path)
    #data = main(path)
    #print json.dumps(data,ensure_ascii=False,indent=4)
    #print data
    #print json.dumps(data,ensure_ascii=False,indent=4)
    #datainfo = ""l
    #lis = list()
    #for i in range(1,7):
        #path = 'testdata/'+str(i)+'.docx'
        #data = data_clear_main(path)
        #print json.dumps(data,ensure_ascii=False,indent=4)
    #print json.dumps(lis,ensure_ascii=False,indent=4)
        #datainfo = datainfo + str(data)+"\n"
    #open('data.txt','w').write(str(datainfo))
    pass