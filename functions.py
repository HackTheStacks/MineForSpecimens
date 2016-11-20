import os
import sys
import json
import csv
import pandas as pd

try:
    import urllib2 as urllib
except ImportError:
    import urllib.request as urllib


def getItemYear(id,yearList):
    '''
    This function takes an id of the item in Dspace
    and a list where all the output will be stored
    '''
    url = 'https://digitallibrary.amnh.org/rest/items/'+str(id)+'/metadata'
    result = os.popen('curl -ki -H "Accept: application/json" -H "Content-Type: application/json" \-X GET ' + url).read()
    try:
        #remove the html header
        parseData = json.loads(result[199:])
        #search though the list the key 'date.issued' and get its value
        for i in range(len(parseData)):
            #looks for the element of the list that has de date.issued
            if parseData[i]['key'] == 'dc.date.issued':
                output = parseData[i]['value']
                break
            else:
                continue
                        
    except ValueError:
        output = 0
    yearList.append(output)


def datetimeCoerce(x):
    '''This function takes a date string as produced
    by getItemYear() and changes it to a date. 
    ERRORS ARE COERCED (dates like [1984?a])'''
    return pd.to_datetime(x,errors = 'coerce')

def getYear(x):
    '''This function takes a datetime and
    returns the year'''
    return x.year

def createListOfIds():
    '''
    This function creates a Pandas Series of ALL the ids from 
    ALL the collections and saves it in a csv
    '''
    years =[]
    #6768 is the current number, we should come up with a way to
    #get it from the full item list
    [getItemYear(id = i,yearList=years) for i in reversed(range(6768))]
    datesOfItems = pd.Series(years)
    #change the index so they reflect the id of the item
    datesOfItems.index = reversed(range(6768))
    datesOfItems.to_csv('datesOfItems.csv')
    
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
