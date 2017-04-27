#!/usr/bin/python
#-*- coding: UTF-8 -*- 
#coding=utf-8

import docx2txt
import os.path
import time
from basicInfo import *
from prescriptionInfo import *
from otherInfo import *
from segtool import *
import json
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


class handlePrescription(object):
    def __init__(self):
        self.diagPath = "C:\\repos3\\sm\\data_clear_prescription" + "\\" + "Diagnosis.txt"
        self.drugPath = "C:\\repos3\\sm\\data_clear_prescription" + "\\" + "DrugNames.txt"
        self.depaPath = "C:\\repos3\\sm\\data_clear_prescription" + "\\" + "DepartmentNames.txt"
        self.inputPath = "C:\\repos3\\sm\\data_clear_prescription" + "\\" + "input"
        self.outputPath = "C:\\repos3\\sm\\data_clear_prescription" + "\\" + "output"
        self.fileIndex = []
        self.infoDict = dict()

    def getfileindex(self):
        try:
            for parent, dirname, filename in os.walk(self.inputPath):
                for file in filename:
                    if file.find(".docx") != -1 or file.find(".doc") != -1:
                        self.fileIndex.append(file)
        except:
            print("inputPath路径错误!")

    def handleWithFile(self,each):
        path = os.path.join(self.inputPath, each)
        text = docx2txt.process(path)
        # 分词
        res1 = jieba_posseg(text)
        basicList = list()
        self.infoDict["name"] = name(text, res1)
        basicList.append(self.infoDict["name"])

        self.infoDict["age"] = age(text, res1)
        basicList.append(self.infoDict["age"])

        self.infoDict["sex"] = sex(text, res1)
        basicList.append(self.infoDict["sex"])

        self.infoDict["hospital"] = hospital(text, res1)
        basicList.append(self.infoDict["hospital"])

        self.infoDict["times"] = times(text, res1)
        basicList.append(self.infoDict["times"])

        self.infoDict["doctor"] = doctor(text, res1)
        basicList.append(self.infoDict["doctor"])

        self.infoDict["department"] = department(text, res1, self.depaPath)
        basicList.append(self.infoDict["department"])

        self.infoDict["cost"] = cost(text, res1)
        basicList.append(self.infoDict["cost"])

        self.infoDict["diagnose"] = diagnose(text, basicList, self.diagPath)
        self.infoDict["medicine"] = medicine(text, basicList, self.drugPath)


    def handle(self,filenames=None):
        self.infoDict = {}
        result = {
            "prescription_information":[
                {
                    "诊断描述":""
                },
                {
                    "药物信息":""
                }
            ],
            "issential_information":{
                "姓名":"",
                "年龄":"",
                "性别":"",
                "医院":"",
                "时间":"",
                "医师":"",
                "科室":"",
                "费用":""
            }
        }
        import zipfile
        print filenames
        filename = zipfile.ZipFile(filenames)
        print filename
        if not filename:
            if self.fileIndex:
                currTime = time.strftime(r"%Y-%m-%d %H.%M.%S", time.localtime())
                try:
                    with open(os.path.join(self.outputPath, currTime + ".txt"), "a") as out:
                        temp = "文件编号\t姓名\t年龄\t性别\t医院\t时间\t医师\t科室\t费用\t诊断\t处方\n"
                        out.writelines(temp)
                        # 写CSV文件首行
                        for each in self.fileIndex:
                            self.handle(each)
                            out.write(each.encode('GBK'))
                            print self.infoDict
                            out.write('\t')
                            temp_list = [self.infoDict.get("name"), self.infoDict.get("age"), self.infoDict.get("sex"), self.infoDict.get("hospital"),
                                         self.infoDict.get("times"), self.infoDict.get("doctor"), self.infoDict.get("department"),
                                         self.infoDict.get("cost"),
                                         self.infoDict.get("diagnose"), self.infoDict.get("medicine")]
                            for temp in temp_list:
                                if isinstance(temp, unicode):
                                    temp = temp.encode('utf-8')
                                out.write(temp)
                                out.write('\t')
                            out.write('\n')
                except Exception as e:
                    print e
                    print("diagnosisPath,drugPath,departmentPath,outputPath路径错误！")
        else:
            self.handleWithFile(filename)
            result["issential_information"]["姓名"] = self.infoDict.get("name")
            result["issential_information"]["年龄"] = self.infoDict.get("age")
            result["issential_information"]["性别"] = self.infoDict.get("sex")
            result["issential_information"]["医院"] = self.infoDict.get("hospital")
            result["issential_information"]["时间"] = self.infoDict.get("times")
            result["issential_information"]["医师"] = self.infoDict.get("doctor")
            result["issential_information"]["科室"] = self.infoDict.get("department")
            result["issential_information"]["费用"] = self.infoDict.get("cost")
            result["prescription_information"][0]["诊断描述"] = self.infoDict.get("diagnose")
            result["prescription_information"][1]["药物信息"] = self.infoDict.get("medicine")
            #return json.dumps(result,ensure_ascii=False,encoding='utf-8')
	    return result
    def main(self):
        self.getfileindex()
        self.handle()

def clear(filePath):
    #direct = "E:\\work\\python\\shumei_medic-develop\\input\\2.docx"
    test = handlePrescription()
    data = test.handle(filePath)
    print data
    #print data

if __name__ == "__main__":
    clear("/Users/charles/Working/shumei_medic-develop/input/10.docx")

