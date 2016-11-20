import re
import json
import csv

SPECIMAN_REGEX='AMNH [A-Z]-[0-9]+|AMNH[ |-][0-9]+'

def find_specimans(article):
    """Returns a sorted, distinct list of AMNH specimans (as defined by 
    SPECIMAN_REGEX) contained in the file."""
    p = re.compile(SPECIMAN_REGEX)
    sp_list = list(set(p.findall(article)))
    sp_list.sort()
    return sp_list

def find_specimans_file(file_name):
    """Takes as input a text file with name file_name and returns a sorted, 
    distinct list of AMNH specimans (as defined by SPECIMAN_REGEX) contained
    in the file."""
    text = open(file_name)
    article = text.read()
    return find_specimans(article)
    
def lookup_speciman_names(sp_list):
    """Tales a list of AMNH specimans as input and produces a list of 
    speciman number and name pairs as output"""
    sp_numbers_names = []
    for s in sp_list:
        psn = re.split(' |-', s[5:])
        if len(psn) == 1:
            sp_name = collection[('', psn[0])]
        else: 
            sp_name = collection[(psn[0], psn[1])]
        sp_numbers_names.append((s, sp_name))
    return sp_numbers_names

def json_specimans(file_name):
    """Calls find_specimans() with the file_name, jsonify and pretty prints 
    the results"""
    sp_list = find_specimans_file(file_name)
    specimans = {}
    specimans["file"] = file_name
    specimans["speciman_count"] = len(sp_list)
    specimans["speciman_list"] = sp_list
    specimans["speciman_list_with_names"] = lookup_speciman_names(sp_list)
    return json.dumps(specimans, indent=4, sort_keys=True)
    
collection = {}    
def load_collections():
    with open('CatalogNos/herp.txt', 'rb') as csvfile:
        collection_reader = csv.reader(csvfile)
        collection_reader.next()    # ignore header
        for row in collection_reader:
            if (row[0], row[1]) in collection:
                collection[(row[0],row[1])].append(row[2:])
            else:
                collection[(row[0],row[1])] = [row[2:]]
    with open('CatalogNos/bird.txt', 'rb') as csvfile:
        collection_reader = csv.reader(csvfile)
        collection_reader.next()    # ignore header
        for row in collection_reader:
            if ('', row[1]) in collection: 
                collection[('',row[1])].append(row[3:])
            else:    
                collection[('',row[1])] = [row[3:]]
    
load_collections() 
print json_specimans('N3849.txt')
print find_specimans('AMNH Collection AMNH 113352')
