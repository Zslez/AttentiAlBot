import json
import os


classe = {i.split(':')[0]: int(i.split(':')[1]) for i in os.environ['CLASSE'].split(',')}

with open('classe.json', 'w') as f:
    json.dump(classe, f)


import globals

globals.name = False

musei_env = os.environ['MUSEI'].split(';')
musei = {
    'roma_arte': None,
    'roma_film': None,
    'roma_musica': None,
    'roma_teatro': None,
    'roma_incroci': None,
    'roma_camminando': None,
    'comingsoon': None,
    'eventi': None
}

globals.musei = {list(musei)[i]: musei_env[i] for i in range(len(musei_env))}


with open('bad.txt', 'w', encoding = 'utf-8') as f:
	f.write('\n'.join(os.environ['BAD'].split(';;;')))


import main