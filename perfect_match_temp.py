import json
import math
import os
import re

import numpy as np
import pandas as pd
import rdflib
import requests
import simplejson as json
from openpyxl import load_workbook

notebook_path = os.path.abspath("perfect_match.py")

# Path to config file
config_path = os.path.join("C:\CNS\Azimuth-asctb-label-comaprison-main\Data\config.json")

# Path to asctb formatted azimuth data
az_path = os.path.join("C:\CNS\Azimuth-asctb-label-comaprison-main\Data")

with open(config_path) as config_file:
    config= json.load(config_file)
#print(config)
# Fetch ASCTB sheet LABEL from config file
asctb_sheet_id = config["asctb_sid"]

def fetch_azimuth(az_url,name):
    
    if name+'.csv' in os.listdir(az_path):
        azimuth_df= pd.read_csv (az_path+'/'+name+'.csv',skiprows=10)
    else:
        azimuth_df= pd.read_csv (az_url,skiprows=10)
    
    azimuth_all_label=[]
    azimuth_all_label_author=[]
    
    # Filter CT Label column
    azimuth_label = azimuth_df.filter(regex=("AS/[0-9]/LABEL$"))
    
    # Filter Author Label column
    azimuth_label_author = azimuth_df.filter(regex=("AS/[0-9]$"))
    
    # Flatten dataframe to list. Append CT Label in all annotation level to a single list and convert it to dataframe.
    for col in azimuth_label:
        azimuth_all_label.extend(azimuth_label[col].tolist())
    azimuth_all_label=pd.DataFrame(azimuth_all_label)
    azimuth_all_label.rename(columns = {0:"CT/LABEL"},inplace = True)
    
    # Flatten dataframe to list. Append Author Label in all annotation level to a single list and convert it to dataframe.
    for col in azimuth_label_author:
        azimuth_all_label_author.extend(azimuth_label_author[col].tolist())
    azimuth_all_label_author=pd.DataFrame(azimuth_all_label_author)
    azimuth_all_label_author.rename(columns = {0:"CT/LABEL.Author"},inplace = True)
    
    # Column bind CT/LABEL , CT/Label and Author Label column
    azimuth_all_cts_label=pd.concat([azimuth_all_label,azimuth_all_label_author],axis=1)
    
    # Remove duplicate rows
    azimuth_all_cts_label_unique=azimuth_all_cts_label.drop_duplicates()
    azimuth_all_cts_label_unique.reset_index(drop=True, inplace=True)
    
    # Return flattend dataframe before and after removing duplicates.
    return azimuth_all_cts_label,azimuth_all_cts_label_unique

# Fetch Asctb Data
# CT/2 - Represents Author label
# CT/2/Label - Represents Ontology label

