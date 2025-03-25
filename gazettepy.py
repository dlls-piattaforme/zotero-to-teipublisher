from pyzotero import zotero
from teigazette import generateItem
import time
import sys
from os import mkdir
try:
    sys.path.insert(1, '../lib') #cambiare a seconda della posizione di libexports.py
    from libexports import is_debug_mode, get_api_data
except:
    print(' [WARNING] Custom library libexports not found in lib')

DEBUG_MODE = is_debug_mode(sys.argv)

try: mkdir('test')
except FileExistsError: pass

typeid = 'group'
if get_api_data('gazette') is not None:
    apiKey = get_api_data('gazette')[0]
    guid = get_api_data('gazette')[1]
else:
    sys.exit("Fatal: API keys not provided.")

def createXMLfile(key, body):
    
    filename = format(key + ".xml") 
    f = open('test/'+filename, mode='w', encoding="utf-8") #cambiare prefisso a seconda di dove si vuole che i file vengano scaricati
    f.write(body)
    f.close()

count = 0
try:
    print('Downloading Zotero data...')
    zot = zotero.Zotero(guid, typeid, apiKey)
    print('Connection established.')
    top = zot.top()
    print("Fetching data...")
    items = zot.everything(top)
except pyzotero.zotero_errors.HTTPError as e:
    sys.exit(f'Errore a monte da Zotero: {e}')

for item in items:
    if DEBUG_MODE:
        print(' DEBUG: full item')
        print(item)
        print('ITEM[DATA]:')
        print(item['data'])
    
    count += 1    
    print(f'{count}/{len(items)} ({round(count/len(items)*100, 1)}%)')

    if not item['data']['title']: #non considerare elementi vuoti (titolo è dato obbligatorio, se non c'è allora si assume che l'elemento sia vuoto)
        continue

    xml = generateItem(item['data'], guid ) #corpo dati completo (corretto), items, group id
    
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

