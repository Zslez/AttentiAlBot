from simple_image_download.simple_image_download    import simple_image_download
from os                                             import listdir, remove, rename
from urlextract                                     import URLExtract
from shutil                                         import rmtree
from subprocess                                     import run

from .utils                                         import *


__all__ = [
    'image',
    'earrape',
    'to_audio',
    'to_video',
    'cut_audio_video',
    'reverse_audio_video',
    'speed_audio_video',
    'speed_pitch_audio_video'
]


exts = (
    'webm', 'mkv', 'flv', 'mp4', 'vob', 'ogg', 'ogv', 'drc',
    'gif', 'avi', 'mov', 'm4p', 'm4v', 'mpg', 'mpeg', 'mpv'
)


extract = URLExtract().find_urls
download = simple_image_download().download



def image(update, ctx):
    query = ' '.join(ctx.args)
    q = '_'.join(ctx.args)

    download(query, 1)

    with open(f'simple_images/{q}/' + listdir(f'simple_images/{q}')[0], 'rb') as f:
        ctx.bot.send_photo(ctx._chat_id_and_data[0], photo = f)

    rmtree(f'simple_images/{q}')



def earrape(update, ctx):
    if len(ctx.args) > 0:
        value = 5 * float(ctx.args[0])

        if value > 50:
            value = 50
        elif value < -50:
            value = -50
    else:
        value = 20

    if value == 0:
        return

    msg_id, file_name, file_id = get_reply(update)

    if file_name.count('.') == 0:
        return

    new_ = download_file(file_id)
    
    if new_.split('.')[-1] == 'oga':
        run(f'ffmpeg -i "{new_}" -c:a libopus -b:a 192k -af "volume={value}dB" "{file_name}"', shell = True)
    else:
        ext = new_.split('.')[-1].lower()

        if ext in exts and 'video' in run(f'ffprobe -loglevel error -show_entries stream=codec_type -of csv=p=0 "{new_}"',
                shell = True, stdout = -1).stdout.decode():
            file_name = '.'.join(file_name.split('.')[:-1]) + '.mp3'

        run(f'ffmpeg -i "{new_}" -vn -ar 44100 -ac 2 -b:a 192k -af "volume={value}dB" "{file_name}"', shell = True)

    with open(file_name, 'rb') as f:
        update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    try:
        remove(new_)
        remove(file_name)
    except:
        pass



def to_audio(update, ctx):
    msg_id = None

    if len(ctx.args) == 0:
        m = update.to_dict()['message']

        if 'reply_to_message' in m:
            reply_msg = m['reply_to_message']
            msg_id = reply_msg['message_id']

            if 'text' in reply_msg:
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
                video_to_audio(update)
                return
        else:
            return
    else:
        url = ctx.args[0]

    run(f'youtube-dl -o "%(title)s.%(ext)s" --extract-audio --audio-format mp3 {url}', shell = True)

    a = run(
        f'youtube-dl --get-filename -o "%(title)s.%(ext)s" {url}',
        shell = True,
        stdout = -1
    ).stdout.decode().strip()

    base = '.'.join(a.split('.')[:-1]).split('\\')[-1]

    with open(base + '.mp3', 'rb') as f:
        update.message.reply_audio(
            f,
            base + '.mp3',
            reply_to_message_id = msg_id
        )

    remove(base + '.mp3')



def to_video(update, ctx):
    msg_id = None

    if len(ctx.args) == 0:
        m = update.to_dict()['message']

        if 'reply_to_message' in m:
            reply_msg = m['reply_to_message']
            msg_id = reply_msg['message_id']

            if 'text' in reply_msg:
                url = extract(reply_msg['text'])[0]
            else:
                return
        else:
            return
    else:
        url = ctx.args[0]

    run(f'youtube-dl -o "%(title)s.%(ext)s" -f best {url}', shell = True)

    a = run(
        f'youtube-dl --get-filename -o "%(title)s.%(ext)s" -f best {url}',
        shell = True,
        stdout = -1
    ).stdout.decode().strip()

    a = a.split('\\')[-1]

    with open(a, 'rb') as f:
        update.message.reply_video(f, a, reply_to_message_id = msg_id)

    remove(a)



def video_to_audio(update):
    msg_id, file_name, file_id = get_reply(update)

    if file_name.count('.') == 0:
        return

    file_name = '.'.join(file_name.split('.')[:-1]) + '.mp3'
    rename(download_file(file_id), file_name)

    with open(file_name, 'rb') as f:
        update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    remove(file_name)



