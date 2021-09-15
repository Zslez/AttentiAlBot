import json
import os



token = {}

token['token']          = os.environ['GTOKEN']
token['refresh_token']  = os.environ['GREFRESH']
token['token_uri']      = os.environ['GURI']
token['client_id']      = os.environ['GCLIENTID']
token['client_secret']  = os.environ['GSECRET']
token['scopes']         = os.environ['GSCOPES'].split(',')
token['expiry']         = os.environ['GEXP']

with open('token.json', 'w') as f:
    json.dump(token, f)



classe = {i.split(':')[0]: int(i.split(':')[1]) for i in os.environ['CLASSE'].split(',')}

with open('classe.json', 'w') as f:
    json.dump(classe, f)



import globals

with open('main.py', encoding = 'utf-8') as f:
    globals.lineno = f.readlines().index('def deco(func):\n') + 1

globals.name = False



import main