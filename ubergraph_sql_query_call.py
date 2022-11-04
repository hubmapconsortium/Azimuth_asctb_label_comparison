import rdflib
g = rdflib.Graph()
g.parse("https://ubergraph.apps.renci.org/sparql")
print(len(g))

knows_query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX overlaps: <http://purl.obolibrary.org/obo/RO_0002131>
PREFIX cell: <http://purl.obolibrary.org/obo/CL_0000000>
PREFIX description: <http://www.w3.org/2000/01/rdf-schema#comment>
PREFIX definition: <http://purl.obolibrary.org/obo/IAO_0000115>
PREFIX synonym: <http://www.geneontology.org/formats/oboInOwl#hasExactSynonym>
SELECT DISTINCT ?cell ?cell_label ?cell_description ?cell_definition ?parent_cell ?parent_label ?synonym WHERE {
    ?cell rdfs:label ?cell_label .
    ?cell rdfs:subClassOf cell: .
    ?cell rdfs:subClassOf ?parent_cell .
    ?cell description: ?cell_description .
    ?cell definition: ?cell_definition .
    ?parent_cell rdfs:subClassOf cell: .
    ?parent_cell rdfs:label ?parent_label .
    ?cell synonym: ?synonym .
}"""
qres = g.query(knows_query)
print(qres) #checking query returned object
import pandas as pd
b = pd.DataFrame(qres) #converting it into dataframe
c=0
for row in b.iterrows():
    c+=1 #issue no rows are being printed
print(c)