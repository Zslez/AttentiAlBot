from telegram   import InlineKeyboardButton, InlineKeyboardMarkup

from .utils     import escape_md

import globals




__all__ = [
    'get_courses',
    'courses_callback_choice',
    'courses_callback_ann',
    'courses_callback_work',
    'callback_delete',
    'callback_null'
]




months = [
    'Gennaio',
    'Febbraio',
    'Marzo',
    'Aprile',
    'Maggio',
    'Giugno',
    'Luglio',
    'Agosto',
    'Settembre',
    'Ottobre',
    'Novembre',
    'Dicembre'
]




def get_courses(update, ctx):
    keyboard = get_courses_keyboard()
    update.message.reply_markdown(text = 'Scegli un corso.', reply_markup = InlineKeyboardMarkup(keyboard))




def get_courses_keyboard():
    return [
        [
            InlineKeyboardButton(
                i['name'],
                callback_data = 'classchoice_' + str(i['id']) + '_' + '_'.join(i['name'].split())
            )
        ] for i in globals.courses
    ] + [
        [InlineKeyboardButton('🗑️', callback_data = 'delete')]
    ]




def courses_callback_choice(update, ctx):
    msg = update.callback_query.message
    data = update.callback_query['data'].split('_')

    if data[-1] == 'back':
        keyboard = get_courses_keyboard()

        msg.edit_text(
            f'Scegli un corso.',
            reply_markup = InlineKeyboardMarkup(keyboard)
        )

        return ctx.bot.answer_callback_query(update.callback_query['id'])

    id, *name = data[1:]
    name1 = ' '.join(name)
    name2 = '_'.join(name)

    keyboard = [
        [InlineKeyboardButton('annunci', callback_data = 'classann_' + id + '_' + name2)],
        [InlineKeyboardButton('compiti', callback_data = 'classwork_' + id + '_' + name2)],
        [InlineKeyboardButton('indietro', callback_data = 'classchoice_back')],
        [InlineKeyboardButton('🗑️', callback_data = 'delete')]
    ]

    msg.edit_text(
        f'Cosa ti serve della classe *{name1}*?',
        reply_markup = InlineKeyboardMarkup(keyboard),
        parse_mode = 'markdown'
    )

    return ctx.bot.answer_callback_query(update.callback_query['id'])




def courses_callback_ann(update, ctx):
    msg = update.callback_query.message
    data = update.callback_query['data'].split('_')[1:]
    page = 1

    id, *name = data
    name1 = ' '.join(name)
    name2 = '_'.join(name)

    if id == 'back':
        name1 = ' '.join(name1.split()[1:])

        keyboard = [
            [InlineKeyboardButton('post', callback_data = 'classann_' + name2)],
            [InlineKeyboardButton('compiti', callback_data = 'classwork_' + name2)],
            [InlineKeyboardButton('indietro', callback_data = 'classchoice_back')],
            [InlineKeyboardButton('🗑️', callback_data = 'delete')]
        ]

        msg.edit_text(
            f'Cosa ti serve della classe *{name1}*?',
            reply_markup = InlineKeyboardMarkup(keyboard),
            parse_mode = 'markdown'
        )

        return ctx.bot.answer_callback_query(update.callback_query['id'])
    elif id == 'page':
        id, *name1, page = name
        name1 = ' '.join(name[1:-1])
        name2 = '_'.join(name[1:-1])
        page = int(page)

    text, end = get_ann(id, name1, page)

    arrows = []

    if page > 1:
        arrows.append(
            InlineKeyboardButton(
                '⬅️',
                callback_data = 'classann_page_' + id + '_' + name2 + '_' + str(page - 1)
            )
        )

    if not end:
        arrows.append(
            InlineKeyboardButton(
                '➡️',
                callback_data = 'classann_page_' + id + '_' + name2 + '_' + str(page + 1)
            )
        )

    keyboard = [
        arrows,
        [InlineKeyboardButton('indietro', callback_data = 'classann_back_' + id + '_' + name2)],
        [InlineKeyboardButton('🗑️', callback_data = 'delete')]
    ]

    msg.edit_text(
        text,
        reply_markup = InlineKeyboardMarkup(keyboard),
        parse_mode = 'markdownv2'
    )

    return ctx.bot.answer_callback_query(update.callback_query['id'])




def get_ann(id, name, num):
    post = globals.service.announcements().list(courseId = id, pageSize = num + 1).execute().get('announcements', [[], []])
    name = escape_md(name)

    end = num == len(post)

    if end:
        post = post[-1]
    else:
        post = post[-2]

    if not post:
        return '_Questo corso non ha ancora nessun annuncio\._', True

    if num == 1:
        text = f'[*ULTIMO ANNUNCIO IN "{name.upper()}"*](' + post['alternateLink'] + ')\n\n'
    elif end:
        text = f'[*PRIMO ANNUNCIO IN "{name.upper()}"*](' + post['alternateLink'] + ')\n\n'
    else:
        text = f'[*ANNUNCIO IN "{name.upper()}"*](' + post['alternateLink'] + ')\n\n'

    text += escape_md(post['text']) + '\n'

    materials = get_materials(post)

    return text + materials, end




