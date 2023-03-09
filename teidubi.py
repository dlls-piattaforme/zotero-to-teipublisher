import xml.etree.cElementTree as ET
from xml.etree import ElementTree
from xml.etree.ElementTree import Element  
from xml.dom import minidom
import html
import re
import datetime


current_date = datetime.datetime.now().strftime("%Y-%m-%d")

def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def getItem(itemID, allItems):
    result = [item['data'] for item in allItems if item['data']['key'] == itemID ]
    if not result:
        return ''
    else:
        return result[0]

def getBibCitation(item, groupID):
    
    zoteroUrl = 'http://zotero.org/groups/'+groupID+'/items/'
    category = ''
    bibl = ET.Element("bibl", type=item['itemType'], corresp=item['key']+'.xml')
    
    if item.get('title'): 
        ET.SubElement(bibl, "title").text = item.get('title')

    if item.get('creators'):
        
        seltype= { 'author': 'author', 'editor' : 'editor', 'seriesEditor':'editor', 'bookAuthor': 'author', 'reviewedAuthor': 'author' }

        for creator in item['creators']:
            if creator['creatorType'] in seltype:
                authoreditor = ET.SubElement(bibl, seltype[creator['creatorType']])
                name = ''
                
                if creator.get('firstName'):
                    name = creator['firstName']
                if creator.get('lastName'):
                    name = name+' '+creator['lastName']
                
                name = ET.SubElement(authoreditor, "name").text = name
            
    if item.get('place'):
        ET.SubElement(bibl, "pubPlace").text = item['place']

    if item.get('publisher'):
        ET.SubElement(bibl, "publisher").text = item['publisher']

    if item.get('date'):
        ET.SubElement(bibl, "date").text = item['date']
        
    if item.get('tags'):
        tags = ET.SubElement(bibl, "note", type="tags")
        for tag in item['tags']:
                category = tag['tag']
                ET.SubElement(tags, "note", type='category').text = tag['tag']
    
    ET.SubElement(bibl, "note", type='citation').text = "["+category+"] "+item.get('title')
    
    
    return bibl

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

    zoteroUrl = 'http://zotero.org/groups/'+groupID+'/items/'
    
    #isAnalytic = item['itemType'] in analyticItemTypes
    
    #verifica se esiste l'uri      
    bibl = ET.SubElement(body, "biblStruct", type=item['itemType'], corresp=zoteroUrl+item['key'])

########################################## MONOGR ############################################   
    monogr = ET.SubElement(bibl, "monogr")
        
    if item.get('title'):
        ET.SubElement(monogr, "title", level="m").text = item['title'] #level m (attributo che rende cliccabile i titoli su TEI Publisher)
        titleStmtTitle.text = item['title']

    if item.get('shortTitle'):
        ET.SubElement(monogr, "title", type='short').text = item['shortTitle']	
    
    publicationTitle = item.get('bookTitle') or item.get('proceedingsTitle') or item.get('encyclopediaTitle') or item.get('dictionaryTitle') or item.get('publicationTitle') or item.get('websiteTitle')
    if not ( publicationTitle is None ):
        ET.SubElement(monogr, "title", type="publication").text = publicationTitle
    
    if item.get('DOI'):
        ET.SubElement(monogr, "idno", type='DOI').text = item['DOI']


    if item.get('conferenceName'):
        #replaceFormatting
        ET.SubElement(monogr, "title", type='conferenceName').text = item['conferenceName']
    
     #itemTypes in Database do unfortunately not match fields
     #of item
    if item.get('series') or item.get('seriesTitle'):
        series = ET.SubElement(bibl, "series")

        if item.get('series'):
            #replaceFormatting
            ET.SubElement(series, "title", level='s').text = item['series'] #level='s' (qui e sotto), per le immagini openseadragon

        if item.get('seriesTitle'):
            #replaceFormatting
            ET.SubElement(series, "title", type='alternative', level='s').text = item['seriesTitle']

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

        if creator.get('firstName'):
            curCreator.text = creator['firstName']
        
        if creator.get('lastName'):
            if creator.get('firstName'):
                curCreator.text = creator['firstName']+" "+creator['lastName']
            else:
                curCreator.text = creator['lastName']
        
        if creator.get('name'):
            curCreator.text = creator['name']

        monogr.append(curCreator)
  

    if item.get('edition'):
        ET.SubElement(monogr, "edition").text = item['edition']
