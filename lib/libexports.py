import json

def is_debug_mode(arg):
    is_debug = len(arg) == 2 and arg[1] == '--debug'
    return is_debug

def get_api_data(groupname):
    try:
        with open('../apikeys.json', 'r') as f:
            data = json.load(f)
            apiKey = data[groupname]
            guid = data[f'{groupname}-group']
            f.close()
        
        return (apiKey, guid)
    except FileNotFoundError:
        return None