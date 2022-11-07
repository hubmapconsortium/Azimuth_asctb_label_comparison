import requests
import simplejson as json
import pandas as pd
import numpy as np
import os
import json
import math
from openpyxl import load_workbook
import re

notebook_path = os.path.abspath("perfect_match.py")

# Path to config file
config_path = os.path.join(os.path.dirname(notebook_path), "Data/config.json")

# Path to asctb formatted azimuth data
az_path = os.path.join(os.path.dirname(notebook_path), "Data/asctb_formatted_azimuth_data/")

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
    
    # Remove duplicate rows
    asctb_all_cts_label_unique=asctb_all_cts_label.drop_duplicates()
    asctb_all_cts_label_unique.reset_index(drop=True, inplace=True)
    
    # Return flattend dataframe before and after removing duplicates.
    return asctb_all_cts_label,asctb_all_cts_label_unique

# Check whether the Azimuth CT LABEL (label_az) is present in ASCT+B. asctb_all_cts_label_unique is a dataframe that contains
# unique CT/LABEL and author label for a reference organ.

# i and j are the index pointing to corresponding row in Azimuth and ASCT+B dataframe respectively. 
# i is the row number of cl_az in Azimuth dataframe.
# j points to the row number in ASCT+B where cl_az matches in ASCT+B.
# az_row_all,asctb_row_all are global lists used to store these the row number of Azimuth, ASCT+B 

# not_matching_all is a list storing index of Azimuth CT(label_az) that does not match to any CT in ASCT+B. 
# And if there is a match then we append azimuth row to the list az_row_all and corresponding ASCT+B row number 
# to asctb_row_all


def check_in_asctb(label_az,i,asctb_all_cts_label_unique,az_row_all,asctb_row_all,not_matching_all):    
    flag=0
    cellLabel1 = re.sub(r"[^a-zA-Z0-9 ]","",label_az) #removed special character from label_az
    for j in range(len(asctb_all_cts_label_unique['CT/LABEL'])):
        rs= re.sub(r"[^a-zA-Z0-9 ]","",asctb_all_cts_label_unique['CT/LABEL'][j])#removed special character from asctb label
        if label_az.strip().lower().replace(" ", "") == asctb_all_cts_label_unique['CT/LABEL'][j].strip().lower().replace(" ", ""):
            az_row_all.append(i) # direct matching label_az with astcb label by removing spaces and converting it into lower cases
            asctb_row_all.append(j)
            flag=1
        elif label_az.strip().lower().replace(" ", "") == asctb_all_cts_label_unique['CT/LABEL'][j][:-1].strip().lower().replace(" ", ""):
            az_row_all.append(i) #direct matching label_az with astcb label with removing last element in case 's' in asctb label is the last element like Label: "Cell's'"
            asctb_row_all.append(j)
            flag=1
        elif label_az[:-1].strip().lower().replace(" ", "") == asctb_all_cts_label_unique['CT/LABEL'][j].strip().lower().replace(" ", ""):
            az_row_all.append(i) #direct matching label_az with astcb label with removing last element in case 's' in label_az is the last element like Label: "Cell's'"
            asctb_row_all.append(j)
            flag=1
        elif cellLabel1.strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
            az_row_all.append(i) # direct matching cleaned label_az with  cleaned astcb label by removing spaces and converting it into lower cases
            asctb_row_all.append(j)
            flag=1
        elif cellLabel1.strip().lower().replace(" ", "") == rs[:-1].strip().lower().replace(" ", ""):
            az_row_all.append(i) #direct matching cleaned label_az with cleaned astcb label with removing last element in case 's' in asctb label is the last element like Label: "Cell's'"
            asctb_row_all.append(j)
            flag=1
        elif cellLabel1[:-1].strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
            az_row_all.append(i) #direct matching cleaned label_az with cleaned astcb label with removing last element in case 's' in label_az is the last element like Label: "Cell's'"
            asctb_row_all.append(j)
            flag=1
        
    if flag==0:
        not_matching_all.append(i)

def perfect_match_for_azimuthct_in_asctb(azimuth_all_cts_label_unique,asctb_all_cts_label_unique):
    
    # az_row_all ,asctb_row_all List to store index number of ASCTB, Azimuth row number where a match is occuring
    # not_matching_all list stores Azimuth row number where CT/LABEL match is not found
    
    az_row_all=[]
    asctb_row_all=[]
    not_matching_all=[]

    for i in range(len(azimuth_all_cts_label_unique['CT/LABEL'])):  
        if azimuth_all_cts_label_unique['CT/LABEL'][i]!="":
            check_in_asctb(azimuth_all_cts_label_unique['CT/LABEL'][i],i,asctb_all_cts_label_unique,az_row_all,asctb_row_all,not_matching_all)
        else:
            not_matching_all.append(i)
    
    # Subset Azimuth and ASCTB dataframe by rows were a match is found.
    az_matches_all=azimuth_all_cts_label_unique.loc[az_row_all]
    asctb_matches_all=asctb_all_cts_label_unique.loc[asctb_row_all]

    az_matches_all.reset_index(drop=True,inplace=True)
    asctb_matches_all.reset_index(drop=True,inplace=True)
    
    
    az_matches_all.rename(columns = {"CT/LABEL":"AZ.CT/LABEL","CT/LABEL.Author":"AZ.CT/LABEL.Author"},inplace = True)
    asctb_matches_all.rename(columns = {"CT/LABEL":"ASCTB.CT/LABEL","CT/LABEL.Author":"ASCTB.CT/LABEL.Author"},inplace = True)

    # Cbind both dataframes to show the perfect matches found in one dataframe
    
    perfect_matches_all=pd.concat([az_matches_all,asctb_matches_all],axis=1)
    perfect_matches_all=perfect_matches_all.drop_duplicates()
    perfect_matches_all.reset_index(drop=True, inplace=True)
    
    az_mismatches_all=azimuth_all_cts_label_unique.loc[not_matching_all]
    az_mismatches_all=az_mismatches_all.drop_duplicates()
    az_mismatches_all.reset_index(drop=True, inplace=True)
    
    # retrun Perfect matches and azimuth mismatches
    return perfect_matches_all,az_mismatches_all

