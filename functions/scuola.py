from datetime               import datetime, timedelta
from statistics             import stdev

from .utils                 import * 
from .file                  import *

import argoscuolanext
import random
import pytz
import json
import os

import globals




__all__ = [
    'get_today',
    'compiti',
    'promemoria_giornaliero',
    'promemoria',
    'sacrifica',
    'analizza_voti'
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



def format_data(ctx, days):
    args = '-'.join(ctx.args).replace('/', '-').split('-')[::-1]
    today = datetime.now(pytz.timezone('Europe/Rome'))
    year, month = str(today.year), str(today.month)

    if args == ['']:
        return (today + timedelta(days = days)).strftime('%Y-%m-%d'), True
    elif len(args) == 3:
        if len(args[0]) == 2:
            args[0] = '20' + args[0]
    elif len(args) == 2:
        args = [year, *args]
    elif len(args) == 1:
        args = [year, month, args[0]]

    for i in range(len(args)):
        if len(args[i]) == 1:
            args[i] = '0' + args[i]

    return '-'.join(args), False




def get_today(ctx, update = False):
    session = argoscuolanext.Session(codice_scuola, uname, passw)
    default = True

    if update:
        data, default = format_data(ctx, 0)
        arg = session.oggi(data)
    else:
        arg = session.oggi()

    dati = arg['dati']

    if default:
        giorno = 'oggi'
    else:
        g = int(data.split('-')[2])
        m = mesi[data.split('-')[1]].capitalize()
        giorno = f'{g} {m}'

    valid = {
        i['dati']['desMateria']: i['dati']['desArgomento']
        for i in dati if i['titolo'] == 'Argomenti lezione'
    }

    if len(valid) == 0:
        msg = f'Nessuna novità per il giorno {giorno}\.'
    else:
        if default:
            msg = '*COSA È SUCCESSO OGGI*\n\n\n'
        else:
            msg = f'*COSA È SUCCESSO IL GIORNO {giorno.upper()}*\n\n\n'

        c = 1

        for k, v in valid.items():
            msg += f'{c}\. *{escape_md(k)}*\n\n{escape_md(v)}\n\n'
            c += 1


    if not update:
        send(gruppo, msg.strip())
    else:
        send_up(update, msg.strip())



def filtra_compiti(arg, data):
    result = [(i['desMateria'], i['desCompiti']) for i in arg['dati'] if i['datCompiti'] == data]

    if len(result) > 0:
        msg = ''
        c = 1

        for i in result:
            msg += f'{c}\. *{escape_md(i[0])}*\n\n{escape_md(i[1])}\n\n'
            c += 1
    else:
        msg = None

    return msg



def compiti(update, ctx):
    data, default = format_data(ctx, 1)

    g = int(data.split('-')[2])
    m = mesi[data.split('-')[1]].capitalize()
    gio = f'{g} {m}'

    session = argoscuolanext.Session("SS16383", uname, passw)
    arg = session.compiti()

    if not (msg := filtra_compiti(arg, data)):
        if default:
            msg = f'Nessun compito per i prossimi 6 giorni\.'
        else:
            msg = f'Nessun compito per il giorno {gio} e per i 5 successivi\.'

        for _ in range(5):
            data = (datetime.strptime(data, '%Y-%m-%d') + timedelta(days = 1)).strftime('%Y-%m-%d')

            if not (msg_2 := filtra_compiti(arg, data)):
                continue

            g = int(data.split('-')[2])
            m = mesi[data.split('-')[1]]

            if default:
                msg = f'Nessun compito per domani\.\n\n\n*COMPITI PER {g} {m}*\n\n\n{msg_2}'
            else:
                msg = f'Nessun compito per il giorno {gio}\.\n\n\n*COMPITI PER {g} {m}*\n\n\n{msg_2}'

            break
    else:
        if default:
            msg = f'*COMPITI PER DOMANI*\n\n\n' + msg
        else:
            msg = f'*COMPITI PER {g} {m.upper()}*\n\n\n' + msg

    send_up(update, msg)



def promemoria_giornaliero(ctx):
    data = (datetime.now(pytz.timezone('Europe/Rome')) + timedelta(days = 1)).strftime('%Y-%m-%d')
    session = argoscuolanext.Session("SS16383", uname, passw)
    prom = session.promemoria()['dati']

    g = int(data.split('-')[2])
    m = mesi[data.split('-')[1]]
    msg = f'*PROMEMORIA {g} {m}*\n'
    c = 0

    for i in prom:
        if i['datGiorno'] == data:
            c += 1
            msg += f'\n\n{c}\. *' + escape_md(i['desMittente']) + '*\n\n' + escape_md(i['desAnnotazioni'])

    if not c:
        return

    send(gruppo, msg)




def promemoria(update, ctx):
    data, default = format_data(ctx, 1)
    session = argoscuolanext.Session("SS16383", uname, passw)
    prom = session.promemoria()['dati']

    g = int(data.split('-')[2])
    m = mesi[data.split('-')[1]]
    msg = f'*PROMEMORIA {g} {m}*\n'
    c = 0

    for i in prom:
        if i['datGiorno'] == data:
            c += 1
            msg += f'\n\n{c}\. *' + escape_md(i['desMittente']) + '*\n\n' + escape_md(i['desAnnotazioni'])

    if not c:
        if default:
            msg = 'Nessun promemoria per domani\.'
        else:
            msg = f'Nessun promemoria per il giorno {g} {m.lower()}\.'

    send_up(update, msg)




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

    send_up(update, res, 0)



def analizza_voti(update, ctx):
    if not (voti := [float(i) for i in ctx.args]):
        return

    if not all(0 <= i <= 10 for i in voti):
        return

    just = 15

    def format_row(word, num, newlines = 1):
        if int(num) == num:
            num = int(num)

        return '\n' * newlines + (word + ':').ljust(just) + str(num)

    media = round(sum(voti) / len(voti), 2)

    res = format_row('media', media, 0)
    res += format_row('massimo', max(voti), 1)
    res += format_row('minimo', min(voti), 1)

    if media <= 2 or (media <= 3 and len(voti) > 2):
        send_up(update, '😳')
        return
    elif media <= 5.5:
        recupero = 5.5 * (len(voti) + 1) - sum(voti)
        res += format_row('per il 5.5', recupero, 2)

        if recupero >= 9:
            send_up(update, '```\n' + escape_md(res) + ' 😳' + '```')
            return

    if media <= 6:
        recupero = 6 * (len(voti) + 1) - sum(voti)
        res += format_row('per il 6', recupero, 2)

        if recupero >= 9:
            res += ' 😳'

    send_up(update, '```\n' + escape_md(res) + '```')