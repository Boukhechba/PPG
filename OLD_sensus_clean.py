#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  4 13:02:46 2018
@author: Mehdi
"""

import os
import time
import csv
import json 
import pandas as pd
import gzip
from collections import defaultdict



data_folder = 'C:/Users/mehdi/Documents/Python_scripts/NAKURU/raw' # Define data filepath
target_folder = 'C:/Users/mehdi/Documents/Python_scripts/NAKURU/clean' # Define folder to store clean files


absolute_start_time = time.time()

complete_data = defaultdict(list)

filenames = [os.path.join(dp, f) for dp, dn, filenames in os.walk(data_folder) for f in filenames if f.endswith('.gz')]


for i in range(len(filenames)):
    
    file = filenames[i]

    print("File " + str(i+1) + " out of " + str(len(filenames)) + ' (' + data_folder + ')'+ ' (' + file + ')') # progress print statement
#    try:
    start_time = time.time()
    if (file.endswith(".gz")):
        f = gzip.open(file, 'rb')
    elif(file.endswith(".json")):
        f = open(file)
    file_content = f.read()
    raw_data = json.loads(file_content)

    base = ''
    if 'Swear' in file:
        base = 'Smartwatch_'
    else:
        base = 'Sensus_'

    for line in raw_data:
        

        if ( 'SWear' in line["$type"]):
            data_type = line.pop("$type").split('.')[-1]
            datum = data_type
        else:
            line["Sensus OS"] = line["$type"].split(',')[1]
            line["Data Type"] = line.pop("$type").split(',')[0]
            data_type_split = line["Data Type"].split('.')
            data_type = data_type_split[len(data_type_split)-1]
            if data_type[-5:] == "Datum":
                datum = data_type[:-5]
            else:
                datum = data_type
        if "PID" in line:
            line.pop("PID")
            
            
        file = base + datum + '.csv'
        
        if datum == "Activity":
            line["Activity Mode"] = line.pop("Activity")
        complete_data[file].append(line)
        
    for key in complete_data.keys():
        print (key)
        if not (os.path.isfile(os.path.join(target_folder,key))):
            w = open(os.path.join(target_folder,key),'a')
            writer = csv.DictWriter(w, fieldnames=complete_data[key][0].keys(),lineterminator='\n')
            writer.writeheader()
        w = open(os.path.join(target_folder,key),'a')
        writer = csv.DictWriter(w, fieldnames=complete_data[key][0].keys(),lineterminator='\n')
        writer.writerows(complete_data[key])
    complete_data.clear()
    w.flush()
    elapsed_time = time.time() - start_time
    elapsed_total_time = time.time() - absolute_start_time        
        
    print("--- " +  time.strftime("%H:%M:%S", time.gmtime(elapsed_time)) +  " / " + time.strftime("%H:%M:%S", time.gmtime(elapsed_total_time)) + " --- " %())
#    except:
#        print("File corrupted")
    
f.close()
w.close()


if os.path.isfile(os.path.join(target_folder,'Sensus_Script.csv')):
    data = pd.read_csv(os.path.join(target_folder,'Sensus_Script.csv'),encoding = "ISO-8859-1")
    data = data.set_index(['RunId'])
    script_types = data.groupby('ScriptName')
    for name,group in script_types:
        data_wide = data.pivot( columns='InputId', values='Response')
        data_long = data.drop(['InputId','Timestamp','Id','GroupId','CompletionRecords','Response'], 1)
        data_long = data_long.drop_duplicates()
        result = pd.concat([data_long, data_wide], axis=1, join='inner')
        result.to_csv(os.path.join(target_folder,'Sensus_Script_'+name+'.csv'), sep=',', encoding='utf-8',index=True)