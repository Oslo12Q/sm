# -*- coding: utf-8 -*-

from tool import *
from segtool import *

def department(ori = "", textSeg = [["",""]], departPath = "") :
    if textSeg == []:
        pass
    else:
        #候选词列表
        candidate = []
        #找出b词性
        for (word,tag) in textSeg:
            if word in [u"科室", u"诊室"]:
                candidate.append(word)
        #截取候选词后的词
        if len(candidate) == 0:
            f = codecs.open(departPath, "r",encoding="utf-8")
            content = f.read()
            f.close()
            contengList = re.split(r"\r\n",content)
            for (word,p) in textSeg:
                if word in contengList:
                    return word
        for can in candidate:
            start = ori.find(can)
            end = start + 10
            segment = jieba_posseg(ori[start + len(can): end])
            departments = ""
            for x in segment:
                if x[1].find("n") != -1:
                    departments += x[0]
            return departments
        return ""

def doctor(ori = "", textSeg = [["",""]]):#传入分词结果
    if textSeg == []:
        pass
    else:
        ori = wash_data(ori)
        textSeg = jieba_posseg(ori)
        #print(textSeg)
        #候选词列表
        candidate = []
        if ori.find("医师".decode('utf-8')) != -1 or ori.find("医生".decode('utf-8')):
            # 如果包含姓名
            #找出nr，n词性
            flag = False
            for (word,tag) in textSeg:
                if word == u"医师" or word == u"医生":
                    flag = True
                    continue
                if tag in ["nr", "n"] and flag:
                    candidate.append(word)
                    break
            #截取候选词前后的词
            for can in candidate:
                start = ori.find(can) - 5
                end = start + 5
                if ori[start : end].find("医师".decode('utf-8')) != -1 or ori[start : end].find("医生".decode('utf-8')) != -1:
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
                if ori[start : end].find("医师".decode('utf-8')) != -1 or ori[start : end].find("医生".decode('utf-8')) != -1:
                    #姓名词条不包含"医生"或"医师"
                    return can
                else:
                    continue
        return ""

def cost(ori = "", textSeg = [["",""]]):
    if textSeg == []:
        pass
    else:
        #数据清洗
        ori = wash_data(ori)
        textSeg = jieba_posseg(ori)

        # 候选词列表
        candidate = []
        # 找出b词性
        for (word, tag) in textSeg:
            if word in [u"金额", u"费用", u"总计", u"合计"]:
                candidate.append(word)
        # 截取候选词后的词
        for can in candidate:
            start = ori.find(can)
            end = start + len(can) + 10
            segment = ori[start+len(can):end]
            costs = re.compile(r"[0-9\.]+").findall(segment)
            try:
                return costs[0]
            except:
                return ""
        return ""