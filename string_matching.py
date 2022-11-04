import requests
import simplejson as json
import pandas as pd
import numpy as np
import os
import json
import math
from openpyxl import load_workbook
notebook_path = os.path.abspath("string_matching.py")
uber = os.path.join(os.path.dirname(notebook_path), "uber2.csv")
ubergraph_response_df = pd.read_csv(uber, encoding = "ISO-8859-1", header =0)
import re
cellLabel = 'MC(T)'
cellLabel1 = re.sub(r"[^a-zA-Z0-9 ]","",cellLabel) #removing spaces and special characters
c=0
for row in ubergraph_response_df.iterrows():
    rs= re.sub(r"[^a-zA-Z0-9 ]","",row[1][1])
    rsy = re.sub(r"[^a-zA-Z0-9 ]","",row[1][6])
    if cellLabel.strip().lower().replace(" ", "") == row[1][1].strip().lower().replace(" ", ""):
        #print(row[1])
        print(row[1][5]) #direct matching and returning parents
        c+=1
    elif cellLabel.strip().lower().replace(" ", "") == row[1][1][:-1].strip().lower().replace(" ", ""):
        print(row[1][5])
        c+=1
    elif cellLabel[:-1].strip().lower().replace(" ", "") == row[1][1].strip().lower().replace(" ", ""):
        print(row[1][5])
        c+=1
    elif cellLabel1.strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
        #print(row[1])
        print(row[1][5])
        c+=1
    elif cellLabel1.strip().lower().replace(" ", "") == rs[:-1].strip().lower().replace(" ", ""):
        print(row[1][5])
        c+=1
    elif cellLabel1[:-1].strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
        print(row[1][5])
        c+=1
    elif cellLabel.strip().lower().replace(" ", "") == row[1][6].strip().lower().replace(" ", ""): #direct matching with synonyms
        #print(row[1])
        print(row[1][5])
        c+=1
    elif cellLabel.strip().lower().replace(" ", "") == row[1][6][:-1].strip().lower().replace(" ", ""):
        print(row[1][5])
        c+=1
    elif cellLabel[:-1].strip().lower().replace(" ", "") == row[1][6].strip().lower().replace(" ", ""):
        print(row[1][5])
        c+=1
print(c)