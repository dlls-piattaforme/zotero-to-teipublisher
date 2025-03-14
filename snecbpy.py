from pyzotero import zotero
from snecbtei import generateItem
from snecbtei import getBibCitation
import itertools
import threading
import html
import time
import sys
from datetime import datetime
from os import mkdir
try:
    sys.path.insert(1, '../lib')
    from libexports import is_debug_mode, get_api_data
except:
    print(' [WARNING] Custom library libexports not found in lib')

#SCRIPT SNORRI

DEBUG_MODE = is_debug_mode(sys.argv)
LIMIT = 30 #solo per debug: documenti da scaricare anziché everything

#########Zotero data CONNECTION########
typeid = 'group'
if get_api_data('snorri') is not None:
    apiKey = get_api_data('snorri')[0]
    guid = get_api_data('snorri')[1]
else:
    sys.exit("Fatal: API keys not provided.")
#####################################

##############LOADER################
done = False 
totItems = 0
completeItem  = 0
####################################

try: mkdir('test')
except FileExistsError: pass

print("["+datetime.now().strftime("%H:%M:%S")+"] - START [Download Items]")

zot = zotero.Zotero(guid, typeid, apiKey)
#Esporta array di item da zotero complete di tutti i metadati 

# per test - limit = numero di items da scaricare da zotero 
if DEBUG_MODE: 
    print(f'[DEBUG] Downloading {LIMIT} items...')
    items = zot.top(limit=LIMIT)
else: 
    print(' Connected. Downloading all items...')
    items = zot.everything(zot.top())
    #items = zot.top(limit=None)

totItems = len(items)

##############################################################################  
#Loader Animation
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\r'+str(completeItem)+'/'+str(totItems)+ c + ' - ' + str(round(completeItem/totItems*100, 1)) + '%')
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\n['+datetime.now().strftime("%H:%M:%S")+'] - DONE!!!!\n')
##############################################################################
#Crea file xml nella cartella test 
def createXMLfile(tit, key, allxml):
    
    filename = format(key + ".xml") 
    f = open('test/'+filename, mode='w', encoding="utf-8")
    f.write(allxml)
    f.close()

###########################################################################
#Funzione che scarica le note associate all'id dell'item
def getNotes(itemkey):
    try:
        notes = zot.children(itemkey)
        return notes
    except:
        print('\n['+itemkey+'] - Error\n')
        time.sleep(30.0)
        print('\n['+itemkey+'] - Retrying\n')
        getNotes(itemkey)
###############################################################################
#Funzione per ripulire la stringa della citazione bibliografica dai tag
def cleanCit(citbb):
        citbb[0] = citbb[0].replace('<div class="csl-entry">', '').replace('</div>','').replace('<i>', '').replace('</i>', '')
        citbb[0] = citbb[0][:-1]
        return citbb[0]

###################################################################################
#Funzione che restituisce la citazione bibliografica con stile chicago ( se va in errore attende e riprova )
def getCit(itemkey):
    
    try:
        cit = zot.item(itemkey, content='bib', style='chicago-fullnote-bibliography', limit=None) #limit=None risolve il limite default dei 100 importato da pyzotero
        if cit:
            return cleanCit(cit)
        else:
            print('\n[ERROR on '+itemkey+']\n'+cit+'\n')
    except Exception as e:
        print('['+itemkey+f'] - Error: {e}') #EDIT: exception e per debug download xml rotti o falliti
        cit = zot.item(itemkey, content='bib', style='chicago-fullnote-bibliography', limit=None)
        print('Waiting 50s to recover...')
        time.sleep(50.0)
        return cleanCit(cit)
    

print('\n['+datetime.now().strftime("%H:%M:%S")+'] - Download Citations\nCirca 1h necessaria')

########################################INZIO####################################
# Per ogni item scarica la citazione
for index, item in enumerate(items):
    itemCit = getCit(item['data']['key'])
    print(f"[ {round(index/totItems*100, 1)}% ] Got {item['data']['key']} citation ({index+1}/{totItems})")
    if itemCit:
        item['data']['bibcit'] = html.unescape(itemCit) 

print('\n['+datetime.now().strftime("%H:%M:%S")+'] - Create XML\n')
print('necessari circa 35 minuti')

#START LOADER
if not DEBUG_MODE:
    t = threading.Thread(target=animate)
    t.start()

#ciclo principale , associa ad ogni item le sue note e genera l'xml per la creazione del documento
for index, item in enumerate(items):

    if DEBUG_MODE: print(index + 1)

    if DEBUG_MODE:
        print(f"[DEBUG] ITEM DATA FOR {item['data']['key']}:")
        print(item)
        try: a = input('DEBUG STOP...')
        except KeyboardInterrupt:
            print('\n Interrupting...')
            time.sleep(0.5)
            sys.exit(' Manually interrupted.')
    
    if item['data']['itemType'] != 'note':
        
        itemNotes = getNotes(item['data']['key'])
        if itemNotes:
            item['data']['notes'] = [note['data'] for note in itemNotes]
        
        
        xml = generateItem(item['data'], items, guid )
        createXMLfile(item['data']['title'], item['data']['key'], xml)
        completeItem += 1

#stop loader
done = True