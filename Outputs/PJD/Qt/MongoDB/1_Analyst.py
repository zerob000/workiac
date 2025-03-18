# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:21:18 2025

@author: R Healy

Purpose: Reads two input files and extracts core information: classifications and lead times into a folder. 
"""

import yaml
import argparse
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from datetime import datetime, timedelta

# Data Extractor
def my_extractor(data, last_pbi, start_date):
    # Build dictionaries and initialise variables
    sysms = {} # Create a dictionary of systems
    #sysms_q = {} # Create a dictionary of systems - needed because multiple systems can be in a single data file - could look to move this to yaml?
    types = {} # Create a dictionary of issue types
    resos = {} # Create a dictionary of resolution types
    statu = {} # Create a dictionary of status types
    matched = {} # Create dictionary of issue types for lead time  
    
    lt_cum = 0
    lt_count = 0

    arr_timeline = [] # Unfiltered Arr Timeline
    ser_timeline = [] # Unfiltered Se Timeline
    t_bi = []
    queues = {"GS_PL_TM_DN": [], # Goldilocks-sized, Planned, Work for Team, Already Completed
              "GS_UP_TM_DN": [], # Goldilocks-sized, Unplanned, Work for Team, Already Completed
              "GS_PL_CX_DN": [], # Goldilocks-sized, Planned, Cancelled, Already Completed
              "GS_UP_CX_DN": [], # Goldilocks-sized, Unplanned, Cancelled, Already Completed
              "GS_PL_TM_IP": [], # Goldilocks-sized, Planned, Work for Team, In Progress
              "GS_UP_TM_IP": [], # Goldilocks-sized, Unplanned, Work for Team, In Progress
              "GS_PL_CX_IP": [], # Goldilocks-sized, Planned, Cancelled, In Progress
              "GS_UP_CX_IP": [], # Goldilocks-sized, Unplanned, Cancelled, In Progress
              "BS_PL_TM_DN": [], # Too big/ too small, Planned, Work for Team, Already Completed              
              "BS_UP_TM_DN": [], # Too big/ too small, Unplanned, Work for Team, Already Completed              
              "BS_PL_CX_DN": [], # Too big/ too small, Planned, Cancelled, Already Completed              
              "BS_UP_CX_DN": [], # Too big/ too small, Unplanned, Cancelled, Already Completed               
              "BS_PL_TM_IP": [], # Too big/ too small, Planned, Work for Team, In Progress              
              "BS_UP_TM_IP": [], # Too big/ too small, Unplanned, Work for Team, In Progress              
              "BS_PL_CX_IP": [], # Too big/ too small, Planned, Cancelled, In Progress              
              "BS_UP_CX_IP": []} # Too big/ too small, Unplanned, Cancelled, In Progress   
    # Loop through data
    for i in range(len(data)):
        item = data[i]
        lock = 0
        # Get the last arrival so we can determine the last 100 days
        test_arr = datetime.strptime(item[arr_loc], date_format)
        t_delta = (test_arr-last_pbi).days
        if t_delta > 0: 
            last_pbi = test_arr
        t_delta_last100a = (test_arr-start_date).days
        if t_delta_last100a >= 0: 
            arr_timeline.append(test_arr) # Append timeline
            #t_bi.append([test_arr,1]) # increment the system size for an arrival
            lock = 1
        if item[ser_loc] != spacer:
            test_ser = datetime.strptime(item[ser_loc], date_format)
            # Calculate the last_pbi (needed for counting last100 days)
            t_delta = (test_ser-last_pbi).days 
            if t_delta > 0: 
                last_pbi = test_ser           
            t_delta_last100s = (test_ser-start_date).days 
            if t_delta_last100s >= 0:#
                ser_timeline.append(test_ser) # Append timeline
                #t_bi.append([test_ser,-1]) # decrement the system size for a service
                lock = 1
        if lock == 1: # Prevent unnecessary counting if not needed.
            # Count the number of systems
            if item[sysm_loc] in sysms:
                sysms[item[sysm_loc]] = sysms[item[sysm_loc]] + 1
            else:
                sysms[item[sysm_loc]] = 1
            # Count the number of issue types
            if item[issue_loc] in types:
                types[item[issue_loc]] = types[item[issue_loc]] + 1
            else:
                types[item[issue_loc]] = 1    
            # Count the number of resolutions
            if item[resol_loc] in resos:
                resos[item[resol_loc]] = resos[item[resol_loc]] + 1
            else:
                resos[item[resol_loc]] = 1 
            # Count the number of statuses
            if item[status_loc] in statu:
                statu[item[status_loc]] = statu[item[status_loc]] + 1
            else:
                statu[item[status_loc]] = 1  
            # Count the lead times
            if item[ser_loc] != spacer:
                # Lead Time Calcs
                lt_end = datetime.strptime(item[ser_loc], date_format)
                lt_start = datetime.strptime(item[arr_loc], date_format)
                lt = (lt_end-lt_start).days # Count the number of days in the system duration
                lt_cum = lt_cum + lt
                lt_count = lt_count + 1
                if item[issue_loc] in matched.keys():
                    matched[item[issue_loc]].append([lt_end, lt])
                else:
                    matched[item[issue_loc]] = [[lt_end, lt]]
            # Filter into 16 buckets
            if item[issue_loc] not in EpicsAndSubtasks:
                test_arr = datetime.strptime(item[arr_loc], date_format)
                t_delta = (test_arr-last_pbi).days
                if t_delta_last100a >= 0: 
                    t_bi.append([test_arr,1]) # increment the system size for an arrival
                if item[issue_loc] not in Feedback_Bugs:
                    if item[resol_loc] not in NotDoneByTeam:
                        if item[status_loc] not in NoFurtherWork or item[ser_loc] == spacer:
                            queues["GS_PL_TM_IP"].append(item)
                        else:
                            queues["GS_PL_TM_DN"].append(item)
                            t_bi.append([test_ser,-1]) # decrement the system size for a service
                    else:
                        if item[status_loc] not in NoFurtherWork or item[ser_loc] == spacer:
                            queues["GS_PL_CX_IP"].append(item)
                        else:
                            queues["GS_PL_CX_DN"].append(item)
                            t_bi.append([test_ser,-1]) # decrement the system size for a service
                else:
                    if item[resol_loc] not in NotDoneByTeam:
                        if item[status_loc] not in NoFurtherWork or item[ser_loc] == spacer:
                            queues["GS_UP_TM_IP"].append(item)
                        else:
                            queues["GS_UP_TM_DN"].append(item)
                            t_bi.append([test_ser,-1]) # decrement the system size for a service
                    else:
                        if item[status_loc] not in NoFurtherWork or item[ser_loc] == spacer:
                            queues["GS_UP_CX_IP"].append(item)
                        else:
                            queues["GS_UP_CX_DN"].append(item)
                            t_bi.append([test_ser,-1]) # decrement the system size for a service
            else:
                if item[issue_loc] not in Feedback_Bugs:
                    if item[resol_loc] not in NotDoneByTeam:
                        if item[status_loc] not in NoFurtherWork:
                            queues["BS_PL_TM_IP"].append(item)
                        else:
                            queues["BS_PL_TM_DN"].append(item)
                    else:
                        if item[status_loc] not in NoFurtherWork:
                            queues["BS_PL_CX_IP"].append(item)
                        else:
                            queues["BS_PL_CX_DN"].append(item)
                else:
                    if item[resol_loc] not in NotDoneByTeam:
                        if item[status_loc] not in NoFurtherWork:
                            queues["BS_UP_TM_IP"].append(item)
                        else:
                            queues["BS_UP_TM_DN"].append(item)
                    else:
                        if item[status_loc] not in NoFurtherWork:
                            queues["BS_UP_CX_IP"].append(item)
                        else:
                            queues["BS_UP_CX_DN"].append(item)

    # Group individual filters into buckets
    tbts = (queues["BS_PL_TM_DN"]+queues["BS_PL_TM_IP"]+queues["BS_PL_CX_DN"]+queues["BS_PL_CX_IP"]+queues["BS_UP_TM_DN"]+queues["BS_UP_TM_IP"]+queues["BS_UP_CX_DN"]+queues["BS_UP_CX_IP"]) # All wrong-sized work
    plan = (queues["GS_PL_TM_DN"]+queues["GS_PL_TM_IP"]+queues["GS_PL_CX_DN"]+queues["GS_PL_CX_IP"]) # All right-sized planned work
    unpl = (queues["GS_UP_TM_DN"]+queues["GS_UP_TM_IP"]+queues["GS_UP_CX_DN"]+queues["GS_UP_CX_IP"]) # All right-sized unplanned work
    canc = (queues["GS_PL_CX_DN"]+queues["GS_UP_CX_DN"]) # All right-sized work, rejected by the team
    done = (queues["GS_PL_TM_DN"]+queues["GS_UP_TM_DN"]) # All right-sized work, completed by the team
    wips = (queues["GS_PL_TM_IP"]+queues["GS_PL_CX_IP"]+queues["GS_UP_TM_IP"]+queues["GS_UP_CX_IP"]) # All incomplete right-sized work
    print(len(tbts),len(plan),len(unpl),len(canc),len(done),len(wips))
    #buckets = [plan, unpl, canc, done, wips]
    
    # Create the timeline of arrivals and departures and the cumulative flow data for the system size.
    tb_sorted = sorted(t_bi, reverse=False) # sort the entire timeline in ascending order
    size = 0
    t_b = []
    back = []
    min_size = 0
    for i in tb_sorted:
        t_b.append(i[0])
        size = size + i[1]
        back.append(size)       
        if size < min_size:
            min_size = size # Needed in the cases where partial data is provided and we don't know the size of the initial backlog. This prevents the unphysical case of a backlog less than 0
    
    for i, item in enumerate(back):
        back[i] = back[i] + abs(min_size) # correcting for the case that there is a negative minimum size so backlog never goes to 0

    if len(t_b) != 0:
        return(sysms, types, resos, statu, matched, last_pbi, lt_cum, lt_count, t_b[0])
    else:
        return(sysms, types, resos, statu, matched, last_pbi, lt_cum, lt_count, 0)


# Barchart
def my_barchart(k_l, v_l, labl, g):
    # Resolutions Chart
    plt.rcParams["figure.figsize"] = (10, 7)
    plt.barh(k_l, v_l, align='center')
    plt.xlabel("Count (log scale)", fontweight ='bold', fontsize = 15)
    plt.xscale('log')
    plt.ylabel(labl, fontweight ='bold', fontsize = 15)
    plt.title(sname+" - "+labl+" Distribution - "+g, fontweight ='bold', fontsize = 18)
    plt.tight_layout()
    plt.savefig(sname+"_"+labl+"_"+g+".png")
    #plt.show()
    plt.clf() 

# Lead time    
def my_leadtimechart(matched, g):
    # Some calcs for fancy post processing of Lead time 
    first_element_of_non_empty = [l[0] for l in matched.values() if l] # list comprehension to filter blank issuetpyes
    num_non_empty = len(first_element_of_non_empty)
    colours = iter(cm.rainbow(np.linspace(0, 1, num_non_empty)))
    plt.rcParams["figure.figsize"] = (10, 7)
    for issue, leads in list(matched.items()):
        if len(leads) != 0: 
            lt_res_date = []
            leadtime = []
            for x in leads:
                lt_res_date.append(x[0])
                leadtime.append(x[1])
            plt.scatter(lt_res_date, leadtime, label = issue, color=next(colours))
            plt.ylabel("Lead Time (days) - "+g, fontweight ='bold', fontsize = 15)
    plt.xlabel("Resolution Date", fontweight ='bold', fontsize = 15)
    plt.legend(loc='upper left')
    plt.title(sname+" - Lead time distribution - "+g, fontweight ='bold', fontsize = 18)
    plt.tight_layout()
    plt.savefig(sname+"_LeadTime_"+g+".png")
    #plt.show()
    plt.clf()          


# Open Yaml File of inputs and read the important ones
parser = argparse.ArgumentParser()
parser.add_argument("yaml", help="Input Yaml file")
parser.add_argument("sname", help="System Name")
args = parser.parse_args()
#print(args.yaml)

with open(args.yaml) as stream:
    try:
        inputs = yaml.safe_load(stream)
        Locations = inputs["Locations"]
        id_loc = Locations["id_loc"]
        sysm_loc = Locations["sysm_loc"]
        issue_loc = Locations["issue_loc"]
        resol_loc = Locations["resol_loc"]
        status_loc = Locations["status_loc"]
        arr_loc = Locations["arr_loc"]
        ser_loc = Locations["ser_loc"]
        spacer = inputs["spacer"]
        date_format = inputs["date_format"]
        Filters = inputs["Filters"]
        EpicsAndSubtasks = Filters["EpicsSubtasks"]
        Feedback_Bugs = Filters["FeedbackBugs"]
        NoFurtherWork = Filters["StatusNoFurtherWorkRequired"]
        NotDoneByTeam = Filters["ResosNotDoneByTeam"]
    except yaml.YAMLError as exc:
        print (exc)
        
# Import CSV
sname = args.sname
file = open(str(sname)+".csv", "r", encoding="utf8") 
data = list(csv.reader(file, delimiter=","))
file.close()
# Strip header line
del data[0]

print(sname,len(data))

# Make a new directory and change into it
path = os.getcwd()
newpath0 = os.path.join(path, sname) 
newpath = os.path.join(newpath0, "1_SystemProps")
if not os.path.exists(newpath):
    os.makedirs(newpath)
os.chdir(newpath)  


## Extract All data
last_pbi = datetime(1901, 1, 1, 12, 1) # initally set this to a very early date
all_start_date = last_pbi # For all set this to an early date
extract = my_extractor(data, last_pbi, all_start_date)
sysms = extract[0]
types = extract[1]
resos = extract[2]
statu = extract[3]
matched = extract[4]
last_pbi = extract[5]
lt_cum = extract[6]
lt_count = extract[7]
first_pbi = extract[8] 

# Output dictionaries - for now use one of each
a = open(sname+"_issuetypes.txt", "w", encoding="utf-8")
a.write(str(types))
a.close()
b = open(sname+"_resolutions.txt", "w", encoding="utf-8")
b.write(str(resos))
b.close()
c = open(sname+"_statuses.txt", "w", encoding="utf-8")
c.write(str(statu))
c.close()

# Issuetypes chart
my_barchart(list(types.keys()), list(types.values()), "IssueType", "all")
# Resolutions Chart
my_barchart(list(resos.keys()), list(resos.values()), "Resolution", "all")
# Statuses Chart
my_barchart(list(statu.keys()), list(statu.values()), "Status", "all")
# Lead Time Chart
my_leadtimechart(matched, "all")

# Open Output file and write
f = open(sname+"_SystemAnalysis.txt", "w", encoding="utf-8")
f.write("All PBIS - Unfiltered \n")
f.write("Start date: "+str(first_pbi)+" End date: "+str(last_pbi)+"\n")
f.write("System: "+str(sysms)+"\n")
f.write("Types: "+str(types)+"\n")
f.write("Resolutions: "+str(resos)+"\n")
f.write("Statuses: "+str(statu)+"\n\n")
# Lead time 
f.write("Average Lead Time (all PBIs): "+str(round(lt_cum / lt_count,1))+" days\n")
for issue, leads in list(matched.items()):
    lt_cum = 0
    lt_count = 0
    for x in leads:
        if len(leads) != 0: 
            lt_cum = lt_cum + x[1]
            lt_count = lt_count + 1
    f.write("Average Lead Time ("+issue+"): "+str(round(lt_cum / lt_count,1))+" days\n")

## Last 100 days unfiltered
last100_start_date = last_pbi - timedelta(days=100)
extract = my_extractor(data, last_pbi, last100_start_date)  
sysms = extract[0]
types = extract[1]
resos = extract[2]
statu = extract[3]
matched = extract[4]
last_pbi = extract[5]
lt_cum = extract[6]
lt_count = extract[7]

# Issuetypes chart
my_barchart(list(types.keys()), list(types.values()), "IssueType", "last100")
# Resolutions Chart
my_barchart(list(resos.keys()), list(resos.values()), "Resolution", "last100")
# Statuses Chart
my_barchart(list(statu.keys()), list(statu.values()), "Status", "last100")
# Lead Time Chart
if  lt_count != 0:
    my_leadtimechart(matched, "last100")

# Write to Output file
f.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nLast 100 days only - Unfiltered \n")
f.write("Start date: "+str(last100_start_date)+" End date: "+str(last_pbi)+"\n")
f.write("System: "+str(sysms)+"\n")
f.write("Types: "+str(types)+"\n")
f.write("Resolutions: "+str(resos)+"\n")
f.write("Statuses: "+str(statu)+"\n\n")
# Lead time
if  lt_count != 0:
    f.write("Average Lead Time (all PBIs): "+str(round(lt_cum / lt_count,1))+" days\n")
    for issue, leads in list(matched.items()):
        lt_cum = 0
        lt_count = 0
        for x in leads:
            if len(leads) != 0: 
                lt_cum = lt_cum + x[1]
                lt_count = lt_count + 1
        f.write("Average Lead Time ("+issue+"): "+str(round(lt_cum / lt_count,1))+" days\n")
else:
    f.write("No PBIs resolved in last 100 days.\n")

f.close() 
