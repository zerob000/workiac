# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:21:18 2025

@author: R Healy

Purpose: Reads two input files and extracts day and hour information for arrivals and services before sending them into a folder. 
"""

import yaml
import argparse
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta

## Functions
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
    buckets = [plan, unpl, canc, done, wips]
    
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
                        
    return(arr_timeline, ser_timeline, last_pbi)
    

# Day and Time Distribution
def my_daytimedistrib(timeline, typ, g):
    # Initialise Time and Date
    X_day = {'Mon':0, 'Tue':0, 'Wed':0, 'Thu':0, 'Fri':0, 'Sat':0, 'Sun':0} # Create a dictionary of arrival days
    X_hour = {'06':0, '05':0, '04':0, '03':0, '02':0, '01':0, '00':0, '23':0, 
                '22':0, '21':0, '20':0, '19':0, '18':0, '17':0, '16':0, '15':0, 
                '14':0, '13':0, '12':0, '11':0, '10':0, '09':0, '08':0, '07':0}
    X_dt =[["00:00 - 01:00",0,0,0,0,0,0,0],["01:00 - 02:00",0,0,0,0,0,0,0],
             ["02:00 - 03:00",0,0,0,0,0,0,0],["03:00 - 04:00",0,0,0,0,0,0,0],
             ["04:00 - 05:00",0,0,0,0,0,0,0],["05:00 - 06:00",0,0,0,0,0,0,0],
             ["06:00 - 07:00",0,0,0,0,0,0,0],["07:00 - 08:00",0,0,0,0,0,0,0],
             ["08:00 - 09:00",0,0,0,0,0,0,0],["09:00 - 10:00",0,0,0,0,0,0,0],
             ["10:00 - 11:00",0,0,0,0,0,0,0],["11:00 - 12:00",0,0,0,0,0,0,0],
             ["12:00 - 13:00",0,0,0,0,0,0,0],["13:00 - 14:00",0,0,0,0,0,0,0],
             ["14:00 - 15:00",0,0,0,0,0,0,0],["15:00 - 16:00",0,0,0,0,0,0,0],
             ["16:00 - 17:00",0,0,0,0,0,0,0],["17:00 - 18:00",0,0,0,0,0,0,0],
             ["18:00 - 19:00",0,0,0,0,0,0,0],["19:00 - 20:00",0,0,0,0,0,0,0],
             ["20:00 - 21:00",0,0,0,0,0,0,0],["21:00 - 22:00",0,0,0,0,0,0,0],
             ["22:00 - 23:00",0,0,0,0,0,0,0],["23:00 - 00:00",0,0,0,0,0,0,0]]
    # Count the number of arrivals / services each day of the week / hour of the day 
    if len(timeline) != 0: # Only work for non-zero timelines
        for i in timeline:
            dte = i # datetime.strptime(i, date_format)
            Xday = dte.strftime('%a')
            X_day[Xday] = X_day[Xday] + 1
            Xhour = dte.strftime('%H')
        
            #Create 2D Matrix of arrivals
            if str(Xday) == "Mon":
                X_dt[int(Xhour)][1] = X_dt[int(Xhour)][1] + 1
            elif str(Xday) == "Tue":
                X_dt[int(Xhour)][2] = X_dt[int(Xhour)][2] + 1
            elif str(Xday) == "Wed":
                X_dt[int(Xhour)][3] = X_dt[int(Xhour)][3] + 1
            elif str(Xday) == "Thu":
                X_dt[int(Xhour)][4] = X_dt[int(Xhour)][4] + 1
            elif str(Xday) == "Fri":
                X_dt[int(Xhour)][5] = X_dt[int(Xhour)][5] + 1
            elif str(Xday) == "Sat":
                X_dt[int(Xhour)][6] = X_dt[int(Xhour)][6] + 1
            elif str(Xday) == "Sun":
                X_dt[int(Xhour)][7] = X_dt[int(Xhour)][7] + 1   
            X_hour[Xhour] = X_hour[Xhour] + 1
            
        # Days
        Xdays = list(X_day.keys())
        Xcounts = list(X_day.values())
        x_axis = np.arange(7) # Split the x axis into 7 for the days for the week
        plt.rcParams["figure.figsize"] = (10, 7)
        plt.bar(x_axis, Xcounts, 0.4, color = 'b', label = typ)
        plt.xticks(x_axis, Xdays)
        plt.ylabel("Count (log scale)", fontweight ='bold', fontsize = 15)
        plt.yscale('log')
        plt.xlabel("Day", fontweight ='bold', fontsize = 15)
        plt.title(typ+" Distribution", fontweight ='bold', fontsize = 18)
        plt.tight_layout()
        plt.savefig(sname+"_"+typ+"_days_"+g+".png")
        #plt.show()
        plt.clf()    
        
        # Hours
        labels = list(X_hour.keys())
        angles = np.linspace(0, 2*np.pi, 24, endpoint=False)
        X_rad = list(X_hour.values())
        
        # calculate the y ticks 
        ytx = np.linspace(0,round(1.1*max(X_rad)), num=5)
        fig = plt.figure(figsize=(10, 7)) # this will output a figure size but it seems this is unavoidable.
        ax = fig.add_subplot(111, polar=True)
        ax.plot(angles, X_rad, 'o-', linewidth=2, color='b', label='Total '+typ+' by hour')
        ax.fill(angles, X_rad, color='b', alpha=0.25)
        ax.set_thetagrids(angles * 180/np.pi, labels)
        ax.set_title(typ+" Time Distribution", fontweight ='bold', fontsize = 18)
        ax.legend(loc='upper right')
        ax.grid(True)
        plt.yticks(ytx)
        plt.tight_layout()
        plt.savefig(sname+"_"+typ+"_hours_"+g+".png")
        #plt.show()
        plt.clf()
        
        # Day and hour distribution tables
        # Count Table
        sus_X = open(sname+"_Day_Hour_"+typ+"_count_"+g+".csv", "w", encoding="utf-8")
        sus_X.write(" ,Mon,Tue,Wed,Thu,Fri,Sat,Sun\n")
        csvWriter = csv.writer(sus_X,delimiter=',', lineterminator='\n')
        csvWriter.writerows(X_dt)
        sus_X.close()
        
        # Percentage table
        sus_X = open(sname+"_Day_Hour_"+typ+"_percent_"+g+".csv", "w", encoding="utf-8")
        sus_X.write(" ,Mon,Tue,Wed,Thu,Fri,Sat,Sun\n")
        csvWriter = csv.writer(sus_X,delimiter=',', lineterminator='\n')
        X_pc = X_dt
        # Loop through the table to conver counts to overall percentages
        i = 0
        while i < 24:
            j = 1
            while j < 8:
                X_pc[i][j]= round(100*X_dt[i][j]/len(timeline),2)
                j = j+1
            i = i+1
        csvWriter.writerows(X_pc)
        sus_X.close()
    
    return(X_day, X_hour)


# Open Yaml File of inputs and read the important ones
parser = argparse.ArgumentParser()
parser.add_argument("yaml", help="Input Yaml file")
parser.add_argument("sname", help="System Name")
args = parser.parse_args()

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
newpath = os.path.join(newpath0, "2_SchedulesOfWork")
if not os.path.exists(newpath):
    os.makedirs(newpath)
os.chdir(newpath)  

## Extract All data
last_pbi = datetime(1901, 1, 1, 12, 1) # initally set this to a very early date
all_start_date = last_pbi # For all set this to an early date
extract = my_extractor(data, last_pbi, all_start_date)
arr_timeline = extract[0]
ser_timeline = extract[1]
last_pbi = extract[2]


# Open Output files and write
f = open(sname+"_DateAndTimeAnalysis.txt", "w", encoding="utf-8")
# Time distribution
arr_day=my_daytimedistrib(arr_timeline, "Arrivals", "all")
ser_day=my_daytimedistrib(ser_timeline, "Services", "all")
f.write("Unfiltered All PBIs between  Start Date: "+str(all_start_date)+" and  End Date: "+str(last_pbi)+"\n")
f.write("\nArrival Days: "+str(arr_day[0])+"\n")
f.write("Total Arrivals: "+str(len(arr_timeline))+"\n")
f.write("Service Days: "+str(ser_day[0])+"\n")
f.write("Total Services: "+str(len(ser_timeline))+"\n")
#f.write("\nArrival Hours: "+str(arr_day[1])+"\n")
#f.write("Service Hours: "+str(ser_day[1])+"\n")

## Last 100 days unfiltered charts
last100_start_date = last_pbi - timedelta(days=100)
extract = my_extractor(data, last_pbi, last100_start_date)  
arr_timeline100 = extract[0]
ser_timeline100 = extract[1]

# Write to files
f.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nLast 100 days only\n")
# Time distribution
arr_day=my_daytimedistrib(arr_timeline100, "Arrivals", "last100")
ser_day=my_daytimedistrib(ser_timeline100, "Services", "last100")
f.write("Unfiltered PBIs between  Start Date: "+str(last100_start_date)+" and  End Date: "+str(last_pbi)+"\n")
f.write("\nArrival Days: "+str(arr_day[0])+"\n")
f.write("Total Arrivals: "+str(len(arr_timeline100))+"\n")
f.write("Service Days: "+str(ser_day[0])+"\n")
f.write("Total Services: "+str(len(ser_timeline100))+"\n")
#f.write("\nArrival Hours: "+str(arr_day[1])+"\n")
#f.write("Service Hours: "+str(ser_day[1])+"\n")

f.close() 
