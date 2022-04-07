from telegram.ext                   import Updater, CommandHandler, MessageHandler, Filters, Defaults
from telegram.ext                   import JobQueue, CallbackQueryHandler
from bs4                            import BeautifulSoup as bs
from datetime                       import time, timedelta
from logging                        import getLogger#, basicConfig, DEBUG
from random                         import choice
from requests                       import get

from functions.calcolatrice.solver  import *
from functions.calcolatrice.calc    import *
from functions.heroku               import *
from functions.scuola               import *
from functions.utils                import *
from functions.file                 import *
from functions.news                 import *

from personale.musei                import *

from help                           import *

import globals

import heroku3
import pytz
import os



# LOGGER

#basicConfig(format = '%(name)s - %(levelname)s - %(message)s', level = DEBUG)
logger = getLogger(__name__)


# VARIABLES

token = os.environ['TOKEN']

globals.max_news    = 90    if globals.name else int(os.environ['MAXNEWS'])
globals.hnews       = None  if globals.name else os.environ['NEWS']
globals.lnu         = None  if globals.name else os.environ['LNU']

with open('start.txt', encoding = 'utf-8') as f:
    start_text = f.read().strip()

news_secs = (2000, 3000) if globals.name else (20,  70)
pers_secs = (4000, 5000) if globals.name else (30,  50)

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
    send_up(update, 'Hey' + ['', '\n\n' + start_text][update.message.chat.id != gruppo])



def argomenti(update, ctx):
    get_today(ctx, update)



def update(update, ctx):
    if update.message.from_user.id == privata:
        with open('novità.txt', encoding = 'utf-8') as f:
            send(gruppo, f.read())



def update_and_restart(update, ctx = None):
    if (ctx != None and update.message.from_user.id == privata) or ctx == None:
        for i in globals.messages:
            delete(attentiallog, i)

        musei = ';'.join(globals.musei.values())

        heroku3.from_key(hkey2).app(
            ['attentialbot2', 'attentialbot'][bool(hname.replace('attentialbot', ''))]
        ).config().update(
            {
                'USERS': ','.join(users),
                'LNU': globals.lnu,
                'MAXNEWS': globals.max_news,
                'NEWS': globals.hnews,
                'MUSEI': musei
            }
        )

        heroku3.from_key(hkey).app(hname).config().update(
            {
                'USERS': ','.join(users),
                'LNU': globals.lnu,
                'MAXNEWS': globals.max_news,
                'NEWS': globals.hnews,
                'MUSEI': musei
            }
        )



# ALTRE FUNZIONI


def orario(update, ctx):
    with open(f'orario/orario.png', 'rb') as f:
        ctx.bot.send_photo(ctx._chat_id_and_data[0], photo = f)



def burla_italiana(update, ctx):
    send_up(update, choice(ridere))



def pise(update, ctx):
    folder_base_url = 'https://drive.google.com/drive/folders/'
    file_base_url = 'https://drive.google.com/uc?export=download&id='
    pise_parent = folder_base_url + '1a_hfzfhDSWQ6vZ62AQJPDR1r4xWZUA3-'

    req = bs(get(pise_parent).content, 'html.parser')
    folder = choice([i.get('data-id') for i in req.find_all('div', {'draggable': True})])
    req = bs(get(folder_base_url + folder).content, 'html.parser')
    file = file_base_url + choice([i.get('data-id') for i in req.find_all('div', {'draggable': True})])

    ctx.bot.send_photo(ctx._chat_id_and_data[0], file)



def grazie(update, ctx):
    send_up(update, '❤️')
    send(update.message.from_user.id, 'ti voglio bene anche io ❤️', 0)



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

    if 'interroga' in txtspl and not any(i in txtspl for i in ['non', 'nn', '?']):
        with open('video/Directed_by_Robert_Weide.mp4', 'rb') as f:
            update.message.reply_video(f, 'Directed_by_Robert_Weide.mp4',
                caption = '🎵pom pom pom, turuturutturù, turù turù🎵\n🎵turù tuturuturutturù, turù IIIH🎵')
            return


# handler per gli errori per non far crashare tutto

