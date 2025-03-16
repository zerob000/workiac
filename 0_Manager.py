# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:21:18 2025

@author: R Healy
"""

import os
import csv
import yaml
import ast
from collections import Counter


# Produce functions
def my_analyst(yml, sname, tot_issu, tot_reso, tot_stat):
    os.system("python 1_Analyst.py "+yml+" "+sname)
    
    # Change into the strategy directory
    path = os.getcwd()
    newpath0 = os.path.join(path, sname) 
    newpath = os.path.join(newpath0, "1_SystemProps")
    os.chdir(newpath)  
    
    # Update issuetypes - add to existing where needed.
    with open(sname+"_issuetypes.txt", "r", encoding="utf8") as data:
        issuetypes = ast.literal_eval(data.read())
    tot_issu = dict(Counter(tot_issu) + Counter(issuetypes))
    # Update resolutions - add to existing where needed.
    with open(sname+"_resolutions.txt", "r", encoding="utf8") as data:
        resolutions = ast.literal_eval(data.read())
    tot_reso = dict(Counter(tot_reso) + Counter(resolutions))
    # Update resolutions - add to existing where needed.
    with open(sname+"_statuses.txt", "r", encoding="utf8") as data:
        statuses = ast.literal_eval(data.read())
    tot_stat = dict(Counter(tot_stat) + Counter(statuses))

    os.chdir(path) 
    
    return(tot_issu, tot_reso, tot_stat)

def my_scheduler(yml, sname):
    os.system("python 2_Scheduler.py RedHat.yaml "+sname)

def my_strategist(yml, sname):
    os.system("python 3_Strategist.py RedHat.yaml "+sname)
    
    # Change into the strategy directory
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

f = open("_BenchMark_Inputs.csv", "a", encoding="utf-8")

# Open Yaml File of inputs 
with open("Queue.yaml") as stream:
    try:
        inputs = yaml.safe_load(stream)
        snames = inputs["System_Names"]
    except yaml.YAMLError as exc:
        print (exc)

tot_issu = {}
tot_reso = {}
tot_stat = {}
for sname, yml in snames.items():
    print(sname, yml)
    # The analyst keeps updating the dictionaries
    updates = my_analyst(yml, sname, tot_issu, tot_reso, tot_stat)
    tot_issu = updates[0]
    tot_reso = updates[1]
    tot_stat = updates[2]

    my_scheduler(yml, sname)
    my_strategist(yml, sname)

f.close()

# Aggregate Issuetypes
csv_F = open("_combined_issuetypes.csv", "w", encoding="utf-8")
csv_F.write("Type,Count\n")
csvWriter = csv.writer(csv_F,delimiter=',', lineterminator='\n')
csvWriter.writerows(tot_issu.items())
csv_F.close()

# Aggregate Resolutions
csv_F = open("_combined_resolutions.csv", "w", encoding="utf-8")
csv_F.write("Type,Count\n")
csvWriter = csv.writer(csv_F,delimiter=',', lineterminator='\n')
csvWriter.writerows(tot_reso.items())
csv_F.close()

# Aggregate Statuses
csv_F = open("_combined_statuses.csv", "w", encoding="utf-8")
csv_F.write("Type,Count\n")
csvWriter = csv.writer(csv_F,delimiter=',', lineterminator='\n')
csvWriter.writerows(tot_stat.items())
csv_F.close()   
    