def get_materials(post):
    materials = ''

    if 'materials' in post:
        materials = '\n*ALLEGATI:*\n'
        mat = post['materials']

        for i in mat:
            for j in ['driveFile', 'youtubeVideo', 'link', 'form']:
                if j in i:
                    obj = i[j]

                    if j == 'driveFile':
                        obj = obj[j]
                        materials += ' ‣ [' + escape_md(obj['title']) + '](' + obj['alternateLink']
                    elif j == 'youtubeVideo':
                        materials += ' ‣ [' + escape_md(obj['title']) + '](' + obj['alternateLink']
                    elif j == 'link':
                        materials += ' ‣ [' + escape_md(obj['title']) + '](' + obj['url']
                    elif j == 'form':
                        materials += ' ‣ [' + escape_md(obj['title']) + '](' + obj['formUrl']

                    materials += ')\n'
    
    return materials




def get_work(id, num):
    post = globals.service.courseWork().list(courseId = id, pageSize = num + 1).execute().get('courseWork', [[], []])

    end = num == len(post)

    if end:
        post = post[-1]
    else:
        post = post[-2]

    date = ''

    if not post:
        return '_Questo corso non ha ancora nessun compito\._', True

    text = f'[*' + escape_md(post['title']).upper() + '*](' + post['alternateLink'] + ')\n'

    if 'description' in post:
        text += '\n' + escape_md(post['description']) + '\n'

    materials = get_materials(post)

    if 'dueDate' in post:
        date = '\n*DA CONSEGNARE ENTRO:*\n'
        duedate = post['dueDate']

        year = str(duedate['year']) if 'year' in duedate else ''
        month = months[duedate['month'] - 1] if 'month' in duedate else ''
        day = str(duedate['day']) if 'day' in duedate else ''

        time = post['dueTime']
        hours = str(time['hours'])
        mins = ':' + str(time['mins']).rjust(2, '0') if 'mins' in time else ':00'
        secs = ':' + str(time['secs']).rjust(2, '0') if 'secs' in time else ':00'

        date += f'{day} {month} {year} alle {hours}{mins}{secs}'.strip()

    return text + materials + date, end




def courses_callback_work(update, ctx):
    msg = update.callback_query.message
    data = update.callback_query['data'].split('_')[1:]
    page = 1

    id, *name = data
    name1 = ' '.join(name)
    name2 = '_'.join(name)

    if id == 'back':
        name1 = ' '.join(name1.split()[1:])

        keyboard = [
            [InlineKeyboardButton('post', callback_data = 'classann_' + name2)],
            [InlineKeyboardButton('compiti', callback_data = 'classwork_' + name2)],
            [InlineKeyboardButton('indietro', callback_data = 'classchoice_back')],
            [InlineKeyboardButton('🗑️', callback_data = 'delete')]
        ]

        msg.edit_text(
            f'Cosa ti serve della classe *{name1}*?',
            reply_markup = InlineKeyboardMarkup(keyboard),
            parse_mode = 'markdown'
        )

        return ctx.bot.answer_callback_query(update.callback_query['id'])
    elif id == 'page':
        id, *name1, page = name
        name1 = ' '.join(name[1:-1])
        name2 = '_'.join(name[1:-1])
        page  = int(page)

    text, end = get_work(id, page)

    arrows = []

    if page > 1:
        arrows.append(
            InlineKeyboardButton(
                '⬅️',
                callback_data = 'classwork_page_' + id + '_' + name2 + '_' + str(page - 1)
            )
        )

    if not end:
        arrows.append(
            InlineKeyboardButton(
                '➡️',
                callback_data = 'classwork_page_' + id + '_' + name2 + '_' + str(page + 1)
            )
        )

    keyboard = [
        arrows,
        [InlineKeyboardButton('indietro', callback_data = 'classwork_back_' + id + '_' + name2)],
        [InlineKeyboardButton('🗑️', callback_data = 'delete')]
    ]

    msg.edit_text(
        text,
        reply_markup = InlineKeyboardMarkup(keyboard),
        parse_mode = 'markdownv2'
    )

    return ctx.bot.answer_callback_query(update.callback_query['id'])




def callback_delete(update, ctx):
    update.callback_query.message.delete()
    return ctx.bot.answer_callback_query(update.callback_query['id'])




def callback_null(update, ctx):
    return ctx.bot.answer_callback_query(update.callback_query['id'])




def f(service, courseslist, num):
    courses = service

    courseWorks = courses.courseWork()
    courseWorks = [courseWorks.list(courseId = i['id'], pageSize = num).execute().get('courseWork', [[]])[-1] for i in courseslist]

    announcements = courses.announcements()
    announcements = [announcements.list(courseId = i['id'], pageSize = num).execute().get('announcements', [[]])[-1] for i in courseslist]

    print(announcements)
    input()

    titles          = [i[0]['title']            if i and 'title'            in i[0] else None for i in courseWorks]
    descriptions    = [i[0]['description']      if i and 'description'      in i[0] else None for i in courseWorks]
    materials       = [i[0]['materials']        if i and 'materials'        in i[0] else None for i in courseWorks]
    worklinks       = [i[0]['alternateLink']    if i and 'alternateLink'    in i[0] else None for i in courseWorks]

    duedates        = [i[0]['dueDate']          if i and 'dueDate'          in i[0] else None for i in courseWorks]
    duetimes        = [i[0]['dueTime']          if i and 'dueTime'          in i[0] else None for i in courseWorks]

    print(len(titles))

    print(len(descriptions))

    print(len(materials))

    print(len(worklinks))

    print(len(duedates))

    print(len(duetimes))

    if courses:
        return [
            [
                i['id'],
                i['name']
            ]
            for i in courses
        ]

    return None
