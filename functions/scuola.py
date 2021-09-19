from datetime               import datetime, timedelta

from .utils                 import * 
from .file                  import *

import argoscuolanext
import random
import json
import os

import globals




__all__ = [
    'get_today',
    'compiti',
    'promemoria_giornaliero',
    'promemoria',
    'sacrifica'
]




codice_scuola = 'SS16383'

uname = None if globals.name else os.environ['USERNAME']
passw = None if globals.name else os.environ['PASSWORD']

gruppo_old = 534734869
gruppo = -1001261320605
privata = 781455352

mesi = {
    '01': 'GENNAIO',
    '02': 'FEBBRAIO',
    '03': 'MARZO',
    '04': 'APRILE',
    '05': 'MAGGIO',
    '06': 'GIUGNO',
    '07': 'LUGLIO',
    '08': 'AGOSTO',
    '09': 'SETTEMBRE',
    '10': 'OTTOBRE',
    '11': 'NOVEMBRE',
    '12': 'DICEMBRE'
}

prof = {
    'barone':       'Scienze',
    'la terza':     'Religione',
    'spognetta':    'Educazione Fisica',
    'navarra':      'Arte',
    'perini':       'Matematica/Fisica',
    'petterlini':   'Italiano/Latino',
    'pollaci':      'Storia/Filosofia',
    'sforza':       'Inglese'
}




def format_data(ctx):
    args = '-'.join(ctx.args).replace('/', '-').split('-')[::-1]
    today = datetime.today()
    year, month = today.year, today.month

    if args == ['']:
        return (today + timedelta(days = 1)).strftime('%Y-%m-%d')
    elif len(args) == 3:
        if len(args[0]) == 2:
            args[0] = '20' + args[0]
    elif len(args) == 2:
        args = [year, *args]
    elif len(args) == 1:
        if len(month := str(month)) == 1:
            month = f'0{month}'

        args = [str(year), month, args[0]]

    for i in range(len(args)):
        if len(str(args[i])) == 1:
            args[i] = f'0{args[i]}'

    return '-'.join([str(i) for i in args])




def get_today(ctx, update = False):
    session = argoscuolanext.Session(codice_scuola, uname, passw)
    arg = session.oggi()
    dati = arg['dati']

    valid = {
        i['dati']['desMateria']: i['dati']['desArgomento']
        for i in dati if i['titolo'] == 'Argomenti lezione'
    }

    if len(valid) == 0:
        msg = 'Non ci sono novità per oggi\.'
    else:
        msg = f'*GLI ARGOMENTI DELLE LEZIONI DI OGGI*\n\n\n'
        c = 1

        for k, v in valid.items():
            msg += f'{c}\. *{escape_md(k)}*\n\n{escape_md(v)}\n\n\n'
            c += 1


    if not update:
        msg = send(gruppo, msg.strip())['result']
        chat = msg['chat']['id']
        msg = msg['message_id']
        pin(chat, msg)
    else:
        reply(update, msg.strip(), markdown = 2)



def filtra_compiti(arg, data):
    result = [(i['desMateria'], i['desCompiti']) for i in arg['dati'] if i['datCompiti'] == data]

    if len(result) > 0:
        msg = ''
        c = 1

        for i in result:
            msg += f'{c}\. *{escape_md(i[0])}*\n\n{escape_md(i[1])}\n\n\n'
            c += 1
    else:
        msg = None

    return msg



def compiti(update, ctx):
    data = format_data(ctx)

    g = data.split('-')[2]
    m = mesi[data.split('-')[1]]
    giorno = f'{int(g)} {m[0] + m[1:].lower()}'

    session = argoscuolanext.Session("SS16383", uname, passw)
    arg = session.compiti()

    if not (msg := filtra_compiti(arg, data)):
        msg = f'Non ci sono compiti per il {giorno} e per i 5 giorni successivi\.'
        altro = ''

        for _ in range(5):
            data = (datetime.strptime(data, '%Y-%m-%d') + timedelta(days = 1)).strftime('%Y-%m-%d')

            if not (msg_2 := filtra_compiti(arg, data)):
                continue

            g = data.split('-')[2]
            m = mesi[data.split('-')[1]]

            altro = f'*I COMPITI PIÙ VICINI SONO PER IL {int(g)} {m}*\n\n\n' + msg_2
            break

        if altro:
            msg = f'Non ci sono compiti per il {giorno}\.\n\n\n' + altro
    else:
        msg = f'*COMPITI PER IL {int(g)} {m}*\n\n\n' + msg

    reply(update, msg, markdown = 2)



def promemoria_giornaliero(ctx):
    data = (datetime.today() + timedelta(days = 1)).strftime('%Y-%m-%d')
    session = argoscuolanext.Session("SS16383", uname, passw)
    prom = session.promemoria()['dati']

    g = data.split('-')[2]
    m = mesi[data.split('-')[1]]
    msg = f'*PROMEMORIA {int(g)} {m}*\n\n\n'
    c = 0

    for i in prom:
        if i['datGiorno'] == data:
            c += 1
            msg += f'{c}. *' + escape_md(i['desMittente']) + '*\n\n' + escape_md(i['desAnnotazioni'])
            msg += '\n\n\n'

    if not c:
        return

    send(gruppo, msg)




def promemoria(update, ctx):
    data = format_data(ctx)
    session = argoscuolanext.Session("SS16383", uname, passw)
    prom = session.promemoria()['dati']
    g = data.split('-')[2]
    m = mesi[data.split('-')[1]]
    msg = f'*PROMEMORIA {int(g)} {m}*\n\n\n'
    c = 0

    for i in prom:
        if i['datGiorno'] == data:
            c += 1
            msg += f'{c}\. *' + escape_md(i['desMittente']) + '*\n\n' + escape_md(i['desAnnotazioni'])
            msg += '\n\n\n'

    if not c:
        msg = f'Non ci sono promemoria per il {int(g)} {m.lower()}\.'

    reply(update, msg, markdown = 2)




def sacrifica(update, ctx):
    with open('classe.json', encoding = 'utf-8') as f:
        classe = json.load(f)

    if len(ctx.args) == 0:
        num = 2
    else:
        num = min(int(ctx.args[0]), len(classe))

    res = ''

    for _ in range(num):
        choice = random.choices(list(classe.keys()), list(classe.values()), k = 1)[0]
        res += choice + '\n'
        del classe[choice]

    reply(update, res)





# BETA

def bacheca():
    session = argoscuolanext.Session("SS16383", uname, passw)
    arg = session.bacheca()['dati']
    print(json.dumps(arg, indent=4))
    del session