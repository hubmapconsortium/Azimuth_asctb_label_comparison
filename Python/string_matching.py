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
"""print(qres) #checking query returned object
import pandas as pd
b = pd.DataFrame(qres, columns= qres.vars) #converting it into dataframe
c=0"""
import re
cellLabel = 'brush cell of epithelium of trachea'
cellLabel1 = re.sub(r"[^a-zA-Z0-9 ]","",cellLabel) #removing spaces and special characters
c=0
for row in qres:
    rs= re.sub(r"[^a-zA-Z0-9 ]","",row.cell_label)
    rsy = re.sub(r"[^a-zA-Z0-9 ]","",row.synonym)
    if cellLabel.strip().lower().replace(" ", "") == row.cell_label.strip().lower().replace(" ", ""):
        #print(row[1])
        print(row.parent_label) #direct matching and returning parents
        c+=1
    elif cellLabel.strip().lower().replace(" ", "") == row.cell_label[:-1].strip().lower().replace(" ", ""):
        print(row.parent_label)
        c+=1
    elif cellLabel[:-1].strip().lower().replace(" ", "") == row.cell_label.strip().lower().replace(" ", ""):
        print(row.parent_label)
        c+=1
    elif cellLabel1.strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
        #print(row[1])
        print(row.parent_label)
        c+=1
    elif cellLabel1.strip().lower().replace(" ", "") == rs[:-1].strip().lower().replace(" ", ""):
        print(row.parent_label)
        c+=1
    elif cellLabel1[:-1].strip().lower().replace(" ", "") == rs.strip().lower().replace(" ", ""):
        print(row.parent_label)
        c+=1
    elif cellLabel.strip().lower().replace(" ", "") == row.synonym.strip().lower().replace(" ", ""): #direct matching with synonyms
        #print(row[1])
        print(row.parent_label)
        c+=1
    elif cellLabel.strip().lower().replace(" ", "") == row.synonym[:-1].strip().lower().replace(" ", ""):
        print(row.parent_label)
        c+=1
    elif cellLabel[:-1].strip().lower().replace(" ", "") == row.synonym.strip().lower().replace(" ", ""):
        print(row.parent_label)
        c+=1
print(c)