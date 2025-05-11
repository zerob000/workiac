# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:21:18 2025

@author: R Healy
"""

import os
import csv
from datetime import datetime
date_format = "%Y-%m-%dT%H:%M:%S.%f%z"

# Open export file and add heading
f = open("_Extract_Report.csv", "w", encoding="utf-8")
f.write("Org Name,Total Data,Subtasks Filter,Epic Filter,CLT Filter,Net data,Number analysable systems\n")


colls = ['Emotion']
for coll in colls: 
    #os.system("mongoexport --db=JiraRepos --collection="+coll+" --type=csv --fieldFile=fields.txt --out="+coll+".csv")
    
    # Import CSV
    file = open(str(coll)+".csv", "r", encoding="utf8") 
    data = list(csv.reader(file, delimiter=","))
    file.close()
    # Strip header line
    del data[0]
    
    # Make a new directory and change into it
    path = os.getcwd()
    newpath = os.path.join(path, coll) 
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    os.chdir(newpath) 
    
    # Create the queue.yaml file
    q = open("Queue.yaml", "w", encoding="utf-8")
    q.write("---\n# Add a queue of system names and data files for the manager to run\nSystem_Names:\n    ## \"CSV name\": \"Yaml name\"\n")
    
    f.write(coll+','+str(len(data))+',')
    subtask_count = 0
    epic_count = 0
    JiraProjects = {} # Initiatilse a list of jira projects
    for i in range(len(data)):
        item = data[i]
        lst = [item[2],item[0],item[4],item[10],item[9],item[7],item[1],item[8]]
        if item[6] in ('SPRING'):
            if item[10] not in ('Sub-task'): # Sub-tasks
                if item[10] not in ('Epic'):
                    print(lst)
                    if item[4] in JiraProjects:
                        JiraProjects[item[4]].append(lst)
                    else:
                        JiraProjects[item[4]] = [lst]
                else:
                    epic_count = epic_count + 1
            else:
                subtask_count = subtask_count + 1
        
    f.write(str(subtask_count)+','+str(epic_count)+',')
    sys_count = 0
    pbi_count = 0
    pbi_rem = 0
    for sname, details in JiraProjects.items():
        print(coll,sname, len(details))
        if len(details) >= 30: # remove systems with fewer than 30 PBIs
            # Export file for each system
            csv_F = open(sname+".csv", "w", encoding="utf-8")
            csv_F.write("Key,ID,Project,IssueType,Status,Resolution,Created Date,Resolved Date\n")
            csvWriter = csv.writer(csv_F,delimiter=',',lineterminator='\n')
            csvWriter.writerows(details)
            csv_F.close()
            sys_count = sys_count + 1
            pbi_count = pbi_count + len(details)
            q.write("    \""+sname+"\": \""+coll+".yaml\"\n")
        else:
            #print("Removed",sname, len(details))
            pbi_rem = pbi_rem + len(details)
    
    f.write(str(pbi_rem)+',')
    f.write(str(pbi_count)+','+str(sys_count)+'\n')
    
    q.close()
    os.chdir(path)

f.close()         
        
