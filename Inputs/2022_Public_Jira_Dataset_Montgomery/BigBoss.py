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


dirs = ['Hyperledger', 'IntelDAOS', 'JFrog', 'Jira', 'JiraEcosystem', 'MariaDB', 'Mojang', 'MongoDB', 'Qt', 'RedHat', 'Sakai', 'SecondLife', 'Sonatype', 'Spring']
path = os.getcwd()
cmd = 'dir'
for dir in dirs:
    newpath = os.path.join(path, dir) 
    os.chdir(newpath) 
    os.system("python 0_Manager.py")
    #os.system(cmd)
    os.chdir(path)  