def error(update, ctx):
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

    dp.add_handler(cmdh("tivogliobenecristiano", grazie))
    dp.add_handler(cmdh("help",                  help))
    dp.add_handler(cmdh("start",                 start))


    # COMANDI PER DIVERTIMENTO

    dp.add_handler(cmdh("audio",      to_audio))
    dp.add_handler(cmdh("burla",      burla_italiana))
    dp.add_handler(cmdh("cut",        cut_audio_video))
    dp.add_handler(cmdh("earrape",    earrape))
    dp.add_handler(cmdh("gif",        gif))
    dp.add_handler(cmdh("loop",       loop_audio_video))
    dp.add_handler(cmdh("image",      image))
    dp.add_handler(cmdh("pise",       pise))
    dp.add_handler(cmdh("reverse",    reverse_audio_video))
    dp.add_handler(cmdh("speed",      speed_audio_video))
    dp.add_handler(cmdh("speedpitch", speed_pitch_audio_video))
    dp.add_handler(cmdh("video",      to_video))
    dp.add_handler(cmdh("voti",       analizza_voti))


    # SCUOLA

    dp.add_handler(cmdh("argomenti",  argomenti))
    dp.add_handler(cmdh("calcola",    calc))
    dp.add_handler(cmdh("compiti",    compiti))
    dp.add_handler(cmdh("orario",     orario))
    dp.add_handler(cmdh("news",       get_news_command))
    dp.add_handler(cmdh("promemoria", promemoria))
    dp.add_handler(cmdh("risolvi",    solve))
    dp.add_handler(cmdh("sacrifica",  sacrifica))
    dp.add_handler(cmdh("zeri",       zeri))


    # ALIAS

    dp.add_handler(cmdh("h",          help))

    dp.add_handler(cmdh("a",          to_audio))
    dp.add_handler(cmdh("arg",        argomenti))
    dp.add_handler(cmdh("b",          burla_italiana))
    dp.add_handler(cmdh("e",          earrape))
    dp.add_handler(cmdh("g",          gif))
    dp.add_handler(cmdh("i",          image))
    dp.add_handler(cmdh("l",          loop_audio_video))
    dp.add_handler(cmdh("o",          orario))
    dp.add_handler(cmdh("r",          reverse_audio_video))
    dp.add_handler(cmdh("s",          speed_audio_video))
    dp.add_handler(cmdh("sp",         speed_pitch_audio_video))
    dp.add_handler(cmdh("v",          to_video))

    dp.add_handler(cmdh("c",          compiti))
    dp.add_handler(cmdh("calc",       calc))
    dp.add_handler(cmdh("n",          get_news_command))
    dp.add_handler(cmdh("solve",      solve))
    dp.add_handler(cmdh("p",          promemoria))
    dp.add_handler(cmdh("z",          zeri))


    # PER ME

    dp.add_handler(cmdh("restart",    update_and_restart))
    dp.add_handler(cmdh("update",     update))


    # ALTRI HANDLER

    dp.add_handler(MessageHandler(Filters.text, word_check))

    dp.add_handler(CallbackQueryHandler(callback_delete, pattern = '^delete'))
    dp.add_handler(CallbackQueryHandler(callback_null,   pattern = '^null'))

    dp.add_handler(CallbackQueryHandler(cp_callback,     pattern = '^(compito|promemoria)'))
    dp.add_handler(CallbackQueryHandler(help_callback,   pattern = '^help_'))

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
    job3.run_daily(callback = get_today,              days = days(4),       time = time2(13, 45))
    job4.run_daily(callback = promemoria_giornaliero, days = days(6),       time = time2(13, 40))

    job5.run_repeating(callback = get_news_job, first = news_secs[0], interval = timedelta(minutes = 7))

    job1.start()
    job2.start()
    job3.start()
    job4.start()
    job5.start()


    # JOB PERSONALI

    jobp1 = JobQueue()
    jobp2 = JobQueue()
    jobp3 = JobQueue()

    jobp1.set_dispatcher(dp)
    jobp2.set_dispatcher(dp)
    jobp3.set_dispatcher(dp)

    jobp1.run_daily(callback = domenica_al_museo, days = (0,),          time = time2(10,  0))
    jobp2.run_daily(callback = stasera_in_tv,     days = days(4, 5, 6), time = time2(18,  0))

    jobp3.run_repeating(callback = culture_roma, first = pers_secs[0], interval = timedelta(minutes = 14))

    jobp1.start()
    jobp2.start()
    jobp3.start()


    # PRENDE LE NEWS DALLA BACHECA

    up.job_queue.run_repeating(callback = get_news, interval = timedelta(minutes = 7), first = news_secs[1])

    up.start_polling()

    print('Ready')

    up.idle()

main()
