# -*- coding: utf-8 -*-

import string
import re
from segtool import *
from tool import  *


def name(ori = "", textSeg=[]):#传入分词结果
    if textSeg == []:
        pass
    else:
        ori = wash_data(ori)
        textSeg = jieba_posseg(ori)
        #print(textSeg)
        #候选词列表
        candidate = []
        if ori.find("姓名".decode('utf-8')) != -1:
            # 如果包含姓名
            #找出nr，n词性
            flag = False
            for (word,tag) in textSeg:
                if word == u"姓名":
                    flag = True
                    continue
                if tag in ["nr", "n"] and flag:
                    candidate.append(word)
            #截取候选词前后的词
            for can in candidate:
                start = ori.find(can) - 5
                end = start + 5
                if ori[start : end].find("姓名".decode('utf-8')) != -1:
                    #找到
                    return can
                else:
                    if ori[start : end].find("医师".decode('utf-8')) == -1 or ori[start : end].find("医生".decode('utf-8')) == -1:
                        #姓名词条不包含"医生"或"医师"
                        return candidate[0]
                    else:
                        continue
        else:
            #不包含姓名关键词
            for (word,tag) in textSeg:
                if tag in ["nr"]:
                    candidate.append(word)
            #截取候选词前后的词
            for can in candidate:
                start = ori.find(can) - 2
                end = start + len(can) + 2
                wat = ori[start: end]
                if ori[start : end].find("医师".decode('utf-8')) == -1 and ori[start : end].find("医生".decode('utf-8')) == -1:
                    #姓名词条不包含"医生""医师"
                    return can
        return ""


def age(ori = "", textSeg = [["",""]]):
    if textSeg == []:
        pass
    else:
        #候选词
        candidate = ""
        #找出年龄或岁
        start = -1
        end = -1
        for (w,_) in enumerate(textSeg):
            if textSeg[w][0] == u"年龄" or textSeg[w][0] == u"龄":
                start = w
            if textSeg[w][0] == u"岁" :
                end = w

        if start < end and start != -1 and end != -1 and (end - start) < 6:
            #年龄、岁关键词存在
            for w in range(start, end + 1):
                if textSeg[w][1] in ["n", "m"]:
                    candidate += textSeg[w][0]
        elif start == -1 :
            #年龄不存在，岁存在
            end -= 1
            while():
                if textSeg[end][1] == u"m":
                    candidate = textSeg[end][0]
                    break
                end -= 1
        elif end == -1 :
            #年龄存在，岁不存在
            start += 1
            while True:
                if textSeg[start][1] == u"m":
                    candidate = textSeg[start][0]
                    break
                start += 1

        #处理candidate
        if candidate != "" :
            return re.compile(r"\d+").findall(candidate)[0]
        else:
            return ""

def sex(ori = "", textSeg = [["",""]]) :
    if textSeg == []:
        pass
    else:
        #候选词列表
        candidate = []
        #找出b词性
        for (word,tag) in textSeg:
            if tag == u"n" and word == u"性别":
                candidate.append(word)
        #截取候选词后的词
        for can in candidate:
            start = ori.find(can)
            end = start + 5
            if ori[start : end].find("男".decode('utf-8')) != -1:
                #找到
                return "男"
            elif ori[start : end].find("女".decode('utf-8')) != -1:
                #找到
                return "女"
            else:
                continue
        return ""

def hospital(ori = "", textSeg = [["",""]]):
    if textSeg == []:
        pass
    else:
        # 候选词
        candidate = ""
        # 找出年龄或岁
        start = -1
        end = -1
        for (w, _) in enumerate(textSeg):
            if textSeg[w][0].find("医院".decode('utf-8')) != -1:
                end = w
                break

        while True:
            if textSeg[end][1] != u"x" :
                #词性不为x时
                candidate = textSeg[end][0] + candidate
                end -= 1
            elif textSeg[end][1] == u"x":
                #词性为x时，例外情况
                if textSeg[end][0] == u"〇":
                    candidate = textSeg[end][0] + candidate
                    end -= 1
                else:
                    break

        return candidate


def times(ori = "", textSeg = ''):
    y = -1
    m = -1
    d = -1
    for (n,c) in enumerate(textSeg):
        if c[0] == u"年":
            y = n
        if c[0] == u"月":
            m = n
        if c[0] == u"日":
            d = n

    if y != -1 and m != -1 and c != -1:
        strs = ""
        for x in range(y - 2, d):
            strs += textSeg[x][0]
        l = exfromstr(strs,num= 3)
        return l[0]+l[1]+l[2]
    else:
        for (n, c) in enumerate(textSeg):
            if c[0].find("日期".decode('utf-8')) != -1:
                strs = ""
                for x in range(n, n + 8):
                    strs += textSeg[x][0]
                l = exfromstr(strs, num=3)
                return l[0] + l[1] + l[2]
    return ""
