# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:21:18 2025

@author: R Healy
"""

import os
import csv
import yaml
#import argparse

f = open("_BenchMark_Inputs.csv", "a", encoding="utf-8")

# Open Yaml File of inputs 
with open("Queue.yaml") as stream:
    try:
        inputs = yaml.safe_load(stream)
        snames = inputs["System_Names"]
    except yaml.YAMLError as exc:
        print (exc)

for sname, yml in snames.items():
    print(sname, yml)
    os.system("python 1_Analyst.py "+yml+" "+sname)
    os.system("python 2_Scheduler.py RedHat.yaml "+sname)
    os.system("python 3_Strategist.py "+yml+" "+sname)
    
    # Make a new directory and change into it
    path = os.getcwd()
    newpath0 = os.path.join(path, sname) 
    newpath = os.path.join(newpath0, "3_Strategy")
    os.chdir(newpath)  
    
    file = open("ReadyReckonerInputs_All.csv", "r", encoding="utf8") 
    data = list(csv.reader(file, delimiter=","))
    file.close()
    # Strip header line
    del data[0]
    print(sname,len(data))
    csvWriter = csv.writer(f,delimiter=',', lineterminator='\n')
    csvWriter.writerows(data)
    
    file = open("ReadyReckonerInputs_last100.csv", "r", encoding="utf8") 
    data = list(csv.reader(file, delimiter=","))
    file.close()
    # Strip header line
    del data[0]
    csvWriter = csv.writer(f,delimiter=',', lineterminator='\n')
    csvWriter.writerows(data)
    
    os.chdir(path) 
    
f.close()
    
    