# 	// software
    elif item.get('versionNumber'):
        ET.SubElement(monogr, "edition").text = item['versionNumber']

# 	// create the imprint
    imprint = ET.SubElement(monogr, "imprint")


    if item.get('place'):
        ET.SubElement(imprint, "pubPlace").text = item['place']

    if item.get('numPages'):
        ET.SubElement(imprint, "biblScope", unit='numPages' ).text = item['numPages']

    if item.get('language'):
        ET.SubElement(imprint, "biblScope", unit='language' ).text = item['language']

    if item.get('archive'):
        ET.SubElement(imprint, "biblScope", unit='archive' ).text = item['archive']
    
    if item.get('archiveLocation'):
        #EDIT: divide archiveLocation e archiveLibrary attraverso il separatore ': '
        archiveData = item['archiveLocation'].split(': ', 1)
        if len(archiveData) > 1:
            archiveLibrary = archiveData[0]
            archiveLocation = archiveData[1]

            ET.SubElement(imprint, "biblScope", unit='archiveLibrary' ).text = archiveLibrary
            ET.SubElement(imprint, "biblScope", unit='archiveLocation' ).text = archiveLocation
        else:
            ET.SubElement(imprint, "biblScope", unit='archiveLocation' ).text = item['archiveLocation']
    
    if item.get('libraryCatalog'):
        ET.SubElement(imprint, "biblScope", unit='libraryCatalog' ).text = item['libraryCatalog']
    
    if item.get('rights'):
        ET.SubElement(imprint, "biblScope", unit='rights' ).text = item['rights']
        #print(f"RIGHTS: {ET.SubElement(imprint, 'biblScope', unit='rights').text}") #EDIT
        #print(item['rights'])
    
    if item.get('publisher'):
        ET.SubElement(imprint, "publisher").text = item['publisher']

    if item.get('date'):
        ET.SubElement(imprint, "date").text = item['date']

    if item.get('accessDate'):
        ET.SubElement(imprint, "note",type="accessed").text = item['accessDate']

    if item.get('url'):
        ET.SubElement(imprint, "note", type="url").text = item['url']

    if item.get('thesisType'):
        ET.SubElement(imprint, "note", type="thesisType").text = item['thesisType']

    if item.get('relations').get('dc:relation'):
        #creare subito relatedItem

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
            
    
    if item.get('collections'):
        for collection in item['collections']:
            ET.SubElement(bibl, "note", type="collection").text = collection

    if item.get('extra'):
         ET.SubElement(bibl, "note", type="extra").text = item['extra']
         #print(f'EXTRA: {ET.SubElement(bibl, "note", type="extra").text}') #EDIT
         #print(item['extra'])

    if item.get('notes'):
        if isinstance(item['notes'], list):
            for note in item['notes']:
                #noteText = Zotero.Utilities.unescapeHTML(noteText);   
                noteText = striphtml(html.unescape(note['note']))
                ET.SubElement(bibl, "note").text = noteText
    if item.get('abstractNote'):
        ET.SubElement(bibl, "note", type="abstract").text = item['abstractNote']
        
    if item.get('tags'):
        tags = ET.SubElement(bibl, "note", type="tags")
        for tag in item['tags']:
                ET.SubElement(tags, "note", type='category').text = tag['tag']
    

    
    #childNodes[0] for remove first line <?xml version="1.0" ?>
    xmlstr = minidom.parseString(ET.tostring(tei, 'utf-8' )).toprettyxml(indent="   ")
    return xmlstr



