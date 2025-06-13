# -*- coding: utf-8 -*-
"""
Created on 12 June 2025

@author: R Healy
"""

import os
import csv
import yaml
import ast
from collections import Counter


dirs = ['2015_Jira_Repository_Dataset_Ortu\Emotion_ASF','2015_Jira_Repository_Dataset_Ortu\Emotion_CODEHAUS','2015_Jira_Repository_Dataset_Ortu\Emotion_HIBERNATE','2015_Jira_Repository_Dataset_Ortu\Emotion_JBOSS','2015_Jira_Repository_Dataset_Ortu\Emotion_SPRING','2024_RedHat', '2022_TAWOS', '2021_UnstableStories_Levy']
path = os.getcwd()
cmd = 'dir'
for dir in dirs:
    newpath = os.path.join(path, dir) 
    os.chdir(newpath) 
    os.system("python 0_Manager.py")
    #os.system(cmd)
    os.chdir(path)  

