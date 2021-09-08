from telegram.ext       import Updater, CommandHandler, MessageHandler, Filters, JobQueue, CallbackQueryHandler
from telegram           import InlineKeyboardButton, InlineKeyboardMarkup
from logging            import basicConfig, DEBUG, getLogger
from datetime           import time, timedelta
from random             import choice

from telegram.update    import Update

import globals

globals.name = __name__ == '__main__'

from functions.classroom    import *
from functions.heroku       import *
from functions.scuola       import *
from functions.utils        import *
from functions.file         import *
from functions.news         import *

import heroku3
import json
import os



# LOGGER

#basicConfig(level = DEBUG, format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)



# VARIABLES

token = os.environ['TOKEN']

privata = 781455352                 # il mio ID Telegram
gruppo = -1001261320605             # l'ID del gruppo
news_channel = -1001568629792       # l'ID del canale delle news
attentiallog = -1001533648966       # l'ID del canale delle notifiche utili a me per risolvere gli errori

users = [str(privata)] if globals.name else os.environ['USERS'].split(',')
intusers = [int(i) for i in users]


# non dire queste parole

with open('json/bad_words_list.json', encoding = 'utf-8') as f:
    bad_words = json.load(f)


# lista dei comandi del Bot

comandi = [
    'class',
    'compiti',
    'sacrifica',
    'promemoria',

    'audio',
    'cut',
    'earrape',
    'image',
    'reverse',
    'speed',
    'speedpitch',
    'video'
]




# COMANDI GENERICI

def start(update, ctx):
    if update.message.chat.id == gruppo:
        reply(update, choice(['Weilà', 'Hey', 'Привет', 'ちわっす', '嘿']))
        return

    reply(update, choice(['Weilà', 'Hey', 'Привет', 'ちわっす', '嘿']) + '\n' + '''
*Info sul Bot*

Con questo Bot è possibile \
ottenere *compiti*, *promemoria* e *notizie* direttamente su Telegram senza bisogno di credenziali, sia in chat privata che sui gruppi\.

Il Bot invierà anche alcuni messaggi in automatico sul gruppo ogni giorno ad un certo orario, \
come gli argomenti della giornata appena finita, i promemoria e i compiti per il giorno successivo\.

Inoltre ci sono tante altre funzioni per puro divertimento, che servono a modificare in vari modi audio e video \
\(funziona anche con i *messaggi vocali*\)\.


*Come usare i comandi*

Usa il comando /help per ricevere la lista dei comandi e informazioni dettagliate su come usarli\.


*Nuove funzioni da proporre?*

Scrivi a *[Cristiano](https://t.me/cristiano_san)* \(scrivigli anche se non hai roba da proporre, \
sono piuttosto sicuro non gli dispiaccia\)\.


*Non ti fidi di [Cristiano](https://t.me/cristiano_san)?*

Understandable, tuttavia ti invito a dare un'occhiata al codice del Bot [qui](https://github.com/Zslez/AttentiAlBot) su GitHub, \
completo e commentato\.
Se ne capisci un minimo vedrai che non c'è nulla di losco, anche perché vengono usate le mie credenziali per accedere ad ARGO\.
''', markdown = 2)


# funzione help con i vari buttons per le info

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
        [InlineKeyboardButton('COMANDI', callback_data = 'null')]
    ] + [
        [InlineKeyboardButton(i, callback_data = f'help_{i}') for i in j] for j in chunks(comandi, 3)
    ] + [
        [InlineKeyboardButton('🗑️', callback_data = 'delete')]
    ]


# handler che viene chiamato quando vengono premuti i buttons del comando help

def help_callback(update: Update, ctx):
    data = update.callback_query['data'].split('_')[-1]
    msg = update.callback_query.message

    if data == 'back':
        msg.edit_text(
            'Su cosa ti serve aiuto?',
            reply_markup = InlineKeyboardMarkup(help_keyboard()),
            parse_mode = 'markdownv2'
        )

    elif data == 'delete':
        msg.delete()

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
        for i in comandi:
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
        uid = update.message.from_user.id
        uname = update.message.from_user.first_name

        if uid != privata:
            send(
                attentiallog,
                'USER ID: ' + uid + \
                f'REGISTRATO: {uid in intusers}' + \
                '\nUSER NAME: ' + uname + \
                '\n\nCOMANDO:\n' + \
                update.message.text
            )

        if uid not in intusers:
            send(uid, 'Invia prima un messaggio nel gruppo, così so che fai parte della classe.')
            return

        func(update, ctx)

    return new_func




# COMMANDS

def bad_word_check(update: Update, ctx):
    if update.message:
        message = update.message
    else:
        message = update.channel_post

    uid = message.from_user.id

    if uid not in users and message.chat_id == gruppo:
        users.append(str(uid))
        intusers.append(uid)
        app = heroku3.from_key(hkey).app(hname)
        config = app.config()
        config['USERS'] = ','.join(users)

    try:
        msg = message.text
    except:
        msg = update.text

    msg = msg.lower()

    if 'sborr' in msg or 'cum' in msg:
        with open('video/quando_sborri.mp4', 'rb') as f:
            update.message.reply_video(f, 'quando_sborri.mp4',
                caption = '🎵turuturù turuturù turuturù🎵\n🎵turutututurutu turutu tù!🎵')
            return
    elif ('interroga ' in msg or 'interroga?' in msg) and 'non' not in msg.split():
        with open('video/Directed_by_Robert_Weide.mp4', 'rb') as f:
            update.message.reply_video(f, 'Directed_by_Robert_Weide.mp4',
                caption = '🎵pom pom pom, turuturutturù, turù turù🎵\n🎵turù tuturuturutturù, turù IIIH🎵')
            return

    for i in bad_words:
        if i in msg.split():
            update.message.reply_text('Attento, la postale ti osserva.')


