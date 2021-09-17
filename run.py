import json
import os



def join(str1, str2):
	a = list(str1)
	b = list(str2)
	biter = iter(b)

	if len(a) == len(b):
		a = [' '] + a

	res = '?'.join(a)

	while '?' in res:
		res = res.replace('?', next(biter), 1)

	if len(a) == len(b):
		return (res.strip() + b[-1])[::-1]
	else:
		return res[::-1].strip()



token = {}

token['token']          = join(*os.environ['GTOKEN'].split(';;;'))
token['refresh_token']  = join(*os.environ['GREFRESH'].split(';;;'))
token['token_uri']      = os.environ['GURI']
token['client_id']      = os.environ['GCLIENTID']
token['client_secret']  = join(*os.environ['GSECRET'].split(';;;'))
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



with open('bad.txt', 'w', encoding = 'utf-8') as f:
	f.write('\n'.join(os.environ['BAD'].split(';;;')))



import main