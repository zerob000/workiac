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

# Aggregate Issuetypes
f = open("All_combined_issuetypes.csv", "w", encoding="utf-8")
f.write("System,Type,Count,Group\n")


# Aggregate Resolutions
g = open("All_combined_resolutions.csv", "w", encoding="utf-8")
g.write("System,Resolution,Count,Group\n")

# Aggregate Statuses
h = open("All_combined_statuses.csv", "w", encoding="utf-8")
h.write("System,Status,Count,Group\n")


dirs = ['2015_Jira_Repository_Dataset_Ortu\\Emotion_ASF',\
        '2015_Jira_Repository_Dataset_Ortu\\Emotion_CODEHAUS',\
        '2015_Jira_Repository_Dataset_Ortu\\Emotion_HIBERNATE',\
        '2015_Jira_Repository_Dataset_Ortu\\Emotion_JBOSS',\
        '2015_Jira_Repository_Dataset_Ortu\\Emotion_SPRING',\
        '2024_RedHat',\
        '2022_TAWOS',\
        '2021_UnstableStories_Levy',\
        '2022_Public_Jira_Dataset_Montgomery\\Apache',\
        '2022_Public_Jira_Dataset_Montgomery\\Hyperledger',\
        '2022_Public_Jira_Dataset_Montgomery\\IntelDAOS',\
        '2022_Public_Jira_Dataset_Montgomery\\JFrog',\
        '2022_Public_Jira_Dataset_Montgomery\\Jira',\
        '2022_Public_Jira_Dataset_Montgomery\\JiraEcosystem',\
        '2022_Public_Jira_Dataset_Montgomery\\MariaDB',\
        '2022_Public_Jira_Dataset_Montgomery\\Mindville',\
        '2022_Public_Jira_Dataset_Montgomery\\Mojang',\
        '2022_Public_Jira_Dataset_Montgomery\\MongoDB',\
        '2022_Public_Jira_Dataset_Montgomery\\Qt',\
        '2022_Public_Jira_Dataset_Montgomery\\RedHat',\
        '2022_Public_Jira_Dataset_Montgomery\\Sakai',\
        '2022_Public_Jira_Dataset_Montgomery\\SecondLife',\
        '2022_Public_Jira_Dataset_Montgomery\\Sonatype',\
        '2022_Public_Jira_Dataset_Montgomery\\Spring']

homepath = os.getcwd()
print(homepath)

#d = '2015_Jira_Repository_Dataset_Ortu\\Emotion_ASF'
for d in dirs:
    inpath = homepath + "\\Outputs\\" + d 
    tot_issu = {}
    tot_reso = {}
    tot_stat = {}
    for root, dir, files in os.walk(inpath):
        for items in fnmatch.filter(dir, "1_SystemProps"):
            r = root.replace(inpath+"\\", "")
            print(r)
            with open(root + "\\1_SystemProps\\"+r+"_issuetypes.txt", "r", encoding="utf8") as data: 
                issuetypes = ast.literal_eval(data.read())
            tot_issu = dict(Counter(tot_issu) + Counter(issuetypes))
            for k,v in tot_issu.items():
                f.write(r+","+k+","+str(v)+","+d+"\n")
            #print(tot_issu) 
            with open(root + "\\1_SystemProps\\"+r+"_resolutions.txt", "r", encoding="utf8") as data:
                resolutions = ast.literal_eval(data.read())
            tot_reso = dict(Counter(tot_reso) + Counter(resolutions))
            for k,v in tot_reso.items():
                g.write(r+","+k+","+str(v)+","+d+"\n")
            # Update resolutions - add to existing where needed.
            with open(root + "\\1_SystemProps\\"+r+"_statuses.txt", "r", encoding="utf8") as data:
                statuses = ast.literal_eval(data.read())
            tot_stat = dict(Counter(tot_stat) + Counter(statuses))
            for k,v in tot_reso.items():
                h.write(r+","+k+","+str(v)+","+d+"\n")
        
f.close()
g.close()
h.close()