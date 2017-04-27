# -*- coding: utf-8 -*-
import re
import numpy as np
#import lda
#import lda.datasets
import codecs

#方法-数据清洗
def wash_data(text = ""):
    #数据清洗
    text = text.replace(" ","")
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = text.replace("\t", "")
    text = text.replace("丨", "")
    text = text.replace("|", "")
    #数据清洗完毕
    return text

#从字符串中提取信息
def exfromstr(source = "", ext = "num", num = 0):
    sour = source
    res = []
    if  ext == "num":
        #提取数字
        for char in sour:
            if char.isnumeric() == False:
                sour = sour.replace(char, " ")
        #split
        strList = re.split(r"\s+",sour)
        for char in strList:
            if num !=0 and char.isdigit() == True:
                res.append(char)
                num -= 1
    while num != 0:
        res.append("")
        num -= 1
    return res

#生成词语字典，保存在dict.txt中
def word_to_dict(textSeg= [["",""]]):
    f = codecs.open("dict.txt","r",encoding = "utf-8")
    content = f.read()
    f.close()
    contentList = re.split(r"[\n\r]",content)
    f = codecs.open("dict.txt","a",encoding = "utf-8")
    for [word,p] in textSeg:
            if word not in contentList and p not in ["x"]:
                f.write("%s\r\n" % word)
    f.close()
    return True

#统计每篇文章，各个词出现的次数
def wordCount(textSeg= [["",""]]):
    #读dict.txt
    f = codecs.open("dict.txt", "r", encoding="utf-8")
    content = f.read()
    f.close()
    contentList = re.split(r"[\r\n]",content)

    #统计textSeg里的词频
    a = dict()
    for [word,p] in textSeg:
        if p not in ["x"]:
            if a.get(word) == None:
                #不存在,添加
                a[word] = 1
            else:
                a[word] += 1
    return a

#生成词语-文章矩阵，矩阵中元素为某文某词出现次数
def wordtext_to_matrix():
    pass