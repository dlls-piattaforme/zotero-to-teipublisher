from cgitb import text
from multiprocessing.dummy import current_process
from unicodedata import category
import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.etree.ElementTree import Element  
from xml.dom import minidom
import html
import re
import datetime


current_date = datetime.datetime.now().strftime("%Y-%m-%d")

#Funzione che rimuove le taggature html dalla stringa
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

#Funzione che restituisce l'item cercata nell'array totale
def getItem(itemID, allItems):
    result = [item['data'] for item in allItems if item['data']['key'] == itemID ]
    if not result:
        return ''
    else:
        return result[0]

#Funzione per la creazione dei data range per il filtro di tei-publisher 
def dateRange(d):
    
    if '-' in str(d):
        d = str(d).split('-')[-1]
    elif  not d.isdecimal():
        return  str(d)
    
    bibYear = int(d)
    if bibYear <= 1499:
        return "1400-"+str(bibYear)
    elif bibYear >= 1500 and bibYear <= 1599:
        return "1500-"+str(bibYear)
    elif bibYear >= 1600 and bibYear <= 1699:
        return "1600-"+str(bibYear)
    elif bibYear >= 1700 and bibYear <= 1799:
        return "1700-"+str(bibYear)
    elif bibYear >= 1800 and bibYear <= 1899:
        return "1800-"+str(bibYear)
    elif bibYear >= 1900 and bibYear <= 1999:
        return "1900-"+str(bibYear)
    elif bibYear >= 2000:
        return "2000-"+str(bibYear)
    else:
        return str(d)

# Funzione che restituisce il blocco di xml dell'item in relazione 
def getBibCitation(item, groupID):
    
    
    zoteroUrl = 'http://zotero.org/groups/'+groupID+'/items/'

    bibl = ET.Element("bibl", type=item['itemType'], corresp=zoteroUrl+item['key'])
    
    if item.get('title'): 
        ET.SubElement(bibl, "title").text = item.get('title')

    if item.get('creators'):
        for creator in item['creators']:
            name = ''
            if creator.get('firstName'):
                name = creator['firstName']
            if creator.get('lastName'):
                name = name+' '+creator['lastName']
            
            if creator['creatorType'] == 'editor' or creator['creatorType'] == 'seriesEditor':
                ET.SubElement(bibl, 'editor').text = name
            else:
                ET.SubElement(bibl, 'author', role=creator['creatorType']).text = name

    if item.get('place'):
        ET.SubElement(bibl, "pubPlace").text = item['place']
    if item.get('publisher'):
        ET.SubElement(bibl, "publisher").text = item['publisher']
    if item.get('date'):
        ET.SubElement(bibl, "date").text = item['date']
    
    if item.get('collections'):
        for collection in item['collections']:
            ET.SubElement(bibl, "note", type="collection").text = collection
            
    if item.get('bibcit'):
        r = re.compile(r"(https?://[^ ]+)")
        noteCit = ET.SubElement(bibl, "note", type="citation", corresp=item['key']+'.xml')
        noteCit.text = str( r.sub(r'', item['bibcit']) )
        
        risSrc = r.search(item['bibcit'])
        if risSrc:
            ET.SubElement(noteCit, "ref", target = risSrc.group(1) )
            
    return bibl
    
def cleanString(s):
    return (s.strip()).lower()

