import re
import json
import csv

SPECIMAN_REGEX='AMNH [A-Z]-[0-9]+|AMNH[ |-][0-9]+'

def find_specimans(file_name):
    """Takes as input a text file with name file_name and returns a sorted, 
    distinct list of AMNH specimans (as defined by SPECIMAN_REGEX) contained
    in the file."""
    text = open(file_name)
    article = text.read()
    p = re.compile(SPECIMAN_REGEX)
    sp_list = list(set(p.findall(article)))
    sp_list.sort()
    return sp_list

def pprint_specimans(file_name):
    """Calls find_specimans() with the file_name, jsonify and pretty prints 
    the results"""
    sp_list = find_specimans(file_name)
    specimans = {}
    specimans["File"] = file_name
    specimans["Speciman Count"] = len(sp_list)
    specimans["Speciman(s)"] = sp_list
    print json.dumps(specimans, indent=4, sort_keys=True)
    
    
collection = {}    
def load_collections():
    with open('CatalogNos/herp.txt', 'rb') as csvfile:
        collection_reader = csv.reader(csvfile)
        collection_reader.next()    # ignore header
        for row in collection_reader:
            collection[(row[0],row[1])] = row[2:]
    with open('CatalogNos/bird.txt', 'rb') as csvfile:
        collection_reader = csv.reader(csvfile)
        collection_reader.next()    # ignore header
        for row in collection_reader:
            collection[('',row[1])] = row[3:]
    
    
pprint_specimans('N3849.txt')
load_collections()
print collection[('A','10329')]
print collection[('', '674957')]