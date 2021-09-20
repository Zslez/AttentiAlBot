from telegram.ext                   import Updater, CommandHandler, MessageHandler, Filters, Defaults
from telegram                       import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext                   import JobQueue, CallbackQueryHandler
from logging                        import getLogger, basicConfig, DEBUG
from datetime                       import time, timedelta
from random                         import choice

from telegram.update import Update

from functions.classroom            import *
from functions.heroku               import *
from functions.scuola               import *
from functions.utils                import *
from functions.file                 import *
from functions.news                 import *

import globals

import heroku3
import pytz
import json
import os



# LOGGER

basicConfig(level = DEBUG, format = '%(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


# VARIABLES

token = os.environ['TOKEN']

globals.lnu = None if globals.name else os.environ['LNU']
globals.max_news = 70 if globals.name else int(os.environ['MAXNEWS'])
globals.hnews = None if globals.name else os.environ['NEWS']

with open('start.txt', encoding = 'utf-8') as f:
    start_text = f.read().strip()

privata      = 781455352            # il mio ID Telegram
gruppo       = -1001261320605       # l'ID del gruppo
news_channel = -1001568629792       # l'ID del canale delle news
attentiallog = -1001533648966       # l'ID del canale delle notifiche che uso per risolvere gli errori

users = [str(privata)] if globals.name else os.environ['USERS'].split(',')
intusers = [int(i) for i in users]

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


# lista dei comandi del Bot dei quali è possibile vedere la spiegazione con /help

comandi = [
    # comandi per scuola
    [
        'argomenti',
        'class',
        'compiti',
        'news',
        'sacrifica',
        'promemoria'
    ],
    # altri comandi
    [
        'audio',
        'cut',
        'earrape',
        'image',
        'loop',
        'reverse',
        'speed',
        'speedpitch',
        'video'
    ]
]


comandi_per_tutti = [
    'start',
    'help'
]



# COMANDI

def start(update, ctx):
    reply(
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
(https://github.com/Zslez/AttentiAlBot/blob/master/main.py#L{globals.lineno}), quindi, \
*NON* inviare mai dati sensibili al Bot quando usi un comando, anche perché *non è mai necessario farlo*\.
Di conseguenza, non mi prendo alcuna responsabilità per questo tipo di _incidenti_\.
Dato che ancora ogni tanto escono fuori cose da sistemare, \
per ora rimane così, poi credo toglierò questa cosa\.'''
        ][update.message.chat.id != gruppo],
        markdown = 2
    )



# funzione help con i vari buttons per le info

@private_deco
def help(update, ctx):
    keyboard = help_keyboard()

    markup = InlineKeyboardMarkup(keyboard)

    if ctx._chat_id_and_data[0] == gruppo:
        update.message.delete()
        ctx.bot.send_message(update.message.from_user.id, 'Su cosa ti serve aiuto?', reply_markup = markup)
        return

    update.message.reply_markdown(text = 'Su cosa ti serve aiuto?', reply_markup = markup)


def help_keyboard():
    return [
        [InlineKeyboardButton('INFO', callback_data = 'null')],
        [
            InlineKeyboardButton('lista comandi', callback_data = 'help_lista'),
            InlineKeyboardButton('formati data', callback_data = 'help_data')
        ],
        [InlineKeyboardButton('COMANDI SCUOLA', callback_data = 'null')]
    ] + [
        [InlineKeyboardButton(i, callback_data = f'help_{i}') for i in j] for j in chunks(comandi[0], 3)
    ] + [
        [InlineKeyboardButton('ALTRI COMANDI', callback_data = 'null')]
    ] + [
        [InlineKeyboardButton(i, callback_data = f'help_{i}') for i in j] for j in chunks(comandi[1], 3)
    ] + [
        [InlineKeyboardButton('🗑️', callback_data = 'delete')]
    ]


# handler che viene chiamato quando vengono premuti i buttons del comando help

def help_callback(update, ctx):
    data = update.callback_query['data'].split('_')[-1]
    msg = update.callback_query.message

    if data == 'back':
        msg.edit_text(
            'Su cosa ti serve aiuto?',
            reply_markup = InlineKeyboardMarkup(help_keyboard()),
            parse_mode = 'markdownv2'
        )

    elif data in ('lista', 'data'):
        with open(f'help/{data}.txt', encoding = 'utf-8') as f:
            msg.edit_text(
                f.read(),
                reply_markup = InlineKeyboardMarkup([
                    [InlineKeyboardButton('indietro', callback_data = 'help_back')]
                ]),
                parse_mode = 'markdownv2'
            )

    else:
        for i in comandi[0] + comandi[1]:
            if data == i:
                with open(f'help/comandi/{i}.txt', encoding = 'utf-8') as f:
                    msg.edit_text(
                        f.read(),
                        reply_markup = InlineKeyboardMarkup([
                            [InlineKeyboardButton('indietro', callback_data = 'help_back')]
                        ]),
                        parse_mode = 'markdownv2'
                    )

    return ctx.bot.answer_callback_query(update.callback_query['id'])



def deco(func):
    def new_func(update, ctx):
        message = update.message
        uid = message.from_user.id
        uname = message.from_user.first_name


        # se chi usa il comando non sono io

        if uid != privata:
            send(
                attentiallog,
                'USER ID: ' + str(uid) + \
                '\nUSER NAME: ' + uname + \
                f'\nREGISTRATO: {uid in intusers}' + \
                '\nCOMANDO:\n' + message.text.replace('@AttentiAlGruppoBot', '')
            )


        # se chi usa il comando non è nella lista di chi può usare il Bot

        if uid not in intusers:
            if message.chat_id != gruppo and func.__name__ not in comandi_per_tutti:
                send(uid, 'Invia prima un messaggio nel gruppo, così so che fai parte della classe\.')
                return
            else:
                users.append(str(uid))
                intusers.append(uid)

        func(update, ctx)

    return new_func



def get_users(update, ctx):
    if update.message.from_user.id == privata:
        users_lst = [ctx.bot.get_chat_member(chat_id = gruppo, user_id = i).user for i in intusers]
        send(
            privata,
            '\n'.join(
                ['`' + str(i.id).ljust(15) + ' ' + i.first_name + '`' for i in users_lst]
            )
        )



def get_today_again(update, ctx):
    get_today(ctx, update)



def update_and_restart(update, ctx = None):
    if (ctx != None and update.message.from_user.id == privata) or ctx == None:
        for i in globals.messages:
            delete(attentiallog, i)

        heroku3.from_key(hkey2).app(
            ['attenti-al-bot-2', 'attenti-al-bot'][bool(hname.replace('attenti-al-bot', ''))]
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
    reply(update, choice(ridere))



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

    dp.add_handler(cmdh("argomenti",  get_today_again))
    dp.add_handler(cmdh("class",      get_courses))
    dp.add_handler(cmdh("compiti",    compiti))
    dp.add_handler(cmdh("orario",     orario))
    dp.add_handler(cmdh("news",       get_news_command))
    dp.add_handler(cmdh("promemoria", promemoria))
    dp.add_handler(cmdh("sacrifica",  sacrifica))


    # ALIAS

    dp.add_handler(cmdh("h",          help))

    dp.add_handler(cmdh("a",          to_audio))
    dp.add_handler(cmdh("arg",        get_today_again))
    dp.add_handler(cmdh("e",          earrape))
    dp.add_handler(cmdh("i",          image))
    dp.add_handler(cmdh("l",          loop_audio_video))
    dp.add_handler(cmdh("r",          reverse_audio_video))
    dp.add_handler(cmdh("s",          speed_audio_video))
    dp.add_handler(cmdh("sp",         speed_pitch_audio_video))
    dp.add_handler(cmdh("v",          to_video))

    dp.add_handler(cmdh("cl",         get_courses))
    dp.add_handler(cmdh("c",          compiti))
    dp.add_handler(cmdh("n",          get_news_command))
    dp.add_handler(cmdh("p",          promemoria))


    # PER ME

    dp.add_handler(cmdh("users",      get_users))
    dp.add_handler(cmdh("restart",    update_and_restart))


    # ALTRI HANDLER

    dp.add_handler(MessageHandler(Filters.text, word_check))

    dp.add_handler(CallbackQueryHandler(courses_callback_choice,    pattern = '^classchoice_'))
    dp.add_handler(CallbackQueryHandler(courses_callback_work,      pattern = '^classwork_'))
    dp.add_handler(CallbackQueryHandler(courses_callback_ann,       pattern = '^classann_'))

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

    job1.run_daily(callback = update_and_restart,     days = (0, 1, 2, 3, 4, 5, 6), time = time(hour =  3, minute =  0))
    job2.run_daily(callback = change_heroku,          days = (0, 1, 2, 3, 4, 5, 6), time = time(hour =  5, minute =  0))
    job3.run_daily(callback = get_today,              days = (0, 1, 2, 3, 4      ), time = time(hour = 15, minute = 30))
    job4.run_daily(callback = promemoria_giornaliero, days = (0, 1, 2, 3,       6), time = time(hour = 15, minute = 40))

    job5.run_repeating(callback = get_news_job,       first = news_secs[0],         interval = timedelta(minutes  =  3))

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