#Funzione principale che restituisce il documento xml dell'item
def generateItem(item, allItems, groupID):

    tei = ET.Element("TEI", xmlns = "http://www.tei-c.org/ns/1.0")
    teiHeader = ET.SubElement(tei, "teiHeader")
    fileDesc = ET.SubElement(teiHeader, "fileDesc")
    titleStmt = ET.SubElement(fileDesc, "titleStmt")
    titleStmtTitle = ET.SubElement(titleStmt, "title")
    publicationStmt = ET.SubElement(fileDesc, "publicationStmt")
    ET.SubElement(publicationStmt, "p").text = "export - "+str(current_date)
    sourceDesc = ET.SubElement(fileDesc, "sourceDesc")
    ET.SubElement(sourceDesc, "p").text = "Exported from Zotero database"
    texttag = ET.SubElement(tei, "text")
    body = ET.SubElement(texttag, "body")

    #analyticItemTypes = { 
    #'journalArticle': True,
    #'bookSection': True,
    #'magazineArticle': True,
    #'newspaperArticle': True,
    #'conferencePaper': True,
    #'encyclopediaArticle': True,
    #'dictionaryEntry': True,
    #'webpage': True
    #} 
    
    #Tutte le subcollections
    categoryList = ["article in miscellaneous work","article in proceedings","article in reference work","bibliography","digital projects & collections","edition","edition/translation","facsimile","journal article","manuscript studies","miscellaneous work","monograph","proceedings","reference work","review","thesis/dissertation","translation"]
    zoteroUrl = 'http://zotero.org/groups/'+groupID+'/items/'
    
    #isAnalytic = item['itemType'] in analyticItemTypes
    
    #verifica se esiste l'uri      
    bibl = ET.SubElement(body, "biblStruct", type=item['itemType'], corresp=zoteroUrl+item['key']) #corresp dovrebbe essere uri

########################################## MONOGR ############################################   
    monogr = ET.SubElement(bibl, "monogr")
        
    if item.get('title'):
        ET.SubElement(monogr, "title").text = item['title']
        titleStmtTitle.text = item['title']

    if item.get('shortTitle'):
        ET.SubElement(monogr, "title", type='short').text = item['shortTitle']	
    
    publicationTitle = item.get('bookTitle') or item.get('proceedingsTitle') or item.get('encyclopediaTitle') or item.get('dictionaryTitle') or item.get('publicationTitle') or item.get('websiteTitle')
    if not ( publicationTitle is None ):
        ET.SubElement(monogr, "title", type="publication").text = publicationTitle
    
    if item.get('DOI'):
        ET.SubElement(monogr, "idno", type='DOI').text = item['DOI']

    #  add name of conference
    if item.get('conferenceName'):
        #replaceFormatting
        ET.SubElement(monogr, "title", type='conferenceName').text = item['conferenceName']
    
     #itemTypes in Database do unfortunately not match fields
     #of item
    if item.get('series') or item.get('seriesTitle'):
        series = ET.SubElement(bibl, "series")

        if item.get('series'):
            #replaceFormatting
            ET.SubElement(series, "title").text = item['series']

        if item.get('seriesTitle'):
            #replaceFormatting
            ET.SubElement(series, "title", type='alternative').text = item['seriesTitle']

        if item.get('seriesText'):
            ET.SubElement(series, "note", type='description').text = item['seriesText']

        if item.get('seriesNumber'):
            ET.SubElement(series, "biblScope", unit='volume').text = item['seriesNumber']
        
        #Other canonical ref nos come right after the title(s) in monogr.

    if item.get('ISBN'):
        ET.SubElement(monogr, "idno", type='ISBN').text = item['ISBN']
    
    if item.get('ISSN'):
        ET.SubElement(monogr, "idno", type='ISSN').text = item['ISSN']
    
    if item.get('callNumber'):
        ET.SubElement(monogr, "idno", type='callNumber').text = item['callNumber']

    #multivolume works
    if item.get('numberOfVolumes'):
        ET.SubElement(monogr, "extent").text = item['numberOfVolumes']	

    #creators are all people only remotely involved into the creation of a resource
    for creator in item['creators']:
        curCreator = ''
        
        if creator['creatorType'] == 'editor' or creator['creatorType'] == 'seriesEditor':
            curCreator = Element('editor')
        else:
            curCreator = Element('author', role=creator['creatorType'])
            

        #add the names of a particular creator
        if creator.get('firstName'):
            #ET.SubElement(curCreator, "forename").text = creator['firstName']
            curCreator.text = creator['firstName']
        
        if creator.get('lastName'):
            if creator.get('firstName'):
                #ET.SubElement(curCreator, "surname").text = creator['lastName']
                curCreator.text = creator['firstName']+" "+creator['lastName']
            else:
                curCreator.text = creator['lastName']
        
        if creator.get('name'):
            curCreator.text = creator['name']

        monogr.append(curCreator)

    if item.get('edition'):
        ET.SubElement(monogr, "edition").text = item['edition']

    elif item.get('versionNumber'):
        ET.SubElement(monogr, "edition").text = item['versionNumber']

