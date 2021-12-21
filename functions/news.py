from selenium.webdriver.support.expected_conditions         import presence_of_element_located as presence
from selenium.webdriver                                     import DesiredCapabilities
from bs4                                                    import BeautifulSoup as bs
from selenium.webdriver.support.ui                          import WebDriverWait
from selenium                                               import webdriver
from selenium.webdriver.chrome.options                      import Options
from shutil                                                 import rmtree
from json                                                   import loads
from time                                                   import sleep
from requests                                               import get
from selenium.webdriver.common.by                           import By

from .utils                                                 import send_up, send, escape_md, send_photo

import os

import globals



# VARIABLES

hkey    = None if globals.name else os.environ['HKEY']
hname   = None if globals.name else os.environ['HNAME']

uname   = None if globals.name else os.environ['USERNAME']
passw   = None if globals.name else os.environ['PASSWORD']

news_channel = -1001568629792



# opzioni per Chrome


capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}


options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')


__all__ = [
    'get_news',
    'get_news_command',
    'get_news_job'
]



def get_news(ctx):
    with webdriver.Chrome(options = options, desired_capabilities = capabilities) as dri:
        dri.get('http://www.ss16383.scuolanext.info/')

        wait_10 = WebDriverWait(dri, 10)
        xpath = By.XPATH

        wait_10.until(presence((xpath, '//*[@id="username"]'))).send_keys(uname)
        dri.find_element_by_xpath('//*[@id="password"]').send_keys(passw)
        dri.find_element_by_xpath('//*[@id="accediBtn"]').click()

        wait_10.until(presence((xpath, '//*[@id="_idJsp27"]/div[1]/div[1]'))).click()
        wait_10.until(presence((xpath, '//*[@id="bacheca"]/table/tbody/tr[3]/td[2]/div/div[3]'))).click()
        wait_10.until(presence((xpath, '//*[@id="sheet-bacheca:tree:scuola"]/div'))).click()

        table = wait_10.until(
            presence(
                (
                    xpath,
                    f'//*[@id="panel-messaggiBacheca:form"]/table/tbody/fieldset[1]/tr/td[2]/table'
                )
            )
        )

        bstable = bs(table.get_attribute('innerHTML'), 'html.parser')

        content = [[j.strip() for j in i.text.split(': ')] for i in bstable.find_all('tr')]
        files = []
        urls = []
        pv = False

        for i in content:
            if i[0] == 'Oggetto':
                ogg = f'NUOVA *{i[1][:-1].upper()}E* SULLA BACHECA\n\n'
            elif i[0] == 'Messaggio':
                msg = i[1] + '\n\n'
                save = ''.join([x[0] for x in msg.split()])

                if save == globals.hnews:
                    return
            elif i[0] == 'File':
                files.append(i[1])
            elif i[0] == 'Url':
                urls.append(i[1])
            elif i[0] == 'Presa Visione':
                pv = True

        c = 0

        for j in [
                table.find_element_by_xpath(f'.//tr[{i + 1}]/td[2]/a')
                for i in range(len(bstable.find_all('tr')))
                if table.find_element_by_xpath(f'.//tr[{i + 1}]/td[1]').text == 'File:'
            ]:
            j.click()
            sleep(1.8)

            try:
                file = loads(dri.get_log('performance')[-1]['message'])['message']['params']['url']
            except KeyError:
                file = 'https://youtu.be/kw1kc2U6NmA'

            os.mkdir('allegati')

            with open(f'allegati/' + list(files)[c], 'wb') as f:
                f.write(get(file).content)

            c += 1

        if len(urls) > 0:
            urls = '*URL ALLEGATI:*\n  ‣ ' + '\n  ‣ '.join(urls)
        else:
            urls = ''

        if pv:
            pv = '\nNOTA: c\'è da confermare presa visione.'
        else:
            pv = ''

        res = ogg + escape_md(msg + urls + pv)

    globals.hnews = save

    send(news_channel, res)

    for i in os.listdir('allegati'):
        with open(f'allegati/{i}', 'rb') as f:
            ctx.bot.send_document(chat_id = news_channel, filename = i, document = f)

    rmtree('allegati')




