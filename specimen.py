import re
import json
import csv

#SPECIMEN_REGEX='AMNH [A-Z]-[0-9]+-[0-9]+|AMNH[ |-][0-9]|'
SPECIMEN_REGEX='AMNH [A-Z]-[0-9]+|AMNH[ |-][0-9]+'
AMNH_REGEX='AMNH \S+'

def findall_regex_match(regex, search_str):
    p = re.compile(regex)
    sp_list = list(set(p.findall(search_str)))
    sp_list.sort()
    return sp_list
    
def find_specimens(article):
    """Returns a sorted, distinct list of AMNH specimens (as defined by 
    specimen_REGEX) contained in the file."""
    return findall_regex_match(SPECIMEN_REGEX, article)

def verify_specimen_regex(file_name):
    article = open(file_name).read()
    return findall_regex_match(AMNH_REGEX, article)

def find_specimens_file(file_name):
    """Takes as input a text file with name file_name and returns a sorted, 
    distinct list of AMNH specimens (as defined by specimen_REGEX) contained
    in the file."""
    text = open(file_name)
    article = text.read()
    return find_specimens(article)
    
def lookup_specimen_names(sp_list):
    """Tales a list of AMNH specimens as input and produces a list of 
    specimen number and name pairs as output"""
    sp_numbers_names = []
    for s in sp_list:
        psn = re.split(' |-', s[5:])
        if len(psn) == 1:
            sp_name = collection.get(('', psn[0]), None)
        else: 
            sp_name = collection.get((psn[0], psn[1]), None)
        sp_numbers_names.append((s, sp_name))
    return sp_numbers_names

def json_specimens(file_name):
    """Calls find_specimens() with the file_name, jsonify and pretty prints 
    the results"""
    sp_list = find_specimens_file(file_name)
    specimens = {}
    specimens["file"] = file_name
    specimens["specimen_count"] = len(sp_list)
    specimens["specimen_list"] = sp_list
    specimens["specimen_list_with_names"] = lookup_specimen_names(sp_list)
    return json.dumps(specimens, indent=4, sort_keys=True)
    
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

if __name__ == "__main__":
    #print  verify_specimen_regex('N3849.txt')
    print json_specimens('N3849.txt')
    #print find_specimens('AMNH Collection AMNH 113352')