# handler per gli errori per non far crashare tutto
# prova ad inviarmi un log dell'errore in privata,
# così posso capire cosa non va

def error(update, ctx):
    try:
        send(
            privata,
            f'An error occurred!\n\n\nUpdate:\n```\n{json.dumps(update.to_dict(), indent = 4)}```' \
                f'\n\nError: {str(ctx.error)}',
            1
        )
    except:
        send(privata, f'An error occurred!\n\nError: {str(ctx.error)}', 0)

    logger.warning('Update "%s" caused error "%s"', update, ctx.error)



def restart(update, ctx):
    if update.message.from_user.id == privata:
        heroku3.from_key(hkey).app(hname).restart()



# MAIN

def main():
    up = Updater(token, use_context = True)
    dp = up.dispatcher

    dp.add_handler(CommandHandler("help",       deco(help)))
    dp.add_handler(CommandHandler("start",      deco(start)))

    dp.add_handler(CommandHandler("audio",      deco(to_audio)))
    dp.add_handler(CommandHandler("cut",        deco(cut_audio_video)))
    dp.add_handler(CommandHandler("earrape",    deco(earrape)))
    dp.add_handler(CommandHandler("image",      deco(image)))
    dp.add_handler(CommandHandler("reverse",    deco(reverse_audio_video)))
    dp.add_handler(CommandHandler("speed",      deco(speed_audio_video)))
    dp.add_handler(CommandHandler("speedpitch", deco(speed_pitch_audio_video)))
    dp.add_handler(CommandHandler("video",      deco(to_video)))


    # SCUOLA

    dp.add_handler(CommandHandler("compiti",    deco(compiti)))
    dp.add_handler(CommandHandler("sacrifica",  deco(sacrifica)))
    dp.add_handler(CommandHandler("promemoria", deco(promemoria)))

    dp.add_handler(CommandHandler("class",      deco(get_courses)))


    # ALIAS

    dp.add_handler(CommandHandler("h",          deco(help)))

    dp.add_handler(CommandHandler("a",          deco(to_audio)))
    dp.add_handler(CommandHandler("e",          deco(earrape)))
    dp.add_handler(CommandHandler("i",          deco(image)))
    dp.add_handler(CommandHandler("r",          deco(reverse_audio_video)))
    dp.add_handler(CommandHandler("s",          deco(speed_audio_video)))
    dp.add_handler(CommandHandler("sp",         deco(speed_pitch_audio_video)))
    dp.add_handler(CommandHandler("v",          deco(to_video)))

    dp.add_handler(CommandHandler("cl",         deco(get_courses)))
    dp.add_handler(CommandHandler("c",          deco(compiti)))
    dp.add_handler(CommandHandler("p",          deco(promemoria)))


    # ALTRI HANDLER

    dp.add_handler(MessageHandler(Filters.text, bad_word_check))

    dp.add_handler(CallbackQueryHandler(help_callback, pattern = '^help_'))
    dp.add_handler(CallbackQueryHandler(courses_callback_choice, pattern = '^classchoice_'))
    dp.add_handler(CallbackQueryHandler(courses_callback_ann, pattern = '^classann_'))
    dp.add_handler(CallbackQueryHandler(courses_callback_work, pattern = '^classwork_'))
    dp.add_handler(CallbackQueryHandler(callback_delete, pattern = '^delete'))
    dp.add_handler(CallbackQueryHandler(callback_null, pattern = '^null'))

    dp.add_error_handler(error)


    # JOB QUEUES

    job_queue1 = JobQueue()
    job_queue2 = JobQueue()
    job_queue3 = JobQueue()
    job_queue4 = JobQueue()
    job_queue5 = JobQueue()

    job_queue1.set_dispatcher(dp)
    job_queue2.set_dispatcher(dp)
    job_queue3.set_dispatcher(dp)
    job_queue4.set_dispatcher(dp)
    job_queue5.set_dispatcher(dp)

    job_queue1.run_daily(callback = change_heroku,            days = (0, 1, 2, 3, 4, 5, 6),   time = time(hour =  2, minute =  0))
    job_queue2.run_daily(callback = verifica,                 days = (0, 1, 2, 3, 4      ),   time = time(hour = 12, minute =  0))
    job_queue3.run_daily(callback = get_today,                days = (0, 1, 2, 3, 4      ),   time = time(hour = 12, minute = 30))
    job_queue4.run_daily(callback = promemoria_giornaliero,   days = (0, 1, 2, 3,       6),   time = time(hour = 13, minute =  0))
    job_queue5.run_daily(callback = promemoria_giornaliero,   days = (0, 1, 2, 3,       6),   time = time(hour = 19, minute =  0))

    job_queue1.start()
    job_queue2.start()
    job_queue3.start()
    job_queue4.start()
    job_queue5.start()


    # PRENDE LE NEWS DALLA BACHECA

    up.job_queue.run_repeating(callback = get_news, interval = timedelta(minutes = 150), first = 1000)

    up.start_polling()

    print('Ready')

    up.idle()


main()