def format_url(url):
    if url.startswith('/'):
        return 'https://www.liceopeanomonterotondo.edu.it/' + url[1:]
    elif not url.startswith('http'):
        return 'https://www.liceopeanomonterotondo.edu.it/' + url

    return url




def get_news_website(num, last = None):
    url = 'https://www.liceopeanomonterotondo.edu.it/homepage'
    images = None

    if num > 11:
        url += f'?page={(num - 1) // 11}'


    # OTTIENE LA PAGINA DEL SITO DELLA SCUOLA

    req = bs(get(url).content, 'html.parser')

    last_news = req.find('div', {'class': f'views-row-{(num - 1) % 11 + 1}'}) \
        .find_all('span', {'class': 'field-content'})

    news = last_news[0].text
    type = last_news[1].text.strip().split(' - ')[1]


    # OTTIENE L'URL DELL'ARTICOLO

    last_news_url = format_url(last_news[0].find('a')['href'])

    if last and last_news_url == globals.lnu:
        return
    elif last:
        globals.lnu = last_news_url
        globals.max_news += 1


    # OTTIENE LA PAGINA DELL'ARTICOLO DALL'URL APPENA ESTRATTO

    req2 = bs(get(last_news_url).content, 'html.parser')


    # RACCOGLIE LE ULTIME INFORMAZIONI E LE ORGANIZZA PER INVIARLE

    if last:
        num = 'NUOVO POST'
    elif num == 1:
        num = 'ULTIMO POST'
    elif num == globals.max_news:
        num = 'PRIMO POST'
    else:
        num = f'{num}° POST PIÙ RECENTE'

    title = f'[*{num} SUL SITO DELLA SCUOLA*]({last_news_url})'

    fields = req2.find_all('div', {'class': 'field-item even'})

    fields_text = [i for i in fields if not i.text.strip().startswith('Allegat')]
    attachments = [i for i in fields if i.text.strip().startswith('Allegat')]


    # ESTRAE IL TESTO DEL POST

    text = ''

    for i in fields_text:
        if type == 'Circolare':
            text += '\n'.join(
                [
                    escape_md(j.text) for j in i.find_all('p')
                    if not j.has_attr('class') and not j.text.strip().lower().startswith('oggetto')
                ]
            ).strip() + '\n'
        else:
            temptext = [
                '[' + escape_md(j.text) + '](' + format_url(j['href']) + ')'
                if j.has_attr('href') else escape_md(j.text.strip())
                for j in i.find_all(['p', 'a'])
                if j.parent.name != 'a' and not j.find('a') and j.text.strip()
            ]

            images = [j.strip().replace('[](', '')[:-1] for j in temptext if '[]' in i]
            images_2 = [format_url(j['src']) for j in i.find_all('img')]

            images += [i for i in images_2 if i not in images]

            text += '\n'.join([i for i in temptext if '[]' not in i]).strip() + '\n'

    if text.strip():
        text = '\n*TESTO:*\n' + text.strip()


    # ESTRAE TUTTI GLI ALLEGATI SE CE NE SONO

    if attachments:
        att_text = '\n*ALLEGATI:*\n'

        for i in attachments[0].find_all('a'):
            att_text += ' ‣ [' + escape_md(i.text) + '](' + i['href'] + ')\n'
    else:
        att_text = ''

    return f'{title}\n\n*OGGETTO:*\n{escape_md(news)}\n{text}\n{att_text}', images




def get_news_command(update, ctx):
    num = min(int(ctx.args[0]), globals.max_news) if len(ctx.args) > 0 else 1

    text, images = get_news_website(num)

    send_up(update, text)

    if images:
        for i in images:
            update.message.reply_photo(i)




def get_news_job(ctx):
    result = get_news_website(1, True)

    if result:
        text, images = result

        send(news_channel, text)

        if images:
            for i in images:
                send_photo(news_channel, i)