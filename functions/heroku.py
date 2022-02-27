# letteralmente io che aggiro i limiti del server che mi hosta il Bot, così da tenerlo attivo 24/7 per sempre

from datetime import datetime

import heroku3
import os

import globals


__all__ = [
    'change_heroku',
    'hkey',
    'hkey2',
    'hname'
]


hkey   = None if globals.name else os.environ['HKEY']
hkey2  = None if globals.name else os.environ['HKEY2']
hname  = None if globals.name else os.environ['HNAME']
hpass  = None if globals.name else os.environ['HPASS']
hemail = None if globals.name else os.environ['HEMAIL']


def change_heroku(ctx):
    if int(datetime.today().strftime('%d')) == 20:
        api = heroku3.from_key(hkey2)
        app = api.app(['attentialbot2', 'attentialbot'][bool(hname.replace('attentialbot', ''))])
        app.process_formation()['worker'].scale(1)

        api = heroku3.from_key(hkey)
        app = api.app(hname)
        app.process_formation()['worker'].scale(0)
