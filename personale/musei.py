from telegram           import InlineKeyboardButton, InlineKeyboardMarkup
from bs4                import BeautifulSoup as bs
from datetime           import datetime, timedelta
from warnings           import simplefilter
from pytz               import timezone
from requests           import get

import re


__all__ = [
    'domenica_al_museo',
    'stasera_in_tv',
    'tv_callback'
]


simplefilter('ignore')


chan = -1001608595750
save = -1001688642977

pattern = re.compile('[\W_]+')



## =================== link utili =================== ##

# https://www.comingsoon.it/film/2022/

# https://www.teatro.it/spettacoli/roma/

# https://www.oggiroma.it/eventi/gennaio/2022/

## =================== link utili =================== ##



# FUNZIONI

def stasera_in_tv(ctx, page = 0, edit = False):
    size = 4
    url = 'https://www.staseraintv.com/film_in_tv_stasera.html'

    req = bs(get(url).content, 'html.parser')
    table = req.find('div', {'class': 'maincolumn'}).find_all('table', {'style': 'height:53px;color:white'})
    lnt = len(table)

    res = '*STASERA IN TV*\n\n'
    lst = []

    for i in table[page * size: (page + 1) * size]:
        text = [j for j in i.text.split('\n') if j]
        text[0] = f'*{text[0].upper()}* (canale {text[3]})'
        lst.append(f'{text[0]}\n```{text[1]}``` - {text[2]}')

    keyboard = [[]]

    if page > 0:
        keyboard.append([InlineKeyboardButton('⬅️', callback_data = f'tv_{page - 1}')])

    if (page + 1) * size < lnt:
        keyboard.append([InlineKeyboardButton('➡️', callback_data = f'tv_{page + 1}')])

    if edit != False:
        edit.edit_text(
            res + '\n\n'.join(lst),
            parse_mode = 'markdown',
            reply_markup = InlineKeyboardMarkup(keyboard)
        )
    else:
        ctx.bot.send_message(
            chat_id = chan,
            text = res + '\n\n'.join(lst),
            parse_mode = 'markdown',
            reply_markup = InlineKeyboardMarkup(keyboard)
        )



def tv_callback(update, ctx):
    stasera_in_tv(ctx, int(update.callback_query['data'].split('_')[-1]), update.callback_query.message)
    return ctx.bot.answer_callback_query(update.callback_query['id'])



def domenica_al_museo(ctx):
    next_sunday = datetime.now(timezone('Europe/Rome')) + timedelta(days = 6)

    if int(next_sunday.strftime('%d')) <= 7:
        with open('personale/images/domenica.jpg', 'rb') as f:
            ctx.bot.send_photo(
                chan,
                photo = f,
                caption = '*Domenica prossima ' +
                next_sunday.strftime('%d/%m/%Y') +
                ' sarà la prima del mese.*\n\n' +
                'Cerca quali musei aderiscono all\'iniziativa.',
                parse_mode = 'markdown'
            )

