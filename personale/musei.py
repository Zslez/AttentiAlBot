from telegram           import InlineKeyboardButton, InlineKeyboardMarkup
from bs4                import BeautifulSoup as bs
from datetime           import datetime, timedelta
from warnings           import simplefilter
from pytz               import timezone
from requests           import get
from telegram.ext.callbackcontext import CallbackContext

import string
import re

from functions.utils    import send, escape_md, chunks

import globals

def escape_md(text):
	chars = '_-~' + '*+=>' + '({[]})' + '|!#`.'

	for i in chars:
		text = text.replace(i, f'\\{i}')

	return text


__all__ = [
    'domenica_al_museo',
    'culture_roma',
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

def stasera_in_tv(ctx: CallbackContext, page = 0, edit = False):
    size = 4
    url = 'https://www.staseraintv.com/film_in_tv_stasera.html'

    req = bs(get(url).content, 'html.parser')
    table = req.find('div', {'class': 'maincolumn'}).find_all('table', {'style': 'height:53px;color:white'})
    lnt = len(table)

    res = '*STASERA IN TV*\n\n'
    lst = []

    for i in table:#[page * size: (page + 1) * size]:
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
            #reply_markup = InlineKeyboardMarkup(keyboard)
        )



def tv_callback(update, ctx):
    stasera_in_tv(ctx, int(update.callback_query['data'].split('_')[-1]), update.callback_query.message)
    return ctx.bot.answer_callback_query(update.callback_query['id'])



def comingsoon(ctx):
    url = 'https://www.comingsoon.it/film/2022/'



def culture_roma(ctx):
    urls = [
        'https://culture.roma.it/estateromana/arte/',
        'https://culture.roma.it/estateromana/film/',
        'https://culture.roma.it/estateromana/musica/',
        'https://culture.roma.it/estateromana/teatro/',
        'https://culture.roma.it/estateromana/incroci-artistici/',
        'https://culture.roma.it/estateromana/camminando/'
    ]

    base_url = 'https://culture.roma.it'

    for i in urls:
        arg = i.split('/')[-2].replace('-', ' ')
        tit = 'CULTURE ROMA \- ' + arg.upper()
        req = bs(get(i, verify = False).content, 'html.parser')

        if i == urls[-1]:
            post = req.find('div', {'class': 'archivio_prossimi_appuntamenti'})

            if (post := post.find('div', {'class': 'post_event_calendar'})) == None:
                return
        else:
            post = req.find('div', {'class': 'post_event_calendar'})

        title = post.find('h2', {'class': 'page_title'})
        url = base_url + title.find('a').get('href')
        title = escape_md(title.text)

        if pattern.sub('', title) == globals.musei['roma_' + arg.split()[0]]:
            continue
        else:
            globals.musei['roma_' + arg.split()[0]] = pattern.sub('', title)

        date = post.find('span', {'class': 'dates'}).text.replace('.', '/')

        if '─' in date:
            date = 'dal ' + ' al '.join([f'*{i.strip()}*' for i in date.split(' ─ ')])

        subtitle = escape_md(post.find('p', {'class': 'page_subtitle'}).text)

        if (place := post.find('a', {'class': 'link_luogo'})) == None:
            place_name = post.find('span', {'class': 'luogo_title'}).text
            place_url = ''
        else:
            place_name, place_url = place.text, base_url + place.get('href')

        place = f'[*{escape_md(place_name)}*]({escape_md(place_url)})'
        add = escape_md(post.find('span', {'class': 'location'}).text)

        send(chan, f'*🆕 {tit}*\n\n[*{title}*]({url})\n\n📅 {date}\n📍 {place} \- {add}\n\n_{subtitle}_')



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


if __name__ == '__main__':
    stasera_in_tv(0)
