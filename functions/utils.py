from urllib.parse       import quote_plus
from telegram.update    import Update
from requests           import get

import globals
import os


token = os.environ['TOKEN']
url = f'https://api.telegram.org/bot{token}/'


__all__ = [
    'chunks',
    'copy_file_name',
    'delete',
    'download_file',
    'escape_md',
    'get_reply',
    'pin',
    'reply',
    'reply_callback',
    'send',
    'url',
]


def send(chat, msg, markdown = 2, preview = False):
    try:
        u = url + f'sendMessage?chat_id={chat}&text={quote_plus(msg)}'

        if markdown == 2:
            u += '&parse_mode=markdownv2'
        elif markdown == 1:
            u += '&parse_mode=markdown'

        if not preview:
            u += '&disable_web_page_preview=True'

        msg = get(u).json()

        if not msg['ok']:
            raise ZeroDivisionError

        return msg
    except ZeroDivisionError:
        u = url + f'sendMessage?chat_id={chat}&text={quote_plus(escape_md(msg))}'

        if markdown == 2:
            u += '&parse_mode=markdownv2'
        elif markdown == 1:
            u += '&parse_mode=markdown'

        if not preview:
            u += '&disable_web_page_preview=True'

        msg = get(u).json()

        return msg


def reply(update: Update, msg, markdown = 0, preview = False):
    if not markdown:
        update.message.reply_text(msg.strip(), disable_web_page_preview = not preview)
    else:
        if markdown == 1:
            update.message.reply_markdown(msg.strip(), disable_web_page_preview = not preview)
        else:
            update.message.reply_markdown_v2(msg.strip(), disable_web_page_preview = not preview)



def reply_callback(update: Update, msg):
    update.callback_query.message.reply_markdown(msg.strip(), disable_web_page_preview = True)


def delete(chat_id, msg_id):
    get(url + f'deleteMessage?chat_id={chat_id}&message_id={msg_id}')


def pin(chat_id, msg_id):
    get(url + f'pinChatMessage?chat_id={chat_id}&message_id={msg_id}')





def download_file(file_id):
    req = get(url + f'getFile?file_id={file_id}').json()['result']

    if req['file_size'] > 52428800:
        return None

    req = req['file_path']

    with open(req.split('/')[-1], 'wb') as f:
        f.write(get(f'https://api.telegram.org/file/bot{token}/{req}', allow_redirects = True).content)
        return req.split('/')[-1]


def get_reply(update):
    reply_msg = update.to_dict()['message']['reply_to_message']
    msg_id = reply_msg['message_id']

    try:
        doc = reply_msg['audio']

        try:
            file_name = doc['file_name']
        except:
            file_name = doc['file_unique_id']
    except:
        try:
            doc = reply_msg['voice']
            file_name = doc['file_unique_id'] + '.ogg'
        except:
            try:
                doc = reply_msg['video']

                try:
                    file_name = doc['file_name']
                except:
                    file_name = doc['file_unique_id'] + '.mp4'
            except:
                doc = reply_msg['document']

                try:
                    file_name = doc['file_name']
                except:
                    file_name = doc['file_unique_id']

    file_id = doc['file_id']
    return msg_id, file_name, file_id


def copy_file_name(file_name):
    return '.'.join(file_name.split('.')[:-1]) + '_copy.' + file_name.split('.')[-1]



def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def escape_md(text):
	chars = '_-~' + '*+=>' + '({[]})' + '|!#`.'

	for i in chars:
		text = text.replace(i, f'\\{i}')

	return text