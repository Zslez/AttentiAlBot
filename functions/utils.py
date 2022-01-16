from urllib.parse       import quote_plus
from requests           import get

import os

import globals


token = os.environ['TOKEN']
url = f'https://api.telegram.org/bot{token}/'


__all__ = [
    'chunks',
    'copy_file_name',
    'delete',
    'download_file',
    'escape_md',
    'get_reply',
    'send',
    'send_up',
    'send_photo',
    'url',
]


def send(chat, msg, markdown = 2, preview = False):
    u = url + f'sendMessage?chat_id={chat}&text={quote_plus(msg)}'

    if markdown == 2:
        u += '&parse_mode=markdownv2'
    elif markdown == 1:
        u += '&parse_mode=markdown'

    if not preview:
        u += '&disable_web_page_preview=True'

    res = get(u).json()

    if not res['ok']:
        raise SyntaxError(f'\n---\nFailed to send message {msg}.\n{res}\n---\n')

    if chat == -1001533648966:
        globals.messages.append(res['result']['message_id'])

    return res



def send_up(update, msg, *args, **kwargs):
    send(update.message.chat.id, msg, *args, **kwargs)



def send_photo(chat, photo, msg = None, markdown = None, preview = False):
    u = url + f'sendPhoto?chat_id={chat}&photo={photo}'

    if msg:
        u += f'&caption={msg}'

    if markdown == 2:
        u += '&parse_mode=markdownv2'
    elif markdown == 1:
        u += '&parse_mode=markdown'

    if not preview:
        u += '&disable_web_page_preview=True'

    res = get(u).json()

    if not res['ok']:
        print('\n\n', res, '\n\n')

    if chat == -1001533648966:
        globals.messages.append(res['result']['message_id'])

    return res



def delete(chat_id, msg_id):
    get(url + f'deleteMessage?chat_id={chat_id}&message_id={msg_id}')



def download_file(file_id, mb = 20):
    if not (req := get(url + f'getFile?file_id={file_id}').json())['ok']:
        return

    req = req['result']

    if req['file_size'] > 1048576 * mb:
        return

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