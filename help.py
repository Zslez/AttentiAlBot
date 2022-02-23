from telegram           import InlineKeyboardButton, InlineKeyboardMarkup

from functions.utils    import send, send_up, chunks

import globals
import os


__all__ = [
    'callback_delete',
    'callback_null',
    'private_deco',
    'help',
    'help_callback',
    'deco',

    'privata',
    'gruppo',
    'attentiallog',

    'intusers',
    'users'
]

privata      = 781455352            # il mio ID Telegram
gruppo       = -1001261320605       # l'ID del gruppo
news_channel = -1001568629792       # l'ID del canale delle news
attentiallog = -1001533648966       # l'ID del canale delle notifiche che uso per risolvere gli errori

users = [str(privata)] if globals.name else os.environ['USERS'].split(',')
intusers = [int(i) for i in users]


# lista dei comandi del Bot dei quali è possibile vedere la spiegazione con /help

comandi = [
    # comandi per scuola
    [
        'argomenti',
        'calcola',
        'compiti',
        'news',
        'promemoria',
        'sacrifica',
        'voti'
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


def deco(func):
    def new_func(update, ctx):
        message = update.message
        uid = message.from_user.id


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


def private_deco(func):
    def new_func(update, ctx):
        try:
            func(update, ctx)
        except:
            user = update.message.from_user
            send_up(
                update,
                f'Hey [{user.name}](tg://user?id={user.id}), inviami prima un messaggio in privata.',
                1
            )

    return new_func


# funzione help con i vari buttons per le info

@private_deco
def help(update, ctx):
    keyboard = help_keyboard()

    markup = InlineKeyboardMarkup(keyboard)

    if ctx._chat_id_and_data[0] == gruppo:
        update.message.delete()

    ctx.bot.send_message(update.message.from_user.id, 'Su cosa ti serve aiuto?', reply_markup = markup)


def help_keyboard():
    return [
        [InlineKeyboardButton('INFO', callback_data = 'null')],
        [
            InlineKeyboardButton('lista comandi', callback_data = 'help_lista'),
            InlineKeyboardButton('formati data', callback_data = 'help_data')
        ],
        [InlineKeyboardButton('COMANDI SCUOLA', callback_data = 'null')],
        *[[InlineKeyboardButton(i, callback_data = f'help_{i}') for i in j] for j in chunks(comandi[0], 3)],
        [InlineKeyboardButton('ALTRI COMANDI', callback_data = 'null')],
        *[[InlineKeyboardButton(i, callback_data = f'help_{i}') for i in j] for j in chunks(comandi[1], 3)],
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
                    [InlineKeyboardButton('indietro', callback_data = 'help_back')],
                    [InlineKeyboardButton('🗑️', callback_data = 'delete')]
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
                            [InlineKeyboardButton('indietro', callback_data = 'help_back')],
                            [InlineKeyboardButton('🗑️', callback_data = 'delete')]
                        ]),
                        parse_mode = 'markdownv2'
                    )

    return ctx.bot.answer_callback_query(update.callback_query['id'])


def callback_delete(update, ctx):
    update.callback_query.message.delete()
    return ctx.bot.answer_callback_query(update.callback_query['id'])


def callback_null(update, ctx):
    return ctx.bot.answer_callback_query(update.callback_query['id'])
