from os                                             import listdir, remove, rename
from subprocess                                     import run as run2
from simple_image_download.simple_image_download    import Downloader
from urlextract                                     import URLExtract
from shutil                                         import rmtree

from .utils                                         import *

import os
import re



__all__ = [
    'cut_audio_video',
    'earrape',
    'gif',
    'image',
    'loop_audio_video',
    'reverse_audio_video',
    'speed_audio_video',
    'speed_pitch_audio_video',
    'to_audio',
    'to_video'
]



exts = (
    'webm', 'mkv', 'flv', 'mp4', 'vob', 'ogg', 'ogv', 'drc',
    'gif', 'avi', 'mov', 'm4p', 'm4v', 'mpg', 'mpeg', 'mpv'
)


limit = 10


with open('bad.txt', encoding = 'utf-8') as f:
    bad = [r'.*' + i + r'.*' if '^' not in i else i for i in f.read().split('\n')]


extract = URLExtract().find_urls



def run(cmd):
    return run2(cmd, shell = True, check = True, stdout = -1)



def get_value(ctx, max_v, min_v, default = None, null = None):
    if len(ctx.args) > 0:
        value = float(ctx.args[0])

        if value > max_v:
            value = max_v
        elif value < min_v:
            value = min_v
    else:
        value = default

    if value == null:
        return

    return value



def is_video(ext, video):
    cmd = run(f'ffprobe -loglevel error -show_entries stream=codec_type -of csv=p=0 "{video}"')
    return ext in exts and 'video' in cmd.stdout.decode()



def get_size(video):
    cmd = f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "{video}"'
    return run(cmd).stdout.decode().split('x')



def check_file(update, file_name, file_id, mb = limit):
    if file_name.count('.') == 0:
        return

    if mb > limit:
        mb = limit

    new = download_file(file_id, mb)

    if new == None:
        send_up(update, 'Il file è troppo pesante.')
        return

    return file_name, new



def ffmpeg(inp, out, cmd_after, oga = '', cmd_before = ''):
    if inp.split('.')[-1] == 'oga':
        oga = '-c:a libopus'

    return run(f'ffmpeg {cmd_before} -i "{inp}" {oga} {cmd_after} "{out}"')




## ==================================================== ##




def is_bad(query):
    for i in bad:
        if re.match(i, query):
            return True

    return False



def image(update, ctx, gif = False):
    args = ctx.args
    query = '_'.join(args)

    if is_bad(query):
        update.message.delete()
        return

    download = Downloader()
    download._extensions = [{'.jpg', '.jpeg'}, {'.gif'}][gif]
    download = download.download

    download(query, limit = 1)

    folder = f'simple_images/{query}'

    if len(listdir(folder)) == 0:
        send_up(update, 'nessuna ' + ['immagine', 'gif'][gif] + f' trovata per \'' + ' '.join(args) + '\'')
        return

    chat_id = ctx._chat_id_and_data[0]

    with open(folder + '/' + listdir(folder)[0], 'rb') as f:
        ctx.bot.send_animation(chat_id, animation = f) if gif else ctx.bot.send_photo(chat_id, photo = f)

    rmtree(folder)



def gif(update, ctx):
    return image(update, ctx, True)



def earrape(update, ctx):
    if (value := get_value(ctx, 10, -10, 4, 0)) == None:
        return

    value *= 5

    msg_id, file_name, file_id = get_reply(update)

    if not (check := check_file(update, file_name, file_id)):
        return

    file_name, new = check
    ext = new.split('.')[-1].lower()

    if is_video(ext, new):
        file_name = '.'.join(file_name.split('.')[:-1]) + '.mp3'

    ffmpeg(new, file_name, f'-b:a 192k -af "volume={value}dB"', '-vn -ar 44100 -ac 2')

    with open(file_name, 'rb') as f:
        try:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)
        except:
            send_up(update, 'Il file è troppo pesante.')

    remove(new)
    remove(file_name)



def to_audio(update, ctx):
    msg_id = None

    if len(ctx.args) == 0:
        m = update.to_dict()['message']

        if not 'reply_to_message' in m:
            return

        reply_msg = m['reply_to_message']
        msg_id = reply_msg['message_id']

        if 'text' not in reply_msg:
            video_to_audio(update)
            return

        url = extract(reply_msg['text'])

        if url:
            url = url[0]
        else:
            if 'entities' in reply_msg:
                for i in reply_msg['entities']:
                    if 'url' in i:
                        url = i['url']
                        break

        if not url:
            return
    else:
        if not (url := extract(' '.join(ctx.args))):
            return

        url = url[0]

    title = '"%(title)s.%(ext)s"'

    run(f'youtube-dl --max-filesize {limit}m -o {title} --extract-audio --audio-format mp3 {url}')
    name = run(f'youtube-dl --get-filename -o {title} {url}').stdout.decode().strip()
    name = '.'.join(name.split('.')[:-1]).split('\\')[-1] + '.mp3'

    if not os.path.exists(name):
        send_up(update, 'L\'audio è troppo pesante.')
        return

    with open(name, 'rb') as f:
        update.message.reply_audio(f, name, reply_to_message_id = msg_id)

    remove(name)