def fetch_asctb(sheet_id,asctb_sheet_name):
    
    # Read ASCT+B organ table from google sheet
    asctb_df = pd.read_csv(f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={asctb_sheet_name}",skiprows=3) 
    
    # Filter CT Label column
    asctb_label = asctb_df.filter(regex=("CT/[0-9]/LABEL$"))
    
    # Filter Author Label column
    asctb_label_author = asctb_df.filter(regex=("CT/[0-9]$"))

    asctb_all_label=[]
    asctb_all_label_author=[]

    # Flatten dataframe to list. Append CT Labels in all annotation level to a single list and convert it to dataframe.
    for col in asctb_label:
        asctb_all_label.extend(asctb_label[col].tolist())
    asctb_all_label=pd.DataFrame(asctb_all_label)
    asctb_all_label.rename(columns = {0:"CT/LABEL"},inplace = True)
    
    # Flatten dataframe to list. Append Author Label in all annotation level to a single list and convert it to dataframe.
    for col in asctb_label_author:
        asctb_all_label_author.extend(asctb_label_author[col].tolist())
    asctb_all_label_author=pd.DataFrame(asctb_all_label_author)
    asctb_all_label_author.rename(columns = {0:"CT/LABEL.Author"},inplace = True)
    
    # Column bind  CT/Label and Author Label column
    asctb_all_cts_label=pd.concat([asctb_all_label,asctb_all_label_author],axis=1)
    #asctb_all_cts_label.dropna(how='all')
    
    # Remove duplicate rows
    asctb_all_cts_label_unique=asctb_all_cts_label.drop_duplicates().dropna()
    asctb_all_cts_label_unique.reset_index(drop=True, inplace=True)
    
    # Return flattend dataframe before and after removing duplicates.
    print(asctb_all_cts_label_unique)
    return asctb_all_cts_label,asctb_all_cts_label_unique

# Check whether the Azimuth CT LABEL (label_az) is present in ASCT+B. asctb_all_cts_label_unique is a dataframe that contains
# unique CT/LABEL and author label for a reference organ.

# i and j are the index pointing to corresponding row in Azimuth and ASCT+B dataframe respectively. 
# i is the row number of cl_az in Azimuth dataframe.
# j points to the row number in ASCT+B where cl_az matches in ASCT+B.
# az_row_matched_index,asctb_row_matched_index are global lists used to store these the row number of Azimuth, ASCT+B 

# not_matching_az is a list storing index of Azimuth CT(label_az) that does not match to any CT in ASCT+B. 
# And if there is a match then we append azimuth row to the list az_row_matched_index and corresponding ASCT+B row number 
# to asctb_row_matched_index

def check_in_asctb(label_az,i,asctb_all_cts_label_unique,az_row_matched_index,asctb_row_matched_index,not_matching_az):    
    
    flag=0
    #removed special character from label_az
    label_az_cleaned = re.sub(r"[^a-zA-Z0-9 ]","",label_az) 
    #trimmed and converted into lower case
    label_az_lower_nospace = label_az_cleaned.strip().lower().replace(" ", "") 

    for j in range(len(asctb_all_cts_label_unique['CT/LABEL'])):
         #removed special character from asctb label
        asctb_label_cleaned= re.sub(r"[^a-zA-Z0-9 ]","",asctb_all_cts_label_unique['CT/LABEL'][j])
         #trimmed and converted into lower case
        asctb_label_lower_nospace = asctb_label_cleaned.strip().lower().replace(" ", "")
         #removed special character from asctb label
        asctb_label_author_cleaned= re.sub(r"[^a-zA-Z0-9 ]","",asctb_all_cts_label_unique['CT/LABEL.Author'][j])
         #trimmed and converted into lower case
        asctb_label_author_lower_nospace = asctb_label_author_cleaned.strip().lower().replace(" ", "")

        
        if label_az_lower_nospace == asctb_label_lower_nospace:
            # direct matching label_az with astcb label 
            az_row_matched_index.append(i) 
            asctb_row_matched_index.append(j)
            
            flag=1

        elif label_az_lower_nospace ==asctb_label_lower_nospace[:-1]:
            #direct matching label_az with astcb label with removing last element in case 's' in asctb label is the last element like Label: "Cell's'"
            az_row_matched_index.append(i) 
            asctb_row_matched_index.append(j)
            
            flag=1

        elif label_az_lower_nospace[:-1] == asctb_label_lower_nospace:
            #direct matching label_az with astcb label with removing last element in case 's' in label_az is the last element like Label: "Cell's'"
            az_row_matched_index.append(i) 
            asctb_row_matched_index.append(j)
            
            flag=1
        elif label_az_lower_nospace == asctb_label_author_lower_nospace:
            # direct matching label_az with astcb label author
            az_row_matched_index.append(i) 
            asctb_row_matched_index.append(j)
            
            flag=1

        elif label_az_lower_nospace ==asctb_label_author_lower_nospace[:-1]:
            #direct matching label_az with astcb label author with removing last element in case 's' in asctb label is the last element like Label: "Cell's'"
            az_row_matched_index.append(i) 
            asctb_row_matched_index.append(j)
            
            flag=1

        elif label_az_lower_nospace[:-1] == asctb_label_author_lower_nospace:
            #direct matching label_az with astcb label author with removing last element in case 's' in label_az is the last element like Label: "Cell's'"
            az_row_matched_index.append(i) 
            asctb_row_matched_index.append(j)
            
            flag=1

    if flag==0:
        not_matching_az.append(i)

def perfect_match_for_azimuthct_in_asctb(azimuth_all_cts_label_unique,asctb_all_cts_label_unique):
    
    # az_row_matched_index ,asctb_row_matched_index List to store index number of ASCTB, Azimuth row number where a match is occuring
    # not_matching_az list stores Azimuth row number where CT/LABEL match is not found
    
    az_row_matched_index=[]
    asctb_row_matched_index=[]
    not_matching_az=[]
    
    for i in range(len(azimuth_all_cts_label_unique['CT/LABEL'])):  

        if azimuth_all_cts_label_unique['CT/LABEL'][i]!="":
            check_in_asctb(azimuth_all_cts_label_unique['CT/LABEL'][i],i,asctb_all_cts_label_unique,az_row_matched_index,asctb_row_matched_index,not_matching_az)
        else:
            not_matching_az.append(i)

    for i in range(len(azimuth_all_cts_label_unique['CT/LABEL.Author'])):  

        if azimuth_all_cts_label_unique['CT/LABEL.Author'][i]!="":
            check_in_asctb(azimuth_all_cts_label_unique['CT/LABEL.Author'][i],i,asctb_all_cts_label_unique,az_row_matched_index,asctb_row_matched_index,not_matching_az)
        else:
            not_matching_az.append(i)

    # Subset Azimuth and ASCTB dataframe by rows were a match is found.
    az_matches_all=azimuth_all_cts_label_unique.loc[az_row_matched_index]
    asctb_matches_all=asctb_all_cts_label_unique.loc[asctb_row_matched_index]

    az_matches_all.reset_index(drop=True,inplace=True)
    asctb_matches_all.reset_index(drop=True,inplace=True)
    
    
    az_matches_all.rename(columns = {"CT/LABEL":"AZ.CT/LABEL","CT/LABEL.Author":"AZ.CT/LABEL.Author"},inplace = True)
    asctb_matches_all.rename(columns = {"CT/LABEL":"ASCTB.CT/LABEL","CT/LABEL.Author":"ASCTB.CT/LABEL.Author"},inplace = True)

    # Cbind both dataframes to show the perfect matches found in one dataframe
    
    perfect_matches_all=pd.concat([az_matches_all,asctb_matches_all],axis=1)
    perfect_matches_all=perfect_matches_all.drop_duplicates()
    perfect_matches_all.reset_index(drop=True, inplace=True)
    
    az_mismatches_all=azimuth_all_cts_label_unique.loc[not_matching_az]
    az_mismatches_all=az_mismatches_all.drop_duplicates()
    az_mismatches_all.reset_index(drop=True, inplace=True)
    
    # retrun Perfect matches and azimuth mismatches
    return perfect_matches_all,az_mismatches_all


def check_in_az(label_asctb,i,az_all_cts_label_unique,az_row_matched_index,asctb_row_matched_index,not_matching_asctb):    
    
    flag=0
    #removed add special character from label_asctb
    label_asctb_cleaned = re.sub(r"[^a-zA-Z0-9 ]","",label_asctb) 
    #trimmed and converted into lower case
    label_asctb_lower_nospace = label_asctb_cleaned.strip().lower().replace(" ", "") 
    
    for j in range(len(az_all_cts_label_unique['CT/LABEL'])):
        #removed special character from azimuth label
        az_label_cleaned= re.sub(r"[^a-zA-Z0-9 ]","",az_all_cts_label_unique['CT/LABEL'][j]) 
        #trimmed and converted into lower case
        az_label_lower_nospace = az_label_cleaned.strip().lower().replace(" ", "") 

        if label_asctb_lower_nospace == az_label_lower_nospace:
            # direct matching label_asctb with azimuth label
            az_row_matched_index.append(j) 
            asctb_row_matched_index.append(i)
            flag=1
            break
        
        elif label_asctb_lower_nospace == az_label_lower_nospace[:-1]:
            #direct matching label_asctb with azimuth label with removing last element in case 's' in azimuth label is the last element like Label: "Cell's'"
            az_row_matched_index.append(j) 
            asctb_row_matched_index.append(i)
            flag=1
            break
        
        elif label_asctb_lower_nospace[:-1] == az_label_lower_nospace:
            #direct matching label_asctb with azimuth label with removing last element in case 's' in label_asctb is the last element like Label: "Cell's'"
            az_row_matched_index.append(j) 
            asctb_row_matched_index.append(i)
            flag=1
            break

    if flag==0:
        not_matching_asctb.append(i)

# Check for mismatches between ASCT+B and Azimuth tables and return Asctb CT mismatches
def perfect_match_for_asctbct_in_azimuth(azimuth_all_cts_label_unique,asctb_all_cts_label_unique):
    
    az_row_matched_index=[]
    asctb_row_matched_index=[]
    not_matching_asctb=[]

    for i in range(len(asctb_all_cts_label_unique['CT/LABEL'])):

        if asctb_all_cts_label_unique['CT/LABEL'][i]!="":
            check_in_az(asctb_all_cts_label_unique['CT/LABEL'][i],i,azimuth_all_cts_label_unique,az_row_matched_index,asctb_row_matched_index,not_matching_asctb)
        else:
            not_matching_asctb.append(i)

    az_matches=azimuth_all_cts_label_unique.loc[az_row_matched_index]
    asctb_matches=asctb_all_cts_label_unique.loc[asctb_row_matched_index]

    az_matches.reset_index(drop=True,inplace=True)
    asctb_matches.reset_index(drop=True,inplace=True)

    az_matches.rename(columns = {"CT/LABEL":"AZ.CT/LABEL","CT/LABEL.Author":"AZ.CT/LABEL.Author"},inplace = True)
    asctb_matches.rename(columns = {"CT/LABEL":"ASCTB.CT/LABEL","CT/LABEL.Author":"ASCTB.CT/LABEL.Author"},inplace = True)

    perfect_matches=pd.concat([asctb_matches,az_matches],axis=1)

    asctb_mismatches=asctb_all_cts_label_unique.loc[not_matching_asctb]
    asctb_mismatches.reset_index(drop=True,inplace=True)
    
    return perfect_matches,asctb_mismatches

for ref in config['references']:
    
    name= ref['name']
    asctb_sheet_name = ref['asctb_sheet_name']
    az_url= ref['url']
    

    # Fetch Azimuth data
    azimuth_all_cts_label,azimuth_all_cts_label_unique = fetch_azimuth(az_url,name)
    azimuth_all_cts_label = azimuth_all_cts_label.dropna(axis = 0, how = 'all', inplace = False)
    azimuth_all_cts_label_unique = azimuth_all_cts_label_unique.dropna(axis = 0, how = 'all', inplace = False)
    azimuth_all_cts_label_unique.reset_index(drop=True, inplace=True)

     # Fetch ASCTB data
    asctb_all_cts_label,asctb_all_cts_label_unique = fetch_asctb(asctb_sheet_id,asctb_sheet_name)
    asctb_all_cts_label = asctb_all_cts_label.dropna(axis = 0, how = 'all', inplace = False)
    asctb_all_cts_label_unique = asctb_all_cts_label_unique.dropna(axis = 0, how = 'all', inplace = False)
    asctb_all_cts_label_unique.reset_index(drop=True, inplace=True)

    # Perfect Match and Mismatch for Azimuth CT in ASCTB (AZ - ASCTB)
    azimuth_perfect_matches,azimuth_mismatches=perfect_match_for_azimuthct_in_asctb(azimuth_all_cts_label_unique,asctb_all_cts_label_unique)
    azimuth_perfect_matches.sort_values(by=['AZ.CT/LABEL','AZ.CT/LABEL.Author'],inplace=True)

    # Mismatch for ASCTB CT in Azimuth (ASCTB - Azimuth)
    #asctb_perfect_matches,asctb_mismatches=perfect_match_for_asctbct_in_azimuth(azimuth_all_cts_label_unique,asctb_all_cts_label_unique)
#print(azimuth_all_cts_label_unique)  
#print(asctb_all_cts_label_unique)
print("\n")
print(azimuth_perfect_matches)
print("\n")
#print(asctb_perfect_matches)
print("\n")
print(azimuth_mismatches)

with pd.ExcelWriter("C:\CNS\Azimuth-asctb-label-comaprison-main/azimuth_perfect_matches.xlsx") as writer:
    azimuth_perfect_matches.to_excel(writer, sheet_name="Matched", index=False)
    azimuth_mismatches.to_excel(writer, sheet_name="Not_Matched", index=False)



