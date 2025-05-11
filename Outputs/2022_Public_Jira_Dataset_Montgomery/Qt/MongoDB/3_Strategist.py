# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 16:21:18 2025

@author: R Healy

Purpose: Reads two input files and extracts and calculates strategic information before placing this into a folder. 
"""

import yaml
import argparse
import csv
import os
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import math
import scipy

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
    ser_timeline = [] # Unfiltered Ser Timeline
    t_bi = []
    queues = {"GS_PL_TM_DN": [], # Goldilocks-sized, Planned, Work for Team, Already Completed
              "GS_UP_TM_DN": [], # Goldilocks-sized, Unplanned, Work for Team, Already Completed
              "GS_PL_CX_DN": [], # Goldilocks-sized, Planned, Cancelled, Already Completed
              "GS_UP_CX_DN": [], # Goldilocks-sized, Unplanned, Cancelled, Already Completed
              "GS_PL_TM_IP": [], # Goldilocks-sized, Planned, Work for Team, In Progress
              "GS_UP_TM_IP": [], # Goldilocks-sized, Unplanned, Work for Team, In Progress
              "GS_PL_CX_IP": [], # Goldilocks-sized, Planned, Cancelled, In Progress
              "GS_UP_CX_IP": [], # Goldilocks-sized, Unplanned, Cancelled, In Progress
              "BS_PL_TM_DN": [], # Too big / too small, Planned, Work for Team, Already Completed              
              "BS_UP_TM_DN": [], # Too big / too small, Unplanned, Work for Team, Already Completed              
              "BS_PL_CX_DN": [], # Too big / too small, Planned, Cancelled, Already Completed              
              "BS_UP_CX_DN": [], # Too big / too small, Unplanned, Cancelled, Already Completed               
              "BS_PL_TM_IP": [], # Too big / too small, Planned, Work for Team, In Progress              
              "BS_UP_TM_IP": [], # Too big / too small, Unplanned, Work for Team, In Progress              
              "BS_PL_CX_IP": [], # Too big / too small, Planned, Cancelled, In Progress              
              "BS_UP_CX_IP": []} # Too big / too small, Unplanned, Cancelled, In Progress   
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
    arrs = (queues["GS_PL_TM_DN"]+queues["GS_PL_TM_IP"]+queues["GS_PL_CX_IP"]+queues["GS_UP_TM_DN"]+queues["GS_UP_TM_IP"]+queues["GS_UP_CX_IP"])
    done = (queues["GS_PL_TM_DN"]+queues["GS_UP_TM_DN"]) # All right-sized work, completed by the team
    wips = (queues["GS_PL_TM_IP"]+queues["GS_PL_CX_IP"]+queues["GS_UP_TM_IP"]+queues["GS_UP_CX_IP"]) # All incomplete right-sized work
    print(len(tbts),len(plan),len(unpl),len(canc),len(arrs),len(done),len(wips))
    
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
  
    return(arr_timeline, ser_timeline, last_pbi, buckets, [t_b, back, min_size])

def my_timeanalysis(bucket, loc, date_format, start_date): 
    if len(bucket) != 0: # Add logic for cases with no pbis
        feature = my_timeline(bucket, loc, date_format, start_date) # Timeline
        t = feature[1]
        cum = feature[2]
        ls_d = my_leastsquares(feature[0], t, cum)  # Least squares fit 
        if ls_d[0] != "NaN": 
            slope = round(ls_d[0],3)
            ls = ls_d[1]
            R2 = round(ls_d[2],3)
            c = ls_d[3]
        else:
            slope = 0
            ls = [0,0]
            R2 = 0
            c = 0
    else:        
        t = [start_date,start_date] #Workaround
        cum = [0,0]
        slope = 0
        ls = [0,0]
        R2 = 0
        c = 0

    return(slope, t, cum, ls, R2, c)


# Timeline function
def my_timeline(data, loc, date_format, start_date):
    res = sorted(data, key=lambda x: datetime.strptime(x[loc], date_format), reverse=False)
    t_start = datetime.strptime(res[-1][loc], date_format) # initially set the start date to the end date.
    # Cumulative Calculations 
    dat_c = 0
    t_b = []
    cumulative = []
    lock = 0
    # Loop through timeline to get data for cumulative graphs
    for i in res:
        # Start Time
        t_test = datetime.strptime(i[loc], date_format)
        t_delta = (start_date-t_test).days
        if t_delta <= 0: # if the test date is _after_ the permissable start date
            if lock == 0: # if this is the first time this has happened (we just ordered the data sequentially)
                t_start = t_test
                lock = 1      
            dat_c = dat_c + 1
            cumulative.append(dat_c)
            t_b.append(datetime.strptime(i[loc], date_format))
    t_b = sorted(t_b, reverse=False)
    return(t_start, t_b, cumulative)
    
# Least squares function
def my_leastsquares(t_start, t_b, cumulative):
    td = []
    for t in t_b:
        t_d = (t-t_start).days # Least squares cal doesn't like datetime
        td.append(t_d)
    x = np.array(td).astype('float')
    y = np.array(cumulative).astype('float')
    if len(set(x)) != 1: # Check if all x values are the same. May need the same for y but not so far.
        ls_a = scipy.stats.linregress(x, y) # New way https://urldefense.com/v3/__https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html__;!!CyYWWBA!AARMGb2-M1ybaqHmtHW1-MtPFZLPFnNpc5rl0o2hp5QNm1dOAvSAdDd5ZvTgq8oa1fL6ix9NykdPrPWPvg1cIA$ [docs[.]scipy[.]sname]
        slp = round(ls_a.slope,3) 
        arr_ls = [slp*td[0]+ls_a.intercept,slp*td[-1]+ls_a.intercept]
        R2 = round(ls_a.rvalue**2,3) # R^2 value lambda
        c = round(ls_a.intercept,3)
    else:
        slp = "NaN" # Vertical lines have slopes equal to infinity.
        arr_ls = ["NaN","NaN"]
        R2 = "NaN" 
        c = "NaN" 
    return([slp, arr_ls, R2, c])

# Some Queueing Metrics and Charts, Poisson and Exponential - tends not to be very useful
def my_poisson(t_sd, rate, nme, g):
    if rate != 0: # Adding logic for cases when no data. 
        # Make a new directory and change into it
        path = os.getcwd()
        newpath = os.path.join(path, "queue_charts") 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        os.chdir(newpath)
        
        # Inter Rates
        tmlin = sorted(t_sd, reverse=False)  
        t_dur = (tmlin[-1] - tmlin[0]).days
        # Count the number of days that an event happened
        i = 0
        inter_as = {}
        while i < len(tmlin): 
            day =  tmlin[i].date() # Convert to a date object
            if day in inter_as:
                inter_as[day] = inter_as[day] + 1
            else:
                inter_as[day] = 1
            i = i + 1
        # Count the number of events per day (PBIs/day)
        arr_cs = {}
        for key in inter_as:
            if inter_as[key] in arr_cs:
                arr_cs[inter_as[key]] = arr_cs[inter_as[key]] + 1 
            else:
                arr_cs[inter_as[key]] = 1
        # Add zero days
        zero_d = t_dur - len(inter_as)
        arr_cs[0] = zero_d
        
        # Inter-arrival rate Histogram
        Rates = sorted(arr_cs)
        Counts = []
        for key in Rates:
            if sum(arr_cs.values()) != 0:
                Counts.append(100*arr_cs[key]/sum(arr_cs.values())) # Had to include this workaround to avoid divide by zero
            else:
                Counts.append(1)
    
        i = 0
        k = [] # number events
        Probs = []
        while i > -1:
            k.append(i)
            prob = 100*math.exp(-rate)*(rate**i)/math.factorial(i) # Poisson probability of an event occuring
            Probs.append(prob)
            i = i + 1
            if i > rate: # wait for upper bounds as Poison can be symmetrical 
                if prob < 0.001:
                    i = -2 # exit the loop
                    
        # Chi squared goodness of fit test - simplified - should improve to remove low scores (freq <5)
        Chi_s = 0
        i = 0   
        for i in k:
            j = 0
            for j in Rates:
                if i == j:
                    if i < len(Probs):
                        if j < len(Counts): # These are needed as mismatches between predicted and actual
                            Chi_s = Chi_s + (((Counts[j] - Probs[i])**2)/Probs[i])
                j = j+1
            i = i+1    
        DoF = min(len(k), len(Rates)) - 1 - 1 # Degree of Freedom is number of classes minus 1 parameter -1   
        # Note: tried out of the box Chisquared test but it introduced way more problems than it was worth
        
        x_axis_act = np.arange(len(Rates))
        x_axis_exp = np.arange(len(k))
        plt.rcParams["figure.figsize"] = (10, 7)
        plt.bar(x_axis_act-0.2, Counts, 0.4, color = 'fuchsia', label = "Actual")
        plt.bar(x_axis_exp+0.2, Probs, 0.4, color = 'khaki', label = "Expected")
        plt.title(nme+" $\u03C7^2$: "+str(round(Chi_s,3))+" DoF: "+str(DoF), fontweight ='bold', fontsize = 18)
        plt.xlabel("Rate (PBIs/day)", fontweight ='bold', fontsize = 15)
        plt.ylabel("Percentage of Total", fontweight ='bold', fontsize = 15)
        if len(Rates) > len(k):
            plt.xticks(x_axis_act, Rates)
        else:
            plt.xticks(x_axis_exp, k)
        #plt.tight_layout()
        plt.legend()
        plt.savefig(nme+'_Poi_'+g+'.png')
        #plt.show()
        plt.clf()         
        
        # Exponential distribution (could be a separate function?)
        i = 0
        inter_ss = {}
        while i < len(tmlin)-1:
            inter_s = (tmlin[i+1] - tmlin[i]).days
            # Count the number of instances of each interarrival rate
            if inter_s in inter_ss:
                inter_ss[inter_s] = inter_ss[inter_s] + 1
            else:
                inter_ss[inter_s] = 1
            i = i + 1 # careful with this, see below
        inter_s_k1 = sorted(inter_ss) # Couldn't get dictionary sorting to work - it only returned a list
        inter_s_v = []
        inter_s_k2 = []
        for key in inter_s_k1:
            inter_s_v.append(inter_ss[key])
            inter_s_k2.append(key)
        plt.rcParams["figure.figsize"] = (10, 7)
        plt.scatter(inter_s_k2, inter_s_v, color='fuchsia', label='Actual')
        
        # Expected 
        x_array = np.arange(0,inter_s_k2[-1]+2,1) # Extend the x array beyond the longest inter-arrival
        y_array =[]
        for x in x_array:
            y = i*rate*math.exp(-rate*x) # use the i counter to scale the graph
            y_array.append(y)
        # Plot
        plt.plot(x_array, y_array, color='khaki', label='Expected')
        plt.title(nme, fontweight ='bold', fontsize = 18)
        plt.xlabel("Inter-X Time (Days/PBI)", fontweight ='bold', fontsize = 15)
        plt.ylabel("Number of Instances", fontweight ='bold', fontsize = 15)
        plt.tight_layout()
        plt.legend()
        plt.savefig(nme+'_Exp_'+g+'.png')
        #plt.show()
        plt.clf()
        
        os.chdir(path)
        return([Chi_s, DoF])

# Stability Chart
def my_plot_stability(t_ba, arr_cum, t_bs, ser_cum, t_b, back, t_ave_a, arr_ls, lamda, t_ave_s, ser_ls, mu, sname, psi, g):
    plt.rcParams["figure.figsize"] = (10, 7)
    plt.plot(t_ba, arr_cum, label = "Cumulative Arrivals("+g+")", color="green", linestyle="-")
    plt.plot(t_ave_a, arr_ls, label = r"$\lambda$: "+str(round(lamda,3)), color="green", linestyle=":")
    plt.plot(t_bs, ser_cum, label = "Cumulative Services("+g+")", color="red", linestyle="-")
    plt.plot(t_ave_s, ser_ls, label = r"$\mu$: "+str(round(mu,3)), color="red", linestyle=":")
    plt.plot(t_b, back, label = "Measured System Size("+g+")", color="blue", linestyle="-")
    plt.title(sname+r' -  $\Psi$('+g+'): '+str(psi), fontweight ='bold', fontsize = 18)
    plt.xlabel('Time', fontweight ='bold', fontsize = 15)
    plt.ylabel('PBIs (Calculated)', fontweight ='bold', fontsize = 15)
    plt.legend(loc='upper left')
    plt.ylim((0, 1.1*arr_cum[-1])) # The best fit line was dragging this below 0.
    plt.tight_layout()
    plt.savefig(sname+'_'+'_Stability_'+g+'.png')
    #plt.show()
    plt.clf() 

# Create a feedback and control chart based on lots of information

def my_plot_feed_ctrl(t_bf, alp_cum, t_be, err_cum, t_bc, cxl_cum, 
                      t_bs, ser_cum,
                      t_ave_f, alp_ls, alpha, 
                      t_ave_e, err_ls, epsilon,
                      t_ave_c, cxl_ls, gamma,
                      t_ave_s, ser_ls, mu,
                      t_b, back, t_beta, beta, 
                      sname, g):
    plt.rcParams["figure.figsize"] = (10, 7)
    if len(t_bf) == len(alp_cum):
        plt.plot(t_bf, alp_cum, label = "Cumulative Planned", color="purple", linestyle="-")
    plt.plot(t_ave_f, alp_ls, label = "\u03B1("+g+"): "+str(round(alpha,3))+" PBIs/day", color="purple", linestyle=":")
    if len(t_be) == len(err_cum):
        plt.plot(t_be, err_cum, label = "Cumulative Unplanned", color="pink", linestyle="-")
    plt.plot(t_ave_e, err_ls, label = "\u03B5("+g+"): "+str(round(epsilon,3))+" PBIs/day", color="pink", linestyle=":")
    if len(t_bc) == len(cxl_cum):
        plt.plot(t_bc, cxl_cum, label = "Cumulative Cancelled", color="orange", linestyle="-")
    plt.plot(t_ave_c, cxl_ls, label = "\u03B3("+g+"): "+str(round(gamma,3))+" PBIs/day", color="orange", linestyle=":")
    plt.plot(t_bs, ser_cum, label = "Cumulative Services", color="red", linestyle="-")
    plt.plot(t_ave_s, ser_ls, label = "\u03BC("+g+"): "+str(round(mu,3))+" PBIs/day", color="red", linestyle=":")
    plt.plot(t_b, back, label = "Measured System Size", color="blue", linestyle="-")
    plt.plot(t_beta, beta, label = "Modelled System Size", color="cyan", linestyle=":")
    plt.title(sname+' - Planned, Unplanned, Done  and Cancelled' , fontweight ='bold', fontsize = 18)
    plt.xlabel('Time', fontweight ='bold', fontsize = 15)
    plt.ylabel('PBIs (Calculated)', fontweight ='bold', fontsize = 15)
    plt.legend(loc='upper left')
    plt.ylim(0, 1.1*max(alp_cum[-1],err_cum[-1],cxl_cum[-1],ser_cum[-1],back[-1])) # The best fit line was dragging this below 0.
    plt.xlim(t_b[0]-timedelta(days=10),t_b[-1]+timedelta(days=10))
    plt.tight_layout()
    plt.savefig(sname+'_'+'_FeedbackAndControl_'+g+'.png')
    #plt.show()
    plt.clf() 

# Return a strategy based on information
def my_strategy(psi, inventory_days, g):
    if psi < 1:
         if inventory_days < 30:
             strategy="Start-up"
         else:
             strategy="Scale-up"
    else:
         if inventory_days < 30:
             strategy="Plan-up"
         else:
            strategy="Catch-up" 
    
    plt.rcParams["figure.figsize"] = (10, 7)
    plt.scatter([inventory_days], [psi], label = g, color='red', marker="X")
    plt.plot([0,60], [0.9,0.9], color='green', linestyle=':')
    plt.plot([0,60], [1.1,1.1], color='green', linestyle=':')
    plt.plot([0,0], [0.9,1.1], color='green', linestyle=':')
    plt.plot([60,60], [0.9,1.1], color='green', linestyle=':')

    plt.plot([-50000,50000], [1,1], color='blue', linestyle='dashed')
    plt.plot([30,30], [-50000,50000], color='blue', linestyle='dashed')
    
    if inventory_days > 60:
        plt.xlim(30-(1.5*(inventory_days-30)),30+(1.5*(inventory_days-30)))
    else:
        plt.xlim(0,60)
           
    if psi > 2:
        plt.ylim(1-(1.5*(psi-1)),1+(1.5*(psi-1)))
    else:
        plt.ylim(0,2)

    plt.text(5.5, 0.85, 'Start-up ', style='italic', 
             horizontalalignment='right',
             verticalalignment='top',
             bbox={'facecolor': 'orange', 'alpha': 0.5, 'pad':0.5})
    plt.text(54.5, 0.85, 'Scale-up', style='italic', 
             horizontalalignment='left',
             verticalalignment='top',
             bbox={'facecolor': 'red', 'alpha': 0.5, 'pad':0.5})
    plt.text(5.5, 1.15, 'Plan-up', style='italic', 
             horizontalalignment='right',
             verticalalignment='bottom',
             bbox={'facecolor': 'cyan', 'alpha': 0.5, 'pad':0.5})
    plt.text(54.5, 1.15, 'Catch-up', style='italic', 
             horizontalalignment='left',
             verticalalignment='bottom',
             bbox={'facecolor': 'green', 'alpha': 0.5, 'pad':0.5})
    
    plt.xlabel("Inventory Days", fontweight ='bold', fontsize = 15)
    plt.ylabel("Stability Metric", fontweight ='bold', fontsize = 15)
    plt.title("Strategy for "+str(sname)+": "+strategy, fontweight ='bold', fontsize = 18)
    plt.legend()
    plt.tight_layout()
    plt.savefig(sname+'_Strategy_'+strategy+'_'+g+'.png')
    #plt.show()
    plt.clf()
    
    return(strategy)

def my_last100(t_x, cumg, first_r):
    t_x100 = []
    x100 = []
    i = 0
    while i < len(t_x):
        if t_x[i] >= first_r:
            t_x100.append(t_x[i])
            x100.append(cumg[i])
        i = i + 1
    if len(t_x100) == 0:
        t_x100 = [first_r, first_r] 
        x100 = [0,0]
    
    lso = my_leastsquares(first_r, t_x100, x100)

    return(lso[0],t_x100,x100,lso[1],lso[2],lso[3])

## Open Yaml File of inputs and read the important ones
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
newpath = os.path.join(newpath0, "3_Strategy")
if not os.path.exists(newpath):
    os.makedirs(newpath)
os.chdir(newpath)  

## Extract All data
last_pbi = datetime(1901, 1, 1, 12, 1) # initally set this to a very early date
all_start_date = last_pbi # For all set this to an early date
extract = my_extractor(data, last_pbi, all_start_date)
last_pbi = extract[2] 
buckets = extract[3]
plan = buckets[0]
unpl = buckets[1]
canc = buckets[2]
done = buckets[3]
wips = buckets[4]
t_bi = extract[4]
t_b = t_bi[0]
back = t_bi[1]
min_backlog = t_bi[2]

## Timelines, Least Squares and Slopes
# Planned (story/feature/task/idea) timeline, and least squares line
alpha_outs = my_timeanalysis(plan, arr_loc, date_format, all_start_date) 
alpha = alpha_outs[0] # Slope of the least squares line through all datapoints
t_bf = alpha_outs[1] # timeline 
alp_cum = alpha_outs[2] # Cumulative flow data 
alp_ls = alpha_outs[3] # Line of least squares
R2_alpha = alpha_outs[4] # R-squared value for least squares
c_alpha = alpha_outs[5] # y value at x=0. The c in y = mx+c
t_ave_f = [t_bf[0],t_bf[-1]] # Get first and last elements 

# Unplanned (defect/bug/error) timeline
epsilon_outs = my_timeanalysis(unpl, arr_loc, date_format, all_start_date) 
epsilon = epsilon_outs[0] # Slope of the least squares line through all datapoints
t_be = epsilon_outs[1] # timeline
err_cum = epsilon_outs[2] # Cumulative flow data 
err_ls = epsilon_outs[3] # Line of least squares
R2_epsilon = epsilon_outs[4] # R-squared value for least squares
c_epsilon = epsilon_outs[5] # y value at x=0. The c in y = mx+c
t_ave_e = [t_be[0],t_be[-1]] # Get first and last elements 

if len(t_bf) == 0:
    t_bf = t_be # This workaround is needed to allow plots (of 0) to appear

# Cancelled timeline 
gamma_outs = my_timeanalysis(canc, ser_loc, date_format, all_start_date) 
gamma = gamma_outs[0] # Slope of the least squares line through all datapoints
t_bc = gamma_outs[1] # timeline
cxl_cum = gamma_outs[2] # Cumulative flow data 
cxl_ls = gamma_outs[3] # Line of least squares
R2_gamma = gamma_outs[4] # R-squared value for least squares
c_gamma = gamma_outs[5] # y value at x=0. The c in y = mx+c
t_ave_c = [t_bc[0],t_bc[-1]] # Get first and last elements

# Net arrivals timeline
# Lambda = Alpha + Epsilon - Gamma. This means it has to be calculated slightly differently than the rest as it is a combination of the arrival timestamp and the resolution timestamp
lamda_outs = []
if t_be[0] != all_start_date: # Do not append when no data exists
    for i in t_be:
        lamda_outs.append([i,1])
if t_bf[0] != all_start_date: # Do not append when no data exists
    for i in t_bf:
        lamda_outs.append([i,1])
if t_bc[0] != all_start_date: # Do not append when no data exists
    for i in t_bc:
        lamda_outs.append([i,-1])
lamda_outs = sorted(lamda_outs, reverse=False)
t_ba = []
arr_cum = []
cuml = 0 
for i in lamda_outs:
    t_ba.append(i[0])
    cuml = cuml + i[1]
    arr_cum.append(cuml)
louts = my_leastsquares(t_ba[0], t_ba, arr_cum)
lamda = louts[0] # Slope of the least squares line through all datapoints
arr_ls = louts[1] # Line of least squares
R2_lambda = louts[2] # R-squared value for least squares
c_arr = louts[3] # y value at x=0. The c in y = mx+c
t_ave_a = [t_ba[0],t_ba[-1]] # Get first and last elements

# Services timeline
mu_outs = my_timeanalysis(done, ser_loc, date_format, all_start_date) 
mu = mu_outs[0] # Slope of the least squares line through all datapoints
t_bs = mu_outs[1] # timeline
ser_cum = mu_outs[2] # Cumulative flow data 
ser_ls = mu_outs[3] # Line of least squares
R2_mu = mu_outs[4] # R-squared value for least squares
c_mu = mu_outs[5] # y value at x=0. The c in y = mx+c
t_ave_s = [t_bs[0],t_bs[-1]] # Get first and last elements  

# Comparing the model backlog to the actual
beta = []
t_beta = []
model = []
alpha_contrib = []
epsilon_contrib = []
gamma_contrib = []
mu_contrib = []
min_b = 0
t = t_b[0]
while t <= t_b[-1]:
    y_alpha = round(alpha * (t-t_bf[0]).days + c_alpha)
    y_epsilon = round(epsilon * (t-t_be[0]).days + c_epsilon)
    y_gamma = round(gamma * (t-t_bc[0]).days + c_gamma)
    y_mu = round(mu * (t-t_bs[0]).days + c_mu)
    if y_alpha < 0:
        y_alpha = 0
    if y_epsilon < 0:
        y_epsilon = 0
    if y_gamma < 0:
        y_gamma = 0
    if y_mu < 0:
        y_mu = 0
    b = y_alpha + y_epsilon - y_gamma - y_mu
    
    alpha_contrib.append(y_alpha)
    epsilon_contrib.append(y_epsilon)
    gamma_contrib.append(y_gamma)
    mu_contrib.append(y_mu)

    if b < 0:
        b = 0
    beta.append(b)
    t_beta.append(t)
    mod = [t,b,y_alpha,y_epsilon,y_gamma,y_mu]
    model.append(mod)
    # Assess minimum backlog
    t = t + timedelta(days=1)
Beta_end = beta[-1]

# Percentage error between the modelled system size and actual. Includes workaround for the situation where the system is of size 0
if back[-1] > 0:
    mod_err = round(abs(Beta_end-(back[-1]-min_backlog))/(back[-1]-min_backlog),2)
else:
    if Beta_end == 0:
        mod_err = 0
    else:
        mod_err = 1  

## Metrics 
if alpha == "NaN" or epsilon == "NaN" or gamma == "NaN" or mu == "NaN":
    psi = "NaN"
    nu = "NaN"
    zeta = "NaN"
    inventory_days = "NaN"
else:
    # Stability
    if gamma != alpha+epsilon:
       psi = round(mu / (alpha+epsilon-gamma),3)
    else:
       psi = "NaN"
    # Quality
    if alpha+epsilon > 0:
        nu = round((alpha) / (alpha+epsilon),3)
    else:
        nu = "NaN"
    # Control
    if alpha+epsilon > 0:
        zeta = round((alpha+epsilon-gamma) / (alpha+epsilon),3)
    else:
        zeta = "NaN"
    # Inventory Days
    if mu != 0:
        inventory_days = round(back[-1]/mu,3)
    else:
        inventory_days = "NaN"
# Strategy
if psi == "NaN" or inventory_days == "NaN":
    strategy = "Indeterminate" 
else:
    strategy=my_strategy(psi, inventory_days, "all")

# Plots
my_plot_stability(t_ba, arr_cum, t_bs, ser_cum, t_b, back, t_ave_a, arr_ls, lamda, t_ave_s, ser_ls, mu, sname, psi, "all") 
my_plot_feed_ctrl(t_bf, alp_cum, t_be, err_cum, t_bc, cxl_cum, t_bs, ser_cum, 
                   t_ave_f, alp_ls, alpha, t_ave_e, err_ls, epsilon, t_ave_c, 
                   cxl_ls, gamma, t_ave_s, ser_ls, mu, t_b, back, t_beta, beta, 
                   sname, "all")

# Exponential and Poisson Distributions
GoFs = my_poisson(t_bs, mu, sname+'_'+'Services', "all")
GoFa = my_poisson(t_ba, lamda, sname+'_'+'Arrivals', "all")
GoFf = my_poisson(t_bf, alpha, sname+'_'+'Planned', "all")
GoFe = my_poisson(t_be, epsilon, sname+'_'+'Unplanned', "all")
GoFc = my_poisson(t_bc, gamma, sname+'_'+'Cancelled', "all")

# Open Output files and write
f = open(sname+"_StrategicAnalysis.txt", "w", encoding="utf-8")
f.write("\nSystem Name: "+sname+"\n")
t_delta = (t_b[-1]-t_b[0]).days # Count the number of days in the system duration
f.write("System Duration (Captured): "+str(t_delta)+" days\n\n")

f.write("Calculated Final System Size: "+str(back[-1])+" PBIs\n")     
f.write("Minimum System Size: "+str(min_backlog)+" PBIs\n") 
f.write("Corrected Final System Size (prevent below 0 backlog): "+str(back[-1] + abs(min_backlog))+" PBIs\n\n")

f.write("Model Final System Size: "+str(Beta_end)+" PBIs\n")     
f.write("Minimum System Size: "+str(min_b)+" PBIs\n") 
f.write("Corrected Final System Size (prevent below 0 backlog): "+str(beta[-1])+" PBIs\n\n")
f.write("% Error, Final backlog, model vs actual: "+str(round(100*mod_err,2))+"%\n")
f.write("Error, Final backlog, model vs actual: "+str(Beta_end-back[-1]-min_backlog)+" PBIs\n\n")

f.write("WHOLE SYSTEM\n")
f.write("Totals:\n")
f.write("Total Planned Arrivals: "+str(alp_cum[-1])+" PBIs\n")
f.write("Total Unplanned Arrivals: "+str(err_cum[-1])+" PBIs\n")
f.write("Total Cancelled/Rejected/Won't Do Arrivals: "+str(cxl_cum[-1])+" PBIs\n")
f.write("Total Net Arrivals: "+str(alp_cum[-1]+err_cum[-1]-cxl_cum[-1])+" PBIs\n")
f.write("Total Services: "+str(ser_cum[-1])+" PBIs\n")
f.write("\nRates:\n")
f.write("Planned Arrival Rate: "+str(alpha)+" PBIs/day\n")
f.write("Unplanned Arrival Rate: "+str(epsilon)+" PBIs/day\n")
f.write("Cancelled/Rejected/Won't Do Rate: "+str(gamma)+" PBIs/day\n")
f.write("Net Arrival Rate: "+str(round(alpha+epsilon-gamma,3))+" PBIs/day\n")
f.write("Service Rate: "+str(round(mu,3))+" PBIs/day\n\n")
f.write("\nMetrics:\n")
f.write("Stability: "+str(psi)+"\n")
f.write("Quality: "+str(nu)+"\n") 
f.write("Control: "+str(zeta)+"\n")       
f.write("Inventory Days: "+str(inventory_days)+" days to backlog 0 with no additional PBIs. Note: based on measured minimum backlog size\n\n")

f.write("Recommended High-Level Strategy: "+strategy+"\n\n")

g = open("ReadyReckonerInputs_All.csv", "w", encoding="utf-8")
g.write("System,Group,Duration Analysed (days),Start Date & Time (date),End Date & Time (date),\
Total PBIs (PBIs),Filtered PBIs (PBIs),\
Planned Arrivals (PBIs),Unplanned Arrivals (PBIs),Cancelled Arrivals (PBIs),\
Net Arrivals (PBIs),Services (PBIs),Measured System Size (PBIs),\
Planned Arrival Rate - alpha (PBIs/day),Unplanned Arrival Rate - epsilon (PBIs/day),\
Cancelled Rate - gamma (PBIs/day),Service Rate - mu (PBIs/day),\
Psi,Nu,Zeta,Inventory Days,Strategy,\
alpha R^2,epsilon R^2,gamma R^2,mu R^2,\
Date/Time of Analysis,Notes\n")
g.write(sname+",All,"+str(t_delta)+","+str(t_b[0])+","+str(t_b[-1])+",")
g.write(str(len(data))+","+str(alp_cum[-1]+err_cum[-1])+",")
g.write(str(alp_cum[-1])+","+str(err_cum[-1])+","+str(cxl_cum[-1])+",")
g.write(str(alp_cum[-1]+err_cum[-1]-cxl_cum[-1])+","+str(ser_cum[-1])+","+str(back[-1])+",")
g.write(str(alpha)+","+str(epsilon)+",")
g.write(str(gamma)+","+str(mu)+",")
g.write(str(psi)+","+str(nu)+","+str(zeta)+","+str(inventory_days)+","+strategy+",")
g.write(str(R2_alpha)+","+str(R2_epsilon)+","+str(R2_gamma)+","+str(R2_mu)+",")
g.write(str(datetime.now())+",,\n")
g.close

## Last 100 days unfiltered charts
last100_start_date = last_pbi - timedelta(days=100)

## Timelines, Least Squares and Slopes
# Incomplete PBIs
incomplete_outs = my_last100(t_b, back, last100_start_date)
t_b = incomplete_outs[1]
back = incomplete_outs[2]

# Planned (story/feature/task/idea) timeline, and least squares line
if t_bf[0] != all_start_date: # Do not update when no data exists Note: this is a risky strategy - it might make more sense to use different varaible names in future
    alpha_outs = my_last100(t_bf, alp_cum, last100_start_date)
    alpha = alpha_outs[0] # Slope of the least squares line through all datapoints
    t_bf = alpha_outs[1] # timeline 
    alp_cum = alpha_outs[2] # Cumulative flow data 
    alp_ls = alpha_outs[3] # Line of least squares
    R2_alpha = alpha_outs[4] # R-squared value for least squares
    c_alpha = alpha_outs[5] # y value at x=0. The c in y = mx+c
    t_ave_f = [t_bf[0],t_bf[-1]] # Get first and last elements 

# Unplanned (defect/bug/error) timeline
if t_be[0] != all_start_date: # Do not update when no data exists Note: this is a risky strategy - it might make more sense to use different varaible names in future
    epsilon_outs = my_last100(t_be, err_cum, last100_start_date) 
    epsilon = epsilon_outs[0] # Slope of the least squares line through all datapoints
    t_be = epsilon_outs[1] # timeline
    err_cum = epsilon_outs[2] # Cumulative flow data 
    err_ls = epsilon_outs[3] # Line of least squares
    R2_epsilon = epsilon_outs[4] # R-squared value for least squares
    c_epsilon = epsilon_outs[5] # y value at x=0. The c in y = mx+c
    t_ave_e = [t_be[0],t_be[-1]] # Get first and last elements 

if len(t_bf) == 0:
    t_bf = t_be # This workaround is needed to allow plots (of 0) to appear

# Cancelled timeline 
if t_bc[0] != all_start_date: # Do not update when no data exists Note: this is a risky strategy - it might make more sense to use different varaible names in future
    gamma_outs = my_last100(t_bc, cxl_cum, last100_start_date) 
    gamma = gamma_outs[0] # Slope of the least squares line through all datapoints
    t_bc = gamma_outs[1] # timeline
    cxl_cum = gamma_outs[2] # Cumulative flow data 
    cxl_ls = gamma_outs[3] # Line of least squares
    R2_gamma = gamma_outs[4] # R-squared value for least squares
    c_gamma = gamma_outs[5] # y value at x=0. The c in y = mx+c
    t_ave_c = [t_bc[0],t_bc[-1]] # Get first and last elements
 

# Net arrivals timeline
lamda_outs = my_last100(t_ba, arr_cum, last100_start_date) 
lamda = lamda_outs[0] # Slope of the least squares line through all datapoints
t_ba = lamda_outs[1] # timeline
arr_cum = lamda_outs[2] # Cumulative flow data 
arr_ls = lamda_outs[3] # Line of least squares
R2_lambda = lamda_outs[4] # R-squared value for least squares
c_arr = lamda_outs[5] # y value at x=0. The c in y = mx+c
t_ave_a = [t_ba[0],t_ba[-1]] # Get first and last elements

# Services timeline
mu_outs = my_last100(t_bs, ser_cum, last100_start_date) 
mu = mu_outs[0] # Slope of the least squares line through all datapoints
t_bs = mu_outs[1] # timeline
ser_cum = mu_outs[2] # Cumulative flow data 
ser_ls = mu_outs[3] # Line of least squares
R2_mu = mu_outs[4] # R-squared value for least squares
c_mu = mu_outs[5] # y value at x=0. The c in y = mx+c
t_ave_s = [t_bs[0],t_bs[-1]] # Get first and last elements  

# Percentage error between the modelled system size and actual. Includes workaround for the situation where the system is of size 0
if back[-1] > 0:
    mod_err = round(abs(Beta_end-(back[-1]-min_backlog))/(back[-1]-min_backlog),2)
else:
    if Beta_end == 0:
        mod_err = 0
    else:
        mod_err = 1  

## Metrics
if alpha == "NaN" or epsilon == "NaN" or gamma == "NaN" or mu == "NaN":
    psi = "NaN"
    nu = "NaN"
    zeta = "NaN"
    inventory_days = "NaN"
else:
    # Stability
    if gamma != alpha+epsilon:
       psi = round(mu / (alpha+epsilon-gamma),3)
    else:
       psi = "NaN"
    # Quality
    if alpha+epsilon > 0:
        nu = round((alpha) / (alpha+epsilon),3)
    else:
        nu = "NaN"
    # Control
    if alpha+epsilon > 0:
        zeta = round((alpha+epsilon-gamma) / (alpha+epsilon),3)
    else:
        zeta = "NaN"
    # Inventory Days
    if mu != 0:
        inventory_days = round(back[-1]/mu,3)
    else:
        inventory_days = "NaN"
    # Strategy
    if psi != "NaN":
        if inventory_days != "NaN":
            strategy=my_strategy(psi, inventory_days, "last100")
    else:
       strategy = "Indeterminate" 
    
    my_plot_stability(t_ba, arr_cum, t_bs, ser_cum, t_b, back, t_ave_a, arr_ls, lamda, t_ave_s, ser_ls, mu, sname, psi, "last100") 
    my_plot_feed_ctrl(t_bf, alp_cum, t_be, err_cum, t_bc, cxl_cum, t_bs, ser_cum, 
                        t_ave_f, alp_ls, alpha, t_ave_e, err_ls, epsilon, t_ave_c, 
                        cxl_ls, gamma, t_ave_s, ser_ls, mu, t_b, back, t_beta, beta, 
                        sname, "last100")

    # Exponential and Poisson Distributions
    GoFs = my_poisson(t_bs, mu, sname+'_'+'Services', "last100")
    GoFa = my_poisson(t_ba, lamda, sname+'_'+'Arrivals', "last100")
    GoFf = my_poisson(t_bf, alpha, sname+'_'+'Planned', "last100")
    GoFe = my_poisson(t_be, epsilon, sname+'_'+'Unplanned', "last100")
    GoFc = my_poisson(t_bc, gamma, sname+'_'+'Cancelled', "last100")

# Open Output files and write
f.write("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\nLast 100 days only\n")
t_delta = (t_b[-1]-t_b[0]).days # Count the number of days in the system duration
f.write("System Duration (Captured): "+str(t_delta)+" days\n\n")

f.write("Calculated Final System Size: "+str(back[-1])+" PBIs\n")     
f.write("Minimum System Size: "+str(min_backlog)+" PBIs\n") 
f.write("Corrected Final System Size (prevent below 0 backlog): "+str(back[-1] + abs(min_backlog))+" PBIs\n\n")

f.write("LAST 100 DAYS\n")
f.write("Totals:\n")
f.write("Planned Arrivals in this period: "+str(alp_cum[-1]-alp_cum[0])+" PBIs\n")
f.write("Unplanned Arrivals in this period: "+str(err_cum[-1]-err_cum[0])+" PBIs\n")
f.write("Cancelled/Rejected/Won't Do  in this period: "+str(cxl_cum[-1]-cxl_cum[0])+" PBIs\n")
f.write("System size change in this period: "+str(back[-1]-back[0])+" PBIs\n")
f.write("Net Arrivals in this period: "+str(alp_cum[-1]-alp_cum[0]+err_cum[-1]-err_cum[0]-cxl_cum[-1]+cxl_cum[0])+" PBIs\n")
f.write("Services in this period: "+str(ser_cum[-1]-ser_cum[0])+" PBIs\n")
f.write("\nRates:\n")
f.write("Planned Arrival Rate: "+str(alpha)+" PBIs/day\n")
f.write("Unplanned Arrival Rate: "+str(epsilon)+" PBIs/day\n")
f.write("Cancelled/Rejected/Won't Do Rate: "+str(gamma)+" PBIs/day\n")
f.write("Net Arrival Rate: "+str(lamda)+" PBIs/day\n")
f.write("Service Rate: "+str(mu)+" PBIs/day\n")
f.write("\nMetrics:\n")
f.write("Stability: "+str(psi)+"\n")
f.write("Quality: "+str(nu)+"\n") 
f.write("Control: "+str(zeta)+"\n")       
f.write("Inventory Days: "+str(inventory_days)+" days to backlog 0 with no additional PBIs. Note: based on measured minimum backlog size\n\n")

f.write("Recommended High-Level Strategy: "+strategy+"\n\n")

g = open("ReadyReckonerInputs_last100.csv", "w", encoding="utf-8")
g.write("System,Group,Duration Analysed (days),Start Date & Time (date),End Date & Time (date),\
Total PBIs (PBIs),Filtered PBIs (PBIs),\
Planned Arrivals (PBIs),Unplanned Arrivals (PBIs),Cancelled Arrivals (PBIs),\
Net Arrivals (PBIs),Services (PBIs),Measured System Size (PBIs),\
Planned Arrival Rate - alpha (PBIs/day),Unplanned Arrival Rate - epsilon (PBIs/day),\
Cancelled Rate - gamma (PBIs/day),Service Rate - mu (PBIs/day),\
Psi,Nu,Zeta,Inventory Days,Strategy,\
alpha R^2,epsilon R^2,gamma,mu R^2,\
Date/Time of Analysis,Notes\n")
print(alp_cum[-1],alp_cum[0],err_cum[-1],err_cum[0],cxl_cum[-1],cxl_cum[0],ser_cum[-1],ser_cum[0],back[-1],back[0])
g.write(sname+",Last100,"+str(t_delta)+","+str(t_b[0])+","+str(t_b[-1])+",")
g.write(" , ,") # It's not (straighforward) possible to get a full measure of the total and filtered for the shorter list so leaving these blank
g.write(str(alp_cum[-1]-alp_cum[0]+1)+","+str(err_cum[-1]-err_cum[0]+1)+","+str(cxl_cum[-1]-cxl_cum[0]+1)+",") # The totals amounts are the last minus the first plus 1
g.write("N/A,"+str(ser_cum[-1]-ser_cum[0]+1)+","+str(back[-1]-back[0])+",")
g.write(str(alpha)+","+str(epsilon)+",")
g.write(str(gamma)+","+str(mu)+",")
g.write(str(psi)+","+str(nu)+","+str(zeta)+","+str(inventory_days)+","+strategy+",")
g.write(str(R2_alpha)+","+str(R2_epsilon)+","+str(R2_gamma)+","+str(R2_mu)+",")
g.write(str(datetime.now())+",,\n")
g.close


f.close() 
