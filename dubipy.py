from pyzotero import zotero
from teidubi import generateItem
from teidubi import getBibCitation
import time
import sys
import requests
from os import mkdir
try:
    sys.path.insert(1, '../lib')
    from libexports import is_debug_mode, get_api_data
except:
    print(' [WARNING] Custom library libexports not found in lib')

DEBUG_MODE = is_debug_mode(sys.argv)

try: mkdir('test')
except FileExistsError: pass

typeid = 'group'
if get_api_data('dubi') is not None:
    apiKey = get_api_data('dubi')[0]
    guid = get_api_data('dubi')[1]
else:
    sys.exit("Fatal: API keys not provided.")

baseurl = "https://test-01.dlls.univr.it/cantaloupe/iiif/3/dubi%2F"

def check_iiif_image(imagename):
    footerurl = ".jpg/full/92,/0/default.jpg"
    try:
        r = requests.head(baseurl+imagename+footerurl)
        if str(r.status_code) == "200":
            return True
        return False
    
    except requests.ConnectionError:
        return False

def createXMLfile(key, body):
    
    filename = format(key + ".xml") 
    f = open('test/'+filename, mode='w', encoding="utf-8")
    f.write(body)
    f.close()

def getNotes(itemkey):
    try:
        notes = zot.children(itemkey)
        return notes
    except KeyboardInterrupt:
        sys.exit('Manually interrupted export.')
    except:
        print('Impossibile ottenere le note per questa item '+itemkey)
        print('Aspetto 30s')
        time.sleep(30.0)
        print('Nuovo tentativo')
        getNotes(itemkey)

count = 0
try:
    print('Downloading Zotero data...')
    zot = zotero.Zotero(guid, typeid, apiKey)
    items = zot.everything(zot.top())
except KeyboardInterrupt:
    sys.exit('Manually interrupted download.')
except pyzotero.zotero_errors.HTTPError as e:
    sys.exit(f'Errore a monte da Zotero: {e}')

for item in items:
    if DEBUG_MODE:
        print(' DEBUG: full item')
        print(item)
        print('ITEM[DATA]:')
        print(item['data'])
    
    if item['data']['itemType'] != 'note':
        
        itemNotes = getNotes(item['data']['key'])
        if itemNotes:
            item['data']['notes'] = [note['data'] for note in itemNotes]
        
        if item['data']['series']:
            item['data']['ckimage'] = check_iiif_image(item['data']['series'])
        else:
            item['data']['ckimage'] = False
    
    count += 1    
    print(f'{count}/{len(items)} ({round(count/len(items)*100, 1)}%)')

    xml = generateItem(item['data'], items, guid ) #corpo dati completo (corretto), items, group id
    
    if DEBUG_MODE:
        print(' DEBUG: expected xml body:')
        print(xml)
    
    createXMLfile(item['data']['key'], xml)

    if DEBUG_MODE:
        try: a = input(" DEBUG STOP...")
        except KeyboardInterrupt:
            print('\n Interrupting...')
            time.sleep(0.5)
            print(' Manually interrupted.')
            break