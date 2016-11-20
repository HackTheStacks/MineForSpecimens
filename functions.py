import os
import sys
import json
import csv
import pandas as pd
import requests
import path
import signal
from cStringIO import StringIO

#must install pdfminer separately (pip install is recommended)
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

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
    url = 'https://digitallibrary.amnh.org/rest/items/'+str(itemId)+'?expand=metadata'
    response = requests.get(url,verify=False)

    parseData = json.loads(response.text)

    listOfUniqueKeys = ['dc.date.issued','dc.date.available','dc.date.issued','dc.identifier.uri','dc.description','dc.description.abstract',
 'dc.language.iso','dc.publisher','dc.relation.ispartofseries']

    itemAuthors           = ""
    itemSubjects          = ""
    itemTitle             = ""
    itemTitleAlternatives = ""
    
    parsedTitle = ""
    parsedNum   = ""

    uniqueDict = {}

    regex=r"(.+\.?).+\(?[A|a]merican [M|m]useum [N|n]ov.+no\. ?(\d+)"

    for item in parseData['metadata']:
        if item['key'] in ['dc.contributor.author']:
            if itemAuthors == "":
                itemAuthors = item['value']
            else:
                itemAuthors = itemAuthors + "|" + item['value']
        elif item['key'] in ['dc.subject']:
            if itemSubjects == "":
                itemSubjects = item['value']
            else:
                itemSubjects = itemSubjects + "|" + item['value']
        elif item['key'] in ['dc.title.alternative']:
            if itemTitleAlternatives == "":
                itemTitleAlternatives = item['value']
            else:
                itemTitleAlternatives = itemTitleAlternatives + "|" + item['value']
        elif item['key'] in ['dc.title']:
            fullName = item['value']
            parsed = re.search(regex, fullName)
            if parsed:
                parsedTitle = parsed.group(1)
                parsedNum   = parsed.group(2)
            else:
                parsedTitle = fullName
                parsedNum   = ""

        elif item['key'] in listOfUniqueKeys:
            uniqueDict = {item['key']:item['value']}

        dic = {'authors':itemAuthors,
           'subjects':itemSubjects,
           'title.alternatives':itemTitleAlternatives,
           'title':parsedTitle,
           'Num':parsedNum}
    
    if bool(uniqueDict):
        dic.update(uniqueDict)
   
    #We have yet to implement this function
    #'species':findSpecieInPDF(file.pdf)    
      
    return dic

def signal_handler(signum, frame):
    raise Exception("Timed Out")

def convert_pdf_to_txt(itemId):
    '''This function takes a handle id for a single pdf file, 
    extracts the pdf, and converts it to text in memory
    '''
    os.system('wget --no-check-certificate https://digitallibrary.amnh.org/rest/bitstreams/'+str(itemId)+'/retrieve -O ' + str(itemId) + '.pdf')

    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = file(str(itemId) + '.pdf', 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        
        signal.signal(signal.SIGALRM,signal_handler)
        signal.alarm(20)
        try:
            interpreter.process_page(page)
        except Exception,msg:
            pass


    text = retstr.getvalue()

    #Cleaning
    fp.close()
    device.close()
    retstr.close()
    os.system('rm '+ str(itemId) + '.pdf')

    return text


def createCSVfile():
    #create a list of id for ALL the items in collection 4 Novitates
    listOfIds = createListOfIds()
    
    #create and empty list
    listOfYears = []
    
    #loop trhough the ids of collection 4 and retrieve the published dates
    [getItemYear(i,listOfYears) for i in listOfIds]
    
    #convert the dates into a series with the item id as index and save it
    serie = pd.Series(listOfYears)
    serie.index = listOfIds
    serie.to_csv('datesOfItems.csv')
