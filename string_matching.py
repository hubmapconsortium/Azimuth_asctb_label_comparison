import requests
import simplejson as json
import pandas as pd
import numpy as np
import os
import json
import math
from openpyxl import load_workbook
import rdflib
import itertools
g = rdflib.Graph()
#g.parse("https://ubergraph.apps.renci.org/sparql")
#print(len(g))

knows_query = """

PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX overlaps: <http://purl.obolibrary.org/obo/RO_0002131>
PREFIX cell: <http://purl.obolibrary.org/obo/CL_0000000>
PREFIX description: <http://www.w3.org/2000/01/rdf-schema#comment>
PREFIX definition: <http://purl.obolibrary.org/obo/IAO_0000115>
PREFIX synonym: <http://www.geneontology.org/formats/oboInOwl#hasExactSynonym>
SELECT DISTINCT ?cell ?cell_label ?cell_description ?cell_definition ?parent_cell ?parent_label ?synonym WHERE {
    SERVICE <https://ubergraph.apps.renci.org/sparql>{
    ?cell rdfs:label ?cell_label .
    ?cell rdfs:subClassOf cell: .
    ?cell rdfs:subClassOf ?parent_cell .
    ?cell description: ?cell_description .
    ?cell definition: ?cell_definition .
    ?parent_cell rdfs:subClassOf cell: .
    ?parent_cell rdfs:label ?parent_label .
    ?cell synonym: ?synonym .
}}"""
qres = g.query(knows_query)
print(qres) #checking query returned object
import pandas as pd
b = pd.DataFrame(qres, columns= qres.vars) #converting it into dataframe
c=0
import re
cellLabel = 'MC(T)'
cellLabel1 = re.sub(r"[^a-zA-Z0-9 ]","",cellLabel) #removing spaces and special characters
c=0
for row in b.iterrows():
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