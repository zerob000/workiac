# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 22:00:57 2023
Last Updated: 14 Oct 2024

@author: R Healy

18 Oct 2024 V0.04
Ironing out few remaining bugs - mostly for exceptional cases.
18 Oct 2024 V0.03
Basic system now working. Looking through major issues:
    - Handling systems with no cancellation (~76%)
    - Handling systems with no cancellation in 100D (~8%)
    - Handling systems with no feedback (~4%)
15 Oct 2024 V0.02
Code for Epsilon (feedback), Kappa(combined feedback) and Gamma(cancellation)
14 Oct 2024
V0.01 Branched from ReporterV0.98.py
15 Oct 2024
Substantial updates of code to use functions for repeated code. This *should* reduce the risks of bugs 
14 Oct 2024
V0.01 Branched from ReporterV0.98.py



"""

# importing package
import csv

# Inputs
snames = ['A',
        'AA','AB','AC','AD','AE','AF','AG','AH','AI','AJ','AK','AL','AM','AN',
        'AP','AQ','AS','AU','AV','AW','AY','AZ',
        'B',
        'BA','BB','BC','BD','BG','BH','BI','BK','BL','BM','BN','BO','BP','BQ',
        'BR','BT','BZ',
        'C',
        'CA','CB','CC','CD','CE','CF','CG','CH','CI','CJ','CK','CM','CN','CO',
        'CP','CS','CT','CU','CV','CW','CX','CY','CZ',
        'D',
        'DA','DB','DC','DD','DE','DF','DG','DI','DK','DM','DN','DO','DP','DQ',
        'DR','DT','DV','DW','DZ',
        'E',
        'EA','EB','EC','ED','EE','EF','EG','EH','EI','EJ','EK','EM','EN','EO',
        'EP','ER','ES','ET','EU','EV','EW','EX',
        'F',
        'FA','FB','FC','FD','FG','FH','FI','FJ','FL','FN','FO','FP','FQ','FR',
        'FS','FT','FU','FV','FW','FX','FY','FZ',
        'G',
        'GA','GB','GC','GD','GE','GF','GG','GH','GI','GK','GL','GM','GN','GO',
        'GP','GQ','GS','GT','GU','GV','GW','GY','GZ',
        'H',
        'HA','HC','HD','HE','HH','HI','HJ','HK','HL','HM','HN','HO','HP','HQ',
        'HR','HS','HT','HU','HV','HW','HX','HY','HZ',
        'I',
        'IA','IB','IC','ID','IE','IF','IH','II','IJ','IK','IL','IM','IN','IO',
        'IP','IQ','IR','IS','IT','IU','IV','IW','IX','IZ',
        'J',
        'JA','JB','JC','JD','JE','JF','JG','JH','JI','JJ','JK','JL','JM','JO',
        'JP','JQ','JS','JT','JV','JW','JX','JY','JZ',
        'K',
        'KA','KB','KC','KD','KE','KF','KG','KH','KI','KJ','KK','KL','KM','KN',
        'KO','KP','KQ','KR','KS','KU','KV','KW','KX','KY',
        'L',
        'LA','LB','LC','LD','LE','LF','LG','LH','LJ','LK','LM','LN','LO','LP',
        'LQ','LR','LV','LW','LY','LZ',
        'M',
        'MA','MB','MC','MD','ME','MF','MG','MH',
        'N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
        'GX']   
Unused = [] 
                                            
types = {'Story': 0, 'Task': 0, 'Bug': 0, 'Spike': 0, 'Feature Request': 0, #
         'Feature': 0, 'Outcome': 0, 'Enhancement': 0, 'Documentation': 0, 
         'Initiative': 0, 'Dev Task': 0, 'Question': 0, 'Clarification': 0, 
         'Component Upgrade': 0, 'Quality Risk': 0, 'Tracker': 0, 'Library Upgrade': 0, 
         'Release': 0, 'Technical Requirement': 0, 'Requirement': 0, 
         'Support Request': 0, 'Docs Task': 0, 'QE Task': 0, 'OKR': 0, 
         'New Feature': 0, 'Ticket': 0,  'Patch': 0, 'CTS Challenge': 0, 
         'Risk': 0, 'Improvement': 0, 
         'Release tracker': 0, 'Vulnerability': 0, 'Support Patch': 0,  
         'Analysis': 0, 'Issue': 0, 'RFE': 0, 'Incident': 0, 'Doc': 0, 
         'Closed Loop': 0, 'Change Request': 0, 'Request': 0, } # Create a dictionary of issue types

resos = {} # Create a dictionary of resolution types
status = {} # Create a dictionary of status types

id_loc =  0
sysm_loc = 2
issue_loc =  6
resol_loc: 5
status_loc = 5
arr_loc = 7
ser_loc = 8

Epic_Count = 0
for sname in snames:    
    #date_format = '%d/%m/%Y'
    #date_format = '%d/%b/%y %H:%M'
    date_format = '%d/%m/%Y %H:%M'    
    
    # Import CSV
    file = open(str(sname)+".csv", "r", encoding="utf8") 
    data = list(csv.reader(file, delimiter=","))
    file.close()
    
    del data[0] # Strip header line
    
    print(sname,len(data))
    

    ids = []
    for i in range(len(data)):
        item = data[i]


        # Count the number of issue types
        if item[issue_loc] in types:
            types[item[issue_loc]] = types[item[issue_loc]] + 1
            # Count the number of resolutions/statuses
            if item[status_loc] in status:
                status[item[status_loc]] = status[item[status_loc]] + 1
            else:
                status[item[status_loc]] = 1 
        else:
            #types[item[issue_loc]] = 1  
            Epic_Count = Epic_Count + 1
            

print(types)
print(Epic_Count)  
print(status)  
  

