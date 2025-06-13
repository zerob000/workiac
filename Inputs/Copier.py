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
import fnmatch
import shutil

inpath = os.getcwd()
outpath = "C:\\Users\\Solar\\Documents\\GitHub\\workiac\\Outputs\\"


# root = "C:\\Users\\Solar\\Documents\\GitHub\\workiac\\Inputs\\TEST\\A"
# source = root + "\\3_Strategy"
# destination = "C:\\Users\\Solar\\Documents\\GitHub\\workiac\\Outputs\\TEST\\A\\3_Strategy" 

# shutil.rmtree(destination)
# dest = shutil.copytree(source, destination)
# shutil.rmtree(root)


for root, dir, files in os.walk(inpath):
    for items in fnmatch.filter(dir, "3_Strategy"):
        source = root + "\\" + items
        print(source)        
        destin = source.replace("Inputs", "Outputs")
        isExist = os.path.exists(source)
        shutil.rmtree(destin)
        shutil.copytree(source, destin)
        shutil.rmtree(root)


