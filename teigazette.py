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

def generateItem(item, groupID):
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
    
    #verifica se esiste l'uri      
    bibl = ET.SubElement(body, "biblStruct", type=item['itemType'], corresp=zoteroUrl+item['key'])

########################################## MONOGR ############################################   
    monogr = ET.SubElement(bibl, "monogr")
        
    if item.get('title'):
        ET.SubElement(monogr, "title", level="m").text = item['title']
        titleStmtTitle.text = item['title']

    if item.get('shortTitle'):
        ET.SubElement(monogr, "title", type='short').text = item['shortTitle']
    
    if item.get('series'):
        ET.SubElement(monogr, "series").text = item['series']

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
                curCreator.text = creator['firstName'] + " " + creator['lastName']
            else:
                curCreator.text = creator['lastName']
        
        if creator.get('name'):
            curCreator.text = creator['name']

        monogr.append(curCreator)
  
    if item.get('seriesText'): #relatore/tutor per tesi triennali 
        ET.SubElement(monogr, "note", type='tutor').text = item['seriesText']

# 	// create the imprint
    imprint = ET.SubElement(monogr, "imprint")

    if item.get('place'):
        ET.SubElement(imprint, "pubPlace").text = item['place']

    if item.get('volume'):
        ET.SubElement(imprint, "biblScope", unit='volume' ).text = item['volume']

    if item.get('issue'): #aggiunto Gazette
        ET.SubElement(imprint, "biblScope", unit='issue' ).text = item['issue']

    if item.get('pages'): #corretto
        ET.SubElement(imprint, "biblScope", unit='pages' ).text = item['pages']

    if item.get('language'):
        ET.SubElement(imprint, "biblScope", unit='language' ).text = item['language']

    if item.get('date'):
        ET.SubElement(imprint, "date").text = item['date']

    if item.get('extra'):
         ET.SubElement(bibl, "note", type="extra").text = item['extra']

    if item.get('notes'):
        if isinstance(item['notes'], list):
            for note in item['notes']:
                #noteText = Zotero.Utilities.unescapeHTML(noteText);   
                noteText = striphtml(html.unescape(note['note']))
                ET.SubElement(bibl, "note").text = noteText
    if item.get('abstractNote'):
        ET.SubElement(bibl, "note", type="abstract").text = item['abstractNote']
    
    #childNodes[0] for remove first line <?xml version="1.0" ?>
    xmlstr = minidom.parseString(ET.tostring(tei, 'utf-8' )).toprettyxml(indent="   ")
    return xmlstr