####################################### IMPRINT #########################################
    imprint = ET.SubElement(monogr, "imprint")
    if item.get('place'):
        ET.SubElement(imprint, "pubPlace").text = item['place']
    if item.get('university'):
        ET.SubElement(imprint, "biblScope", unit='university').text = item['university']
    if item.get('volume'):
        ET.SubElement(imprint, "biblScope", unit='volume' ).text = item['volume']
    if item.get('language'):
        ET.SubElement(imprint, "biblScope", unit='language' ).text = item['language']
    if item.get('issue'):
        ET.SubElement(imprint, "biblScope", unit='issue' ).text = item['issue']
    if item.get('section'):
        ET.SubElement(imprint, "biblScope", unit='chapter' ).text = item['section']
    if item.get('pages'):
        ET.SubElement(imprint, "biblScope", unit='pages' ).text = item['pages']
    if item.get('numPages'):
        ET.SubElement(imprint, "biblScope", unit='n.pages' ).text = item['numPages']
    if item.get('publisher'):
        ET.SubElement(imprint, "publisher").text = item['publisher']
    if item.get('date'):
        ET.SubElement(imprint, "date").text = item['date']
        ET.SubElement(imprint, "date", type="range").text = dateRange(item['date'])
    if item.get('url'):
        ET.SubElement(imprint, "note", type="url").text = item['url']
    if item.get('thesisType'):
        ET.SubElement(imprint, "note", type="thesisType").text = item['thesisType']

#######################################  RELATED ITEM #########################################
    if item.get('relations').get('dc:relation'):
     
        relatedItemTag = ET.SubElement(bibl, "relatedItem")
        lbibl = ET.SubElement(relatedItemTag, "listBibl")
        
        if isinstance(item['relations']['dc:relation'], list):
           
            for relation in item['relations']['dc:relation']:
                
                key = relation.split('/')[-1]
                relatedItem = getItem(key, allItems)
                if relatedItem:
                    bibcit = getBibCitation(relatedItem, groupID)
                    lbibl.append(bibcit)
            
        else:
            key = item['relations']['dc:relation'].split('/')[-1]
            relatedItem = getItem(key, allItems)
            if relatedItem:
                bibcit = getBibCitation(relatedItem, groupID)
                lbibl.append(bibcit)
            
#######################################  NOTE  ######################################### 
    if item.get('collections'):
        for collection in item['collections']:
            ET.SubElement(bibl, "note", type="collection").text = collection

    if item.get('notes'):
        if isinstance(item['notes'], list):
            for note in item['notes']:
                #noteText = Zotero.Utilities.unescapeHTML(noteText);   
                noteText = striphtml(html.unescape(note['note']))
                ET.SubElement(bibl, "note").text = noteText
    
    if item.get('tags'):
        tags = ET.SubElement(bibl, "note", type="tags")
        for tag in item['tags']:
                if cleanString(tag['tag']) not in categoryList:
                    ET.SubElement(tags, "note", type='tag').text = tag['tag'].capitalize()

    if item.get('abstractNote'):
        ET.SubElement(bibl, "note", type="abstract").text = striphtml(html.unescape(item['abstractNote'])) 
    
    #citazione item principale
    if item.get('bibcit'):
        r = re.compile(r"(https?://[^ ]+)")
        noteCit = ET.SubElement(bibl, "note", type="citation")
        noteCit.text = str( r.sub(r'', item['bibcit']) )
        
        risSrc = r.search(item['bibcit'])
        if risSrc:
            ET.SubElement(noteCit, "ref", target = risSrc.group(1) )

    xmlstr = minidom.parseString(ET.tostring(tei, 'utf-8' )).toprettyxml(indent="   ")
    return xmlstr



