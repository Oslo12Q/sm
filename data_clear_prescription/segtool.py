# coding=utf-8
import re
import os
import string
import codecs
from io import StringIO
import jieba
import jieba.posseg as pseg
import sys
import jieba.analyse


#jieba分词工具初始化
#设定字典及加载用户自定义字典
def jieba_init():
    jieba.set_dictionary("UserDict.txt")
    jieba.load_userdict("UserDict.txt")
    #jieba.enable_parallel(4)

#方法-jieba词性标注
#传入-txt字符串
#输出-结果列表=[ [词，词性] ... ...]
def jieba_posseg(txt):
    seg_list = pseg.cut(txt)
    res_list = []
    for w in seg_list:
        res_list.append([w.word,w.flag])
    return res_list

def jieba_keyword(sentence,top,ifweight= True):
    #keyword_list = list(jieba.analyse.extract_tags(sentence,topK = top,withWeight = ifweight))
    keyword_list = list(jieba.analyse.textrank(sentence,topK= top,withWeight= ifweight))
    #print(keyword_list)
    return keyword_list

#添加球队球员名到自定义字典中
def jieba_addname_to_dict(teamclass):
    f = codecs.open("UserDict.txt","r",encoding = "utf-8")
    content = f.read()
    f.close()
    f = codecs.open("UserDict.txt","a",encoding = "utf-8")
    for item in teamclass.playerdatadic:
        for p in re.split(r"[\s\·\-\']+",item["球员名"]):
            if content.find(p) == -1:
                f.write("%s %d %s\r\n" % (p,10000,"nr"))
        #jieba.add_word(item["球员名"],freq = 10000,tag = "nr")
        #jieba.suggest_freq("",True)
        #print("add %s to dict" % item["球员名"])
    f.write("%s %d %s\r\n" % (teamclass.name,10000,"nr"))
    f.close()
    print("add %s to dict" % teamclass.name)