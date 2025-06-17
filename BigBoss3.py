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


#dirs = ['2015_Jira_Repository_Dataset_Ortu\Emotion_ASF',\
dirs = ['2015_Jira_Repository_Dataset_Ortu\Emotion_CODEHAUS',\
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
in_man = homepath + '\\0_Manager.py'
in_ana = homepath + '\\1_Analyst.py'
in_sch = homepath + '\\2_Scheduler.py'
in_str = homepath + '\\3_Strategist.py'
cmd = 'dir'
for dir in dirs:
    source = homepath + "\\Inputs\\" + dir
    destin = homepath + "\\Outputs\\" + dir
    shutil.copytree(source, destin, dirs_exist_ok=True)
    os.chdir(destin) 
    dest_man = destin + '\\0_Manager.py'
    dest_ana = destin + '\\1_Analyst.py'
    dest_sch = destin + '\\2_Scheduler.py'
    dest_str = destin + '\\3_Strategist.py'
    shutil.copy(in_man, destin)
    shutil.copy(in_ana, destin)
    shutil.copy(in_sch, destin)
    shutil.copy(in_str, destin)
    os.system("python 0_Manager.py")
    #os.system(cmd)
    os.remove(dest_man)
    os.remove(dest_ana)
    os.remove(dest_sch)
    os.remove(dest_str)
    os.chdir(homepath)  

