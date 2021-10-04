from telegram.ext                   import Updater, CommandHandler, MessageHandler, Filters, Defaults
from telegram.ext                   import JobQueue, CallbackQueryHandler
from datetime                       import time, timedelta
from logging                        import getLogger
from random                         import choice

from functions.heroku               import *
from functions.scuola               import *
from functions.utils                import *
from functions.file                 import *
from functions.news                 import *

from help                           import *

import globals

import heroku3
import pytz
import json
import os



# LOGGER

logger = getLogger(__name__)


# VARIABLES

token = os.environ['TOKEN']

globals.lnu = None if globals.name else os.environ['LNU']
globals.max_news = 70 if globals.name else int(os.environ['MAXNEWS'])
globals.hnews = None if globals.name else os.environ['NEWS']

with open('start.txt', encoding = 'utf-8') as f:
    start_text = f.read().strip()

news_secs = (1000, 3000) if globals.name else (10, 30)

with open('burla.txt', encoding = 'utf-8') as f:
    ridere = f.read().split('\n')

giorni = [
    'lunedì',
    'martedì',
    'mercoledì',
    'giovedì',
    'venerdì'
]



# COMANDI

def start(update, ctx):
    send_up(
        update,
        choice(
            [
                'Weilà',
                'Hey',
                'Привет',
                'ちわっす',
                '嘿'
            ]
        ) + [
            '',
            '\n\n' + start_text + f'''\n\n\n*ATTENZIONE*
per sapere se ci sono errori e per capire come correggerli, \
[inoltro in un canale privato il testo di tutti i comandi usati]\
(https://github.com/Zslez/AttentiAlBot/blob/master/help.py#L{globals.lineno}), quindi, \
*NON* inviare mai dati sensibili al Bot quando usi un comando, anche perché *non è mai necessario farlo*\.
Di conseguenza, non mi prendo alcuna responsabilità per questo tipo di _incidenti_\.
Dato che ancora ogni tanto escono fuori cose da sistemare, \
per ora rimane così, poi credo toglierò questa cosa\.'''
        ][update.message.chat.id != gruppo],
        markdown = 2
    )



def get_users(update, ctx):
    if update.message.from_user.id == privata:
        users_lst = [ctx.bot.get_chat_member(chat_id = gruppo, user_id = i).user for i in intusers]
        send(
            privata,
            '\n'.join(
                ['`' + str(i.id).ljust(15) + ' ' + i.first_name + '`' for i in users_lst]
            )
        )



def argomenti(update, ctx):
    get_today(ctx, update)



def update_and_restart(update, ctx = None):
    if (ctx != None and update.message.from_user.id == privata) or ctx == None:
        for i in globals.messages:
            delete(attentiallog, i)

        heroku3.from_key(hkey2).app(
            ['attentialbot2', 'attentialbot'][bool(hname.replace('attentialbot', ''))]
        ).config().update(
            {
                'USERS': ','.join(users),
                'LNU': globals.lnu,
                'MAXNEWS': globals.max_news,
                'NEWS': globals.hnews
            }
        )

        heroku3.from_key(hkey).app(hname).config().update(
            {
                'USERS': ','.join(users),
                'LNU': globals.lnu,
                'MAXNEWS': globals.max_news,
                'NEWS': globals.hnews
            }
        )



# ALTRE FUNZIONI


def orario(update, ctx):
    try:
        day = 0 if len(ctx.args) == 0 else max(min(int(ctx.args[0]), 5), 1)
    except:
        return

    with open(f'orario/orario_{day}.jpg', 'rb') as f:
        update.message.reply_photo(f, [f'orario {giorni[day - 1]}', None][day == 0])



def burla_italiana(update, ctx):
    send_up(update, choice(ridere))



def word_check(update, ctx):
    message = update.effective_message
    text = message.text.lower()
    txtspl = text.split()

    try:
        uid = message.from_user.id
    except:
        return


    # se chi ha usato il comando non è nella lista di chi può usare il Bot
    # ma il messaggio è stato inviato sul gruppo, questo viene aggiunto alla lista

    if uid not in intusers and message.chat_id == gruppo:
        users.append(str(uid))
        intusers.append(uid)


    # goliardia

    if 'sborr' in text or 'cum' in txtspl:
        with open('video/quando_sborri.mp4', 'rb') as f:
            update.message.reply_video(f, 'quando_sborri.mp4',
                caption = '🎵turuturù turuturù turuturù🎵\n🎵turutututurutu turutu tù!🎵')
            return
    elif ('interroga' in txtspl or 'interroga?' in text) and 'non' not in txtspl and 'nn' not in txtspl:
        with open('video/Directed_by_Robert_Weide.mp4', 'rb') as f:
            update.message.reply_video(f, 'Directed_by_Robert_Weide.mp4',
                caption = '🎵pom pom pom, turuturutturù, turù turù🎵\n🎵turù tuturuturutturù, turù IIIH🎵')
            return


