from telegram               import InlineKeyboardButton as Button, InlineKeyboardMarkup as Markup
from datetime               import datetime, timedelta

from .utils                 import * 
from .file                  import *

import argoscuolanext
import random
import pytz
import json
import os

import globals




__all__ = [
    'analizza_voti',
    'compiti',
    'cp_callback',
    'get_today',
    'promemoria',
    'promemoria_giornaliero',
    'sacrifica'
]




with open('classe.json', encoding = 'utf-8') as f:
    CLASSE = json.load(f)

SEP = '-'
CODICE = 'SS16383'
TIMEZONE = pytz.timezone('Europe/Rome')

UNAME = os.environ['NAMEUSER'] if globals.name else os.environ['USERNAME']
PASSW = os.environ['PASSWORD']

PRIVATA = 781455352
GRUPPO  = -1001261320605

MESI = {
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



def format_data(args, days):
    args = SEP.join(args).replace('/', SEP).split(SEP)[::-1]
    today = datetime.now(TIMEZONE)
    year, month = str(today.year), str(today.month)

    if args == ['']:
        return (today + timedelta(days = days)).strftime('%Y-%m-%d'), True

    if len(args) == 3 and len(args[0]) == 2:
        args[0] = '20' + args[0]
    elif len(args) == 2:
        args = [year, *args]
    elif len(args) == 1:
        args = [year, month, args[0]]

    for i in range(len(args)):
        if len(args[i]) == 1:
            args[i] = '0' + args[i]

    return SEP.join(args), False



def filtra(dati, data, args):
    result = [(i[args[0]], i[args[1]]) for i in dati['dati'] if i[args[2]] == data]

    if len(result) > 0:
        c = 0
        return ''.join([f'{(c := c + 1)}\. *{escape_md(i[0])}*\n\n{escape_md(i[1])}\n\n' for i in result])



def get_today(ctx, update = False):
    session = argoscuolanext.Session(CODICE, UNAME, PASSW)
    default = True

    if update:
        data, default = format_data(ctx.args, 0)
        arg = session.oggi(data)
    else:
        arg = session.oggi()

    dati = arg['dati']
    giorno = 'oggi' if default else f'{int(data.split(SEP)[2])} {MESI[data.split(SEP)[1]].capitalize()}'

    valid = {
        i['dati']['desMateria']: i['dati']['desArgomento']
        for i in dati if i['titolo'] == 'Argomenti lezione'
    }

    if len(valid) == 0:
        if not update:
            return

        msg = f'Nessuna novità per il giorno {giorno}\.'
    else:
        c = 0
        msg = '*COSA È SUCCESSO '
        msg += 'OGGI*\n\n\n' if default else f'IL GIORNO {giorno.upper()}*\n\n\n'

        for k, v in valid.items():
            msg += f'{(c := c + 1)}\. *{escape_md(k)}*\n\n{escape_md(v)}\n\n'

    if not update:
        send(GRUPPO, msg.strip())
    else:
        send_up(update, msg.strip())



def compiti_promemoria(update, ctx, dati, args, tipo, days = 1, edit = False, dir = 1):
    data, default = format_data([ctx.args, ['']][edit != False], days)
    default = not (edit or not default)
    orig_days = (days := days + 1) - 2
    max_days = 7

    gio = f'{int(data.split(SEP)[2])} {MESI[data.split(SEP)[1]].capitalize()}'
    tipo1, tipo2 = tipo
    c = 0

    if not (msg := filtra(dati, data, args)):
        dir2 = ['precedenti', 'successivi'][dir == 1]
        msg = f'Nessun {tipo1} per i'
        msg += ' prossimi 7 giorni\.' if default else f'l giorno {gio} e per i 6 {dir2}\.'

        for c in range(1, max_days):
            data = (datetime.strptime(data, '%Y-%m-%d') + dir * timedelta(days = 1)).strftime('%Y-%m-%d')

            if dir == 1:
                days += 1
            else:
                orig_days -= 1

            if not (msg_2 := filtra(dati, data, args)):
                continue

            msg = ''

            if not edit:
                msg = f'Nessun {tipo1} per '
                msg += f'domani\.\n\n\n' if default else f'il giorno {gio}\.\n\n\n'

            msg += f'*{tipo2} PER {int(data.split(SEP)[2])} {MESI[data.split(SEP)[1]]}*\n\n\n{msg_2}'

            break
    else:
        msg2 = msg
        msg = f'*{tipo2} PER DOMANI*\n\n\n' if default else f'*{tipo2} PER {gio.upper()}*\n\n\n'
        msg += msg2

    mark = [[
        Button('⬅️', None, f'{tipo1}_-1_{orig_days}'),
        Button('🗑️', None, 'delete'),
        Button('➡️', None, f'{tipo1}_1_{days}')
    ]]

    if data != format_data([], 1 + c)[0]:
        mark.append([Button('Resetta', None, f'{tipo[0]}_1_1')])

    if not edit:
        chat_id = update.message.chat.id
        ctx.bot.send_message(chat_id, msg, parse_mode = 'markdownv2', reply_markup = Markup(mark))
    else:
        edit.edit_text(msg, parse_mode = 'markdownv2', reply_markup = Markup(mark))



def cp_callback(update, ctx):
    tipo, dir, days = update.callback_query['data'].split('_')
    edit = update.callback_query.message

    [compiti, promemoria][tipo == 'promemoria'](update, ctx, int(days), edit, int(dir))

    return ctx.bot.answer_callback_query(update.callback_query['id'])



def compiti(update, ctx, days = 1, edit = False, dir = 1):
    session = argoscuolanext.Session(CODICE, UNAME, PASSW)
    arg = session.compiti()
    args = ['desMateria', 'desCompiti', 'datCompiti']

    compiti_promemoria(update, ctx, arg, args, ['compito', 'COMPITI'], days, edit, dir)



def promemoria(update, ctx, days = 1, edit = False, dir = 1):
    session = argoscuolanext.Session(CODICE, UNAME, PASSW)
    prom = session.promemoria()
    args = ['desMittente', 'desAnnotazioni', 'datGiorno']

    compiti_promemoria(update, ctx, prom, args, ['promemoria', 'PROMEMORIA'], days, edit, dir)



def promemoria_giornaliero(ctx):
    data = (datetime.now(TIMEZONE) + timedelta(days = 1)).strftime('%Y-%m-%d')
    session = argoscuolanext.Session(CODICE, UNAME, PASSW)
    prom = session.promemoria()['dati']

    g = int(data.split(SEP)[2])
    m = MESI[data.split(SEP)[1]]
    msg = f'*PROMEMORIA {g} {m}*\n'
    c = 0

    for i in prom:
        if i['datGiorno'] == data:
            c += 1
            msg += f'\n\n{c}\. *' + escape_md(i['desMittente']) + '*\n\n' + escape_md(i['desAnnotazioni'])

    if not c:
        return

    send(GRUPPO, msg)



def sacrifica(update, ctx):
    num = 2 if len(ctx.args) == 0 else min(int(ctx.args[0]), len(CLASSE))

    send_up(update, '\n'.join(random.sample(list(CLASSE), num)), 0)



def analizza_voti(update, ctx):
    if not (voti := [float(i) for i in ctx.args]) or (not all(0 <= i <= 10 for i in voti)):
        return

    just = 15
    media = round(sum(voti) / len(voti), 2)
    res = 'media:'.ljust(just) + str(media)

    if media <= 2 or (media <= 3 and len(voti) > 2):
        send_up(update, '😳')
        return
    elif media <= 8:
        recupero = 5.5 * (len(voti) + 1) - sum(voti)
        res += '\n' + 'per il 5.5:'.ljust(just) + str(recupero)

        if recupero > 10:
            send_up(update, '```\n' + escape_md(res) + ' 😳' + '```')
            return

    if media <= 9:
        recupero = 6 * (len(voti) + 1) - sum(voti)
        res += '\n' + 'per il 6:'.ljust(just) + str(recupero)

        if recupero > 10:
            res += ' 😳'

    send_up(update, '```\n' + escape_md(res) + '```')