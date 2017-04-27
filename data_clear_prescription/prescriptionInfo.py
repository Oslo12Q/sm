# -*- coding: utf-8 -*-
from segtool import *
from tool import  *


def diagnose(text, basicList, diagPath):
    if text != "":
        #将text中已经提取的内容删除
        for word in basicList:
            if isinstance(word,str):
                word = word.decode('utf-8')
            if isinstance(text,str):
                text = text.decode('utf-8')
            text.replace(word,"\n")
        diagText = ""
        sentence = re.split(r"[\r+\n+\s+\t+]", text)
        # 拼接sentence
        retext = ""
        for word in sentence:
            retext += word + ","
        # retext 分词
        #划分句子
        retext = re.split(r"[\,\，\.\。]",retext)

        #打开Diag文本，读取诊断关键词
        f = codecs.open(diagPath, "r",encoding="utf-8")
        content = f.read()
        f.close()
        contentList = re.split(r"[\r\n]",content)

        diag = ""
        for sent in retext:
            if len(sent) > 0:
                if sent.find("诊断".decode('utf-8')) != -1:
                    # 存在"诊断"关键字
                    diag += sent
                    continue
                else:
                    sent_seg = jieba_posseg(sent)
                    for (word,p) in sent_seg:
                        if word in contentList or content.find(word) != -1:
                            diag += sent
                            break
        return diag
    else:
        return ""

def medicine(text, basicList, drugPath):
    if text != "":
        # 将text中已经提取的内容删除
        for word in basicList:
            if word != "":
                if isinstance(word, str):
                    word = word.decode('utf-8')
                if isinstance(text, str):
                    text = text.decode('utf-8')
                text = text.replace(word, ",")
        diagText = ""
        sentence = re.split(r"[\r\n\s\t]+", text)
        # print("sentence:",sentence)
        # 拼接sentence
        retext = ""
        for word in sentence:
            retext += word + ","
        # retext 分词
        # 划分句子
        retext = re.split(r"[\,\，\.\。]", retext)

        # 打开Drug文本，读取诊断关键词
        f = codecs.open(drugPath, "r", encoding="utf-8")
        content = f.read()
        f.close()
        contentList = re.split(r"[\r\n]", content)

        drug = ""
        index = list()
        # 查找药品的起止段
        for (num,sent) in enumerate(retext):
            if len(sent) > 0:
                sent_seg = jieba_posseg(sent)
                wordlist = list()
                for word in sent_seg:
                    wordlist.append(word[0])
                    if isDiagOrDrug(wordlist,contentList):
                        index.append(num)
                        break
        # 截取
        if len(index) != 0:
            cut = list()
            for sent in range(index[-1],len(retext)):
                for word in ["医师","医生","金额","费用","合计","总计","收费"]:
                    if retext[sent].find(word.decode('utf-8')) != -1:
                        cut.append(sent)
            cut.sort()
            if len(cut) != 0:
                for sent in range(index[0],cut[0]):
                    try:
                        drug += retext[sent] + ","
                    except:
                        break
            else:
                for sent in range(index[0],index[-1]+1):
                    try:
                        drug += retext[sent] + ","
                    except:
                        break
        return drug


def isDiagOrDrug(text = [""], list = [""]):
    for word in text:
        if word in list:
            return True
        else:
            return False
