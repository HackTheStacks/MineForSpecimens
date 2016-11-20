import os
import sys
import json
import csv
import pandas as pd
import requests

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib

# Return array of all valid item IDs

def createListOfIds():
    response = requests.get('https://digitallibrary.amnh.org/rest/collections/4?expand=items&limit=10000',verify=False)
    json_data = json.loads(response.text)

    itemIdList=[]

    for item in json_data['items']:
        itemId = item.get("id")
        itemIdList.append(itemId)

    return itemIdList


def getItemYear(id,yearList):
    
    '''
    This function takes an id of the item in Dspace
    and a list where all the output will be stored
    '''
        
    response = requests.get('https://digitallibrary.amnh.org/rest/items/' + str(id) + '?expand=metadata',verify=False)
    json_data = json.loads(response.text)
    
    try:
        for item in json_data['metadata']:
            #looks for the element of the list that has de date.issued
            if item['key'] == 'dc.date.issued':
                output = item['value']
                break
            else:
                continue
                        
    except ValueError:
        output = 0

    return yearList.append(output)

def datetimeCoerce(x):
    '''This function takes a date string as produced
    by getItemYear() and changes it to a date. 
    ERRORS ARE COERCED (dates like [1984?a])'''
    return pd.to_datetime(x,errors = 'coerce')

def getYear(x):
    '''This function takes a datetime and
    returns the year'''
    return x.year

'''
Keeping this in here for now in case we need to change the new function

def createListOfIds():
    
#    This function creates a Pandas Series of ALL the ids from 
#    ALL the collections and saves it in a csv
    
    years =[]
    #6768 is the current number, we should come up with a way to
    #get it from the full item list
    [getItemYear(id = i,yearList=years) for i in reversed(range(6768))]
    datesOfItems = pd.Series(years)
    #change the index so they reflect the id of the item
    datesOfItems.index = reversed(range(6768))
    datesOfItems.to_csv('datesOfItems.csv')
'''

def getIdsFromPeriod(year):
    '''This function takes a year, 
    reads the csv returned from createListOfIds()
    and returns the ids of the items for that year in a list'''
    #read the csv returned from createListOfIds()
    idsFromPeriod = pd.Series.from_csv('datesOfItems.csv')
    #parse the dates and COERCE the errors
    idsFromPeriod = idsFromPeriod.apply(datetimeCoerce)
    #create a mask of ids whose year is equal to year
    mask = idsFromPeriod.apply(getYear)==year
    return list(idsFromPeriod[mask].index)


def getMetadata(itemId):
    '''This function takes an items's id
    and returns the metadata in a python dic
    '''
    url = 'https://digitallibrary.amnh.org/rest/items/'+str(itemId)+'/metadata'
    result = os.popen('curl -ki -H "Accept: application/json" -H "Content-Type: application/json" \-X GET ' + url).read()
    parseData = json.loads(result[199:])
    dic = {'authors':[parseData[i]['value'] for i in range(len(parseData)) if parseData[i]['key'] in ['dc.contributor.author']],
        'subjects':[parseData[i]['value'] for i in range(len(parseData)) if parseData[i]['key'] in ['dc.subject']],
        'title.alternatives':[parseData[i]['value'] for i in range(len(parseData)) if parseData[i]['key'] in ['dc.title.alternative']]
           }
    listOfUniqueKeys = ['dc.date.issued','dc.date.available','dc.date.issued','dc.identifier.uri','dc.description','dc.description.abstract',
 'dc.language.iso','dc.publisher','dc.relation.ispartofseries','dc.title']
    dic2 = dict([(parseData[i]['key'],parseData[i]['value']) for i in range(len(parseData)) if parseData[i]['key'] in listOfUniqueKeys])
    dic.update(dic2)
    
    #We have yet to implement this function
    #'species':findSpecieInPDF(file.pdf)    
      
    return dic