# handler per gli errori per non far crashare tutto
# prova ad inviarmi un log dell'errore su un canale privato,
# così posso capire cosa non va

def error(update, ctx):
    try:
        send(
            attentiallog,
            f'*UPDATE:*\n```\n{escape_md(json.dumps(update.effective_message.to_dict(), indent = 4))}```' \
                f'\n\n*ERROR:*\n{escape_md(str(ctx.error))}'
        )
    except:
        send(attentiallog, f'*ERROR:*\n{str(ctx.error)}', 1)

    logger.warning('Update "%s" caused error "%s"', update, ctx.error)



# MAIN

def main():
    up = Updater(token, use_context = True, defaults = Defaults(tzinfo = pytz.timezone('Europe/Rome')))
    dp = up.dispatcher

    def cmdh(name, func):
        return CommandHandler(name, deco(func), run_async = True)

    def days(*args):
        return (0, 1, 2, 3) + tuple(args)

    def time2(h, m):
        return time(hour = h, minute = m)


    # COMANDI BASE

    dp.add_handler(cmdh("help",       help))
    dp.add_handler(cmdh("start",      start))


    # COMANDI PER DIVERTIMENTO

    dp.add_handler(cmdh("audio",      to_audio))
    dp.add_handler(cmdh("burla",      burla_italiana))
    dp.add_handler(cmdh("cut",        cut_audio_video))
    dp.add_handler(cmdh("earrape",    earrape))
    dp.add_handler(cmdh("loop",       loop_audio_video))
    dp.add_handler(cmdh("image",      image))
    dp.add_handler(cmdh("reverse",    reverse_audio_video))
    dp.add_handler(cmdh("speed",      speed_audio_video))
    dp.add_handler(cmdh("speedpitch", speed_pitch_audio_video))
    dp.add_handler(cmdh("video",      to_video))


    # SCUOLA

    dp.add_handler(cmdh("argomenti",  argomenti))
    dp.add_handler(cmdh("compiti",    compiti))
    dp.add_handler(cmdh("orario",     orario))
    dp.add_handler(cmdh("news",       get_news_command))
    dp.add_handler(cmdh("promemoria", promemoria))
    dp.add_handler(cmdh("sacrifica",  sacrifica))


    # ALIAS

    dp.add_handler(cmdh("h",          help))

    dp.add_handler(cmdh("a",          to_audio))
    dp.add_handler(cmdh("arg",        argomenti))
    dp.add_handler(cmdh("b",          burla_italiana))
    dp.add_handler(cmdh("e",          earrape))
    dp.add_handler(cmdh("i",          image))
    dp.add_handler(cmdh("l",          loop_audio_video))
    dp.add_handler(cmdh("r",          reverse_audio_video))
    dp.add_handler(cmdh("s",          speed_audio_video))
    dp.add_handler(cmdh("sp",         speed_pitch_audio_video))
    dp.add_handler(cmdh("v",          to_video))

    dp.add_handler(cmdh("c",          compiti))
    dp.add_handler(cmdh("n",          get_news_command))
    dp.add_handler(cmdh("p",          promemoria))


    # PER ME

    dp.add_handler(cmdh("users",      get_users))
    dp.add_handler(cmdh("restart",    update_and_restart))


    # ALTRI HANDLER

    dp.add_handler(MessageHandler(Filters.text, word_check))

    dp.add_handler(CallbackQueryHandler(callback_delete,            pattern = '^delete'))
    dp.add_handler(CallbackQueryHandler(callback_null,              pattern = '^null'))

    dp.add_handler(CallbackQueryHandler(help_callback,              pattern = '^help_'))

    dp.add_error_handler(error)


    # JOB QUEUES

    job1 = JobQueue()
    job2 = JobQueue()
    job3 = JobQueue()
    job4 = JobQueue()
    job5 = JobQueue()

    job1.set_dispatcher(dp)
    job2.set_dispatcher(dp)
    job3.set_dispatcher(dp)
    job4.set_dispatcher(dp)
    job5.set_dispatcher(dp)

    job1.run_daily(callback = update_and_restart,     days = days(4, 5, 6), time = time2( 3,  0))
    job2.run_daily(callback = change_heroku,          days = days(4, 5, 6), time = time2( 5,  0))
    job3.run_daily(callback = get_today,              days = days(4),       time = time2(15, 25))
    job4.run_daily(callback = promemoria_giornaliero, days = days(6),       time = time2(15, 30))

    job5.run_repeating(callback = get_news_job, first = news_secs[0], interval = timedelta(minutes = 3))

    job1.start()
    job2.start()
    job3.start()
    job4.start()
    job5.start()


    # PRENDE LE NEWS DALLA BACHECA

    up.job_queue.run_repeating(callback = get_news, interval = timedelta(minutes = 3), first = news_secs[1])

    up.start_polling()

    print('Ready')

    up.idle()


main()
