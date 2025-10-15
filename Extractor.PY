# -*- coding: utf-8 -*-
"""
Created on 12 June 2025

Loop across the directories to run the scripts

@author: R Healy
"""

import os
import csv
import yaml
import ast
import shutil
from collections import Counter
import fnmatch
import shutil

f = open("ReadyReckonerNew.csv", "a", encoding="utf-8")
f.write("System,Group,Duration Analysed (days),Start Date & Time (date),End Date & Time (date),\
Total PBIs (PBIs),Filtered PBIs (PBIs),\
Planned Arrivals (PBIs),Unplanned Arrivals (PBIs),Cancelled Arrivals (PBIs),\
Net Arrivals (PBIs),Services (PBIs),Measured System Size (PBIs),\
Planned Arrival Rate - alpha (PBIs/day),Unplanned Arrival Rate - epsilon (PBIs/day),\
Cancelled Rate - gamma (PBIs/day),Service Rate - mu (PBIs/day),\
Net Arrival Rate - lambda (PBIs/day),LS Arrival Rate - lambda_LS (PBIs/day),\
Psi,Nu,Zeta,Inventory Days,Strategy,\
Inter-service rate (Days/PBI),\
alpha R^2,epsilon R^2,gamma R^2,mu R^2,\
Date/Time of Analysis,Notes\n")

dirs = ['2015_Jira_Repository_Dataset_Ortu\Emotion_ASF',\
        '2015_Jira_Repository_Dataset_Ortu\Emotion_CODEHAUS',\
        '2015_Jira_Repository_Dataset_Ortu\Emotion_HIBERNATE',\
        '2015_Jira_Repository_Dataset_Ortu\Emotion_JBOSS',\
        '2015_Jira_Repository_Dataset_Ortu\Emotion_SPRING',\
        '2024_RedHat',\
        '2022_TAWOS',\
        '2021_UnstableStories_Levy',\
        '2022_Public_Jira_Dataset_Montgomery\Apache',\
        '2022_Public_Jira_Dataset_Montgomery\Hyperledger',\
        '2022_Public_Jira_Dataset_Montgomery\IntelDAOS',\
        '2022_Public_Jira_Dataset_Montgomery\JFrog',\
        '2022_Public_Jira_Dataset_Montgomery\Jira',\
        '2022_Public_Jira_Dataset_Montgomery\JiraEcosystem',\
        '2022_Public_Jira_Dataset_Montgomery\MariaDB',\
        '2022_Public_Jira_Dataset_Montgomery\Mindville',\
        '2022_Public_Jira_Dataset_Montgomery\Mojang',\
        '2022_Public_Jira_Dataset_Montgomery\MongoDB',\
        '2022_Public_Jira_Dataset_Montgomery\Qt',\
        '2022_Public_Jira_Dataset_Montgomery\RedHat',\
        '2022_Public_Jira_Dataset_Montgomery\Sakai',\
        '2022_Public_Jira_Dataset_Montgomery\SecondLife',\
        '2022_Public_Jira_Dataset_Montgomery\Sonatype',\
        '2022_Public_Jira_Dataset_Montgomery\Spring']

homepath = os.getcwd()
print(homepath)

#d = '2015_Jira_Repository_Dataset_Ortu\\Emotion_ASF'
for d in dirs:
    inpath = homepath + "\\Outputs\\" + d 

    for root, dir, files in os.walk(inpath):
        for items in fnmatch.filter(dir, "3_Strategy"):
            file = open(root + "\\3_Strategy\\" + "ReadyReckonerInputs_All.csv", "r", encoding="utf8") 
            data = list(csv.reader(file, delimiter=","))
            file.close()
            # Strip header line
            del data[0]
            data[0][-2] = d 
            #print(data)
            csvWriter = csv.writer(f,delimiter=',', lineterminator='\n')
            csvWriter.writerows(data)
            
            file = open(root  + "\\3_Strategy\\" + "ReadyReckonerInputs_last100.csv", "r", encoding="utf8") 
            data = list(csv.reader(file, delimiter=","))
            file.close()
            # Strip header line
            del data[0]
            data[0][-2] = d 
            csvWriter = csv.writer(f,delimiter=',', lineterminator='\n')
            csvWriter.writerows(data)
    
#for dir in dirs:
 

f.close()