def to_video(update, ctx):
    msg_id = None

    if len(ctx.args) == 0:
        m = update.to_dict()['message']

        if 'reply_to_message' not in m:
            return

        reply_msg = m['reply_to_message']
        msg_id = reply_msg['message_id']

        if 'text' not in reply_msg:
            return

        url = extract(reply_msg['text'])
    else:
        url = extract(' '.join(ctx.args))

    if not url:
        return

    url = url[0]

    run(f'youtube-dl --max-filesize {limit}m -o "%(title)s.%(ext)s" -f best {url}')
    name = run(f'youtube-dl --get-filename -o "%(title)s.%(ext)s" {url}').stdout.decode().strip()
    name = name.split('\\')[-1]

    if not os.path.exists(name):
        send_up(update, 'Il video è troppo pesante.')
        return

    with open(name, 'rb') as f:
        update.message.reply_video(f, name, reply_to_message_id = msg_id)

    remove(name)



def video_to_audio(update):
    msg_id, file_name, file_id = get_reply(update)
    file_name = '.'.join(file_name.split('.')[:-1]) + '.mp3'

    if not (check := check_file(update, file_name, file_id)):
        return

    file_name, new = check

    rename(new, file_name)

    with open(file_name, 'rb') as f:
        update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    remove(file_name)



def cut_audio_video(update, ctx):
    if len(ctx.args) == 0 or len(ctx.args) == 1:
        return

    sec1, sec2 = float(ctx.args[0]), float(ctx.args[1])

    msg_id, file_name, file_id = get_reply(update)

    if not (check := check_file(update, file_name, file_id)):
        return

    file_name, new = check
    ext = new.split('.')[-1].lower()
    video = is_video(ext, new)

    if video:
        w, h = get_size(new)

    ffmpeg(
        new,
        file_name,
        f'-to {int(sec2 // 3600)}:{int((sec2 % 3600) // 60)}:{sec2 % 60} -c copy',
        '',
        f'-ss {int(sec1 // 3600)}:{int((sec1 % 3600) // 60)}:{sec1 % 60}'
    )

    with open(file_name, 'rb') as f:
        if video:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
        else:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    remove(new)
    remove(file_name)



def reverse_audio_video(update, ctx):
    msg_id, file_name, file_id = get_reply(update)

    if not (check := check_file(update, file_name, file_id)):
        return

    file_name, new = check
    ext = new.split('.')[-1].lower()

    if is_video(ext, new):
        cmd = 'ffprobe -v error -show_entries format=duration ' \
            f'-of default=noprint_wrappers=1:nokey=1 "{new}"'

        if float(run(cmd).stdout.decode()) > 8:
            send_up(update, 'Video troppo lungo per il reverse 😔')

            remove(new)
            remove(file_name)

            return

        w, h = get_size(new)

        ffmpeg(new, file_name, '-vf reverse -af areverse')

        with open(file_name, 'rb') as f:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
    else:
        ffmpeg(new, file_name, '-b:a 192k -af areverse')

        with open(file_name, 'rb') as f:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    remove(new)
    remove(file_name)



def speed_audio_video(update, ctx):
    value = get_value(ctx, 10, 0.5, None, 1)

    msg_id, file_name, file_id = get_reply(update)

    if not (check := check_file(update, file_name, file_id)):
        return

    file_name, new = check
    ext = new.split('.')[-1].lower()

    if is_video(ext, new):
        w, h = get_size(new)

        ffmpeg(new, file_name, f'-af atempo={value} -filter:v "setpts=PTS/{value}"')

        with open(file_name, 'rb') as f:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
    else:
        ffmpeg(new, file_name, f'-af atempo={value}')

        with open(file_name, 'rb') as f:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    remove(new)
    remove(file_name)



def speed_pitch_audio_video(update, ctx):
    value = get_value(ctx, 10, 0.5, None, 1)
    real = value / .9188

    msg_id, file_name, file_id = get_reply(update)

    if not (check := check_file(update, file_name, file_id)):
        return

    file_name, new = check
    ext = new.split('.')[-1].lower()

    if is_video(ext, new):
        w, h = get_size(new)

        ffmpeg(new, file_name, f'-af asetrate=44100*{real},aresample=44100 -filter:v "setpts=PTS/{real}"')

        with open(file_name, 'rb') as f:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
    else:
        ffmpeg(new, file_name, f'-af asetrate=44100*{real},aresample=44100')

        with open(file_name, 'rb') as f:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    remove(new)
    remove(file_name)



def loop_audio_video(update, ctx):
    value = int(get_value(ctx, 10, 2, 2)) - 1

    msg_id, file_name, file_id = get_reply(update)

    if not (check := check_file(update, file_name, file_id, limit / (value + 1) - 0.005)):
        return

    file_name, new = check
    ext = new.split('.')[-1].lower()

    ffmpeg(new, file_name, '', '', f'-stream_loop {value}')

    with open(file_name, 'rb') as f:
        if is_video(ext, new):
            w, h = get_size(new)
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
        else:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    remove(new)
    remove(file_name)
