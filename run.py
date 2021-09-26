import json
import os


classe = {i.split(':')[0]: int(i.split(':')[1]) for i in os.environ['CLASSE'].split(',')}

with open('classe.json', 'w') as f:
    json.dump(classe, f)


import globals

with open('help.py', encoding = 'utf-8') as f:
    globals.lineno = f.readlines().index('def deco(func):\n') + 1

globals.name = False


with open('bad.txt', 'w', encoding = 'utf-8') as f:
	f.write('\n'.join(os.environ['BAD'].split(';;;')))


import main