# Check whether the ASCTB CT LABEL (label_asctb) is present in Azimuth. az_all_cts_label_unique is a dataframe that contains
# unique CT/LABEL, Label and author label for a reference organ.

# i and j are the index(row number) pointing to corresponding row in ASCT+B and Azimuth dataframe respectively. 
# i is the row number of label_asctb in Azimuth dataframe.
# j points to the row number in azimuth where label_asctb matches in Azimuth.
# az_row_all,asctb_row_all are global lists used to store these the row number of Azimuth, ASCT+B 

# not_matching_all is a list storing index of Asctb CT(label_asctb) that does not match to any CT in Azimuth. 
# And if there is a match then we append Asctb row to the list asctb_row_all and corresponding Azimuth row number 
# to az_row_all
def check_in_az(label_asctb,i,az_all_cts_label_unique,az_row,asctb_row,not_matching):    
    flag=0
    cellLabel1 = re.sub(r"[^a-zA-Z0-9 ]","",label_asctb) #removed add special character from label_asctb
    for j in range(len(az_all_cts_label_unique['CT/LABEL'])):
        rs= re.sub(r"[^a-zA-Z0-9 ]","",az_all_cts_label_unique['CT/LABEL'][j]) #removed special character from azimuth label
        if label_asctb.strip().lower().replace(" ", "") == az_all_cts_label_unique['CT/LABEL'][j].strip().lower().replace(" ", ""):
            az_row.append(j) # direct matching label_asctb with azimuth label by removing spaces and converting it into lower cases
            asctb_row.append(i)
            flag=1
            break
        elif label_asctb.strip().lower().replace(" ", "") == az_all_cts_label_unique['CT/LABEL'][j][:-1].strip().lower().replace(" ", ""):
            az_row.append(j) #direct matching label_asctb with azimuth label with removing last element in case 's' in azimuth label is the last element like Label: "Cell's'"
            asctb_row.append(i)
            flag=1
            break
        elif label_asctb[:-1].strip().lower().replace(" ", "") == az_all_cts_label_unique['CT/LABEL'][j].strip().lower().replace(" ", ""):
            az_row.append(j) #direct matching label_asctb with azimuth label with removing last element in case 's' in label_asctb is the last element like Label: "Cell's'"
            asctb_row.append(i)
            flag=1
            break
        elif cellLabel1.strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
            az_row.append(j) # direct matching cleaned label_asctb with  cleaned azimuth label by removing spaces and converting it into lower cases
            asctb_row.append(i)
            flag=1
            break
        elif cellLabel1.strip().lower().replace(" ", "") == rs[:-1].strip().lower().replace(" ", ""):
            az_row.append(j) #direct matching cleaned label_asctb with cleaned azimuth label with removing last element in case 's' in azimuth label is the last element like Label: "Cell's'"
            asctb_row.append(i)
            flag=1
            break
        elif cellLabel1[:-1].strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
            az_row.append(j) #direct matching cleaned label_asctb with cleaned azimuth label with removing last element in case 's' in label_asctb is the last element like Label: "Cell's'"
            asctb_row.append(i)
            flag=1
            break

    if flag==0:
        not_matching.append(i)

# Check for mismatches between ASCT+B and Azimuth tables and return Asctb CT mismatches
def perfect_match_for_asctbct_in_azimuth(azimuth_all_cts_label_unique,asctb_kidney_all_cts_label_unique):
    az_row=[]
    asctb_row=[]
    not_matching=[]

    for i in range(len(asctb_kidney_all_cts_label_unique['CT/LABEL'])):
        if asctb_all_cts_label_unique['CT/LABEL'][i]!="":
            check_in_az(asctb_kidney_all_cts_label_unique['CT/LABEL'][i],i,azimuth_all_cts_label_unique,az_row,asctb_row,not_matching)
        else:
            not_matching.append(i)

    az_matches=azimuth_all_cts_label_unique.loc[az_row]
    asctb_matches=asctb_kidney_all_cts_label_unique.loc[asctb_row]

    az_matches.reset_index(drop=True,inplace=True)
    asctb_matches.reset_index(drop=True,inplace=True)

    az_matches.rename(columns = {"CT/LABEL":"AZ.CT/LABEL","CT/LABEL.Author":"AZ.CT/LABEL.Author"},inplace = True)
    asctb_matches.rename(columns = {"CT/LABEL":"ASCTB.CT/LABEL","CT/LABEL.Author":"ASCTB.CT/LABEL.Author"},inplace = True)

    perfect_matches=pd.concat([asctb_matches,az_matches],axis=1)

    asctb_mismatches=asctb_kidney_all_cts_label_unique.loc[not_matching]
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
    asctb_perfect_matches,asctb_mismatches=perfect_match_for_asctbct_in_azimuth(azimuth_all_cts_label_unique,asctb_all_cts_label_unique)
#print(azimuth_all_cts_label_unique)  
#print(asctb_all_cts_label_unique)
print("\n")
print(azimuth_perfect_matches)
print("\n")
print(asctb_perfect_matches)


