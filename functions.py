import os
import sys
import json
import csv
import pandas as pd
import glob
import path
import errno
import signal


#must install pdfminer separately (pip install is recommended)
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from cStringIO import StringIO

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

def signal_handler(signum, frame):
    raise Exception("Timed Out")

def convert_pdf_to_txt(itemId):
    '''This function takes a single pdf file,
    and converts it to a .txt file
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

def findSpecieInPDF(itemId):
    '''Extract pdf given an ID, convert it to text,
    and remove the local pdf.
    '''

    #download PDF
    os.system('wget --no-check-certificate https://digitallibrary.amnh.org/rest/bitstreams/'+str(itemId)+'/retrieve -O ' + itemId + '.pdf')
    
    #extract text
    #convert_pdf_to_txt(itemId+'.pdf')
    
    #remove pdf
    #os.system('rm '+ itemId + '.pdf')
    
    #apply Bens function
    listOfSpecies = []
    
    return listOfSpecies