def cut_audio_video(update, ctx):
    if len(ctx.args) == 0 or len(ctx.args) == 1:
        return

    sec1, sec2 = float(ctx.args[0]), float(ctx.args[1])

    msg_id, file_name, file_id = get_reply(update)

    if file_name.count('.') == 0:
        return

    new_ = download_file(file_id)
    ext = new_.split('.')[-1].lower()

    if ext in exts and 'video' in run(f'ffprobe -loglevel error -show_entries stream=codec_type -of csv=p=0 "{new_}"',
            shell = True, stdout = -1).stdout.decode():

        w, h = run(f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "{new_}"',
            shell = True, stdout = -1).stdout.decode().split('x')

        run(f'ffmpeg -ss {int(sec1 // 3600)}:{int((sec1 % 3600) // 60)}:{sec1 % 60} -i "{new_}"' \
            f' -to {int(sec2 // 3600)}:{int((sec2 % 3600) // 60)}:{sec2 % 60} -c copy "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
    else:
        run(f'ffmpeg -ss {int(sec1 // 3600)}:{int((sec1 % 3600) // 60)}:{sec1 % 60} -i "{new_}"' \
            f' -to {int(sec2 // 3600)}:{int((sec2 % 3600) // 60)}:{sec2 % 60} -c copy "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    try:
        remove(new_)
        remove(file_name)
    except:
        pass



def reverse_audio_video(update, ctx):
    msg_id, file_name, file_id = get_reply(update)

    if file_name.count('.') == 0:
        return

    new_ = download_file(file_id)
    ext = new_.split('.')[-1].lower()

    if ext in exts and 'video' in run(f'ffprobe -loglevel error -show_entries stream=codec_type -of csv=p=0 "{new_}"',
            shell = True, stdout = -1).stdout.decode():

        if float(run(f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{new_}"',
            shell = True, stdout = -1).stdout.decode()) > 8:
            update.message.reply_markdown('Al momento non è possibile fare il reverse di video troppo lunghi ' \
                'perché richede più memoria di quella che mi viene concessa dal server. 😔')

            try:
                remove(new_)
                remove(file_name)
            except:
                pass

            return

        w, h = run(f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "{new_}"',
            shell = True, stdout = -1).stdout.decode().split('x')

        run(F'ffmpeg -i "{new_}" -vf reverse -af areverse "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
    else:
        if new_.split('.')[-1] == 'oga':
            run(F'ffmpeg -i "{new_}" -c:a libopus -b:a 192k -af areverse "{file_name}"', shell = True, check = True)
        else:
            run(F'ffmpeg -i "{new_}" -b:a 192k -af areverse "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    try:
        remove(new_)
        remove(file_name)
    except:
        pass



def speed_audio_video(update, ctx):
    if len(ctx.args) > 0:
        value = float(ctx.args[0])

        if value > 100:
            value = 100
        elif value < 0.5:
            value = 0.5
    else:
        return

    msg_id, file_name, file_id = get_reply(update)

    if file_name.count('.') == 0:
        return

    new_ = download_file(file_id)
    ext = new_.split('.')[-1].lower()

    if ext in exts and 'video' in run(f'ffprobe -loglevel error -show_entries stream=codec_type -of csv=p=0 "{new_}"',
            shell = True, stdout = -1).stdout.decode():

        w, h = run(f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "{new_}"',
            shell = True, stdout = -1).stdout.decode().split('x')

        
        run(F'ffmpeg -i "{new_}" -af atempo={value} -filter:v "setpts=PTS/{value}" "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
    else:
        if new_.split('.')[-1] == 'oga':
            run(F'ffmpeg -i "{new_}" -c:a libopus -af atempo={value} "{file_name}"', shell = True)
        else:
            run(F'ffmpeg -i "{new_}" -af atempo={value} "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    try:
        remove(new_)
        remove(file_name)
    except:
        pass



def speed_pitch_audio_video(update, ctx):
    if len(ctx.args) > 0:
        value = float(ctx.args[0])

        if value > 100:
            value = 100
        elif value < 0.5:
            value = 0.5
    else:
        return

    msg_id, file_name, file_id = get_reply(update)

    if file_name.count('.') == 0:
        return

    new_ = download_file(file_id)
    ext = new_.split('.')[-1].lower()

    if ext in exts and 'video' in run(f'ffprobe -loglevel error -show_entries stream=codec_type -of csv=p=0 "{new_}"',
            shell = True, stdout = -1).stdout.decode():

        w, h = run(f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0:s=x "{new_}"',
            shell = True, stdout = -1).stdout.decode().split('x')

        
        run(F'ffmpeg -i "{new_}" -af asetrate=44100*{value},aresample=44100 -filter:v "setpts=PTS/{value}" "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_video(f, file_name, reply_to_message_id = msg_id, width = w, height = h)
    else:
        if new_.split('.')[-1] == 'oga':
            run(F'ffmpeg -i "{new_}" -c:a libopus -af asetrate=44100*{value},aresample=44100 "{file_name}"', shell = True)
        else:
            run(F'ffmpeg -i "{new_}" -af asetrate=44100*{value},aresample=44100 "{file_name}"', shell = True)

        with open(file_name, 'rb') as f:
            update.message.reply_audio(f, file_name, reply_to_message_id = msg_id)

    try:
        remove(new_)
        remove(file_name)
    except:
        pass
