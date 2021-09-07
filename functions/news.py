from selenium.webdriver.support.expected_conditions         import presence_of_element_located as presence
from selenium.webdriver                                     import DesiredCapabilities
from bs4                                                    import BeautifulSoup as bs
from selenium.webdriver.support.ui                          import WebDriverWait
from selenium                                               import webdriver
from selenium.webdriver.chrome.options                      import Options
from json                                                   import loads
from time                                                   import sleep
from requests                                               import post
from selenium.webdriver.common.by                           import By

from .utils import send, escape_md

import heroku3
import os

import globals


# VARIABLES

hkey  = None if globals.name else os.environ['HKEY']
hname = None if globals.name else os.environ['HNAME']

news_channel = -1001568629792

uname = None if globals.name else os.environ['USERNAME']
passw = None if globals.name else os.environ['PASSWORD']



# per accorciare gli URL con Bitly

bittoken = os.environ['BITTOKEN']

header = {'Authorization': 'Bearer ' + bittoken, 'Content-Type': 'application/json'}

capabilities = DesiredCapabilities.CHROME
capabilities["goog:loggingPrefs"] = {"performance": "ALL"}


# opzioni per Chrome

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')


__all__ = [
    'get_news'
]



def get_news(ctx):
    n = 1
    hnews = os.environ['NEWS']

    with webdriver.Chrome(options = options, desired_capabilities = capabilities) as dri:
        dri.get('https://www.portaleargo.it/')

        wait_5 = WebDriverWait(dri, 5)
        xpath = By.XPATH

        wait_5.until(presence((xpath, '/html/body/div[5]/div/div/div/span[1]/a'))).click()
        WebDriverWait(dri, 10).until(presence((xpath, '//*[@id="codiceScuola"]'))).send_keys('SS16383')

        dri.find_element_by_xpath('//*[@id="username"]').send_keys(uname)
        dri.find_element_by_xpath('//*[@id="password"]').send_keys(passw)
        dri.find_element_by_xpath('//*[@id="accediBtn"]').click()

        WebDriverWait(dri, 30).until(presence((xpath, '//*[@id="_idJsp27"]/div[1]/div[1]'))).click()
        wait_5.until(presence((xpath, '//*[@id="bacheca"]/table/tbody/tr[3]/td[2]/div/div[3]'))).click()
        wait_5.until(presence((xpath, '//*[@id="sheet-bacheca:tree:scuola"]/div'))).click()

        table = wait_5.until(presence((xpath, f'//*[@id="panel-messaggiBacheca:form"]/table/tbody/fieldset[{n}]/tr/td[2]/table')))
        bstable = bs(table.get_attribute('innerHTML'), features = 'html.parser')

        content = [[j.strip() for j in i.text.split(': ')] for i in bstable.find_all('tr')]
        ogg = ''
        msg = ''
        files = {}
        urls = []
        pv = False

        for i in content:
            if i[0] == 'Oggetto':
                ogg = f'NUOVA *{i[1][:-1].upper()}E* DALLA SCUOLA\n\n'
            elif i[0] == 'Messaggio':
                msg = i[1] + '\n\n\n'

                save = ''.join([x[0] for x in msg.split()])

                if save == hnews:
                    print(f'Il Messaggio è lo stesso:\n{msg}')
                    return
            elif i[0] == 'File':
                files[i[1]] = None
            elif i[0] == 'Url':
                urls.append(i[1])
            elif i[0] == 'Presa Visione':
                pv = True

        c = 0
        for j in [table.find_element_by_xpath(f'.//tr[{i + 1}]/td[2]/a') for i in range(len(bstable.find_all('tr')))
            if table.find_element_by_xpath(f'.//tr[{i + 1}]/td[1]').text == 'File:']:
            j.click()
            sleep(2.5)

            try:
                file = loads(dri.get_log('performance')[-1]['message'])['message']['params']['url']
            except KeyError:
                file = 'https://youtu.be/kw1kc2U6NmA'

            data = {
                "long_url": file,
                "group_guid": 'Bl7pg5tTZil'
            }

            files[list(files)[c]] = post('https://api-ssl.bitly.com/v4/shorten', json = data, headers = header).json()["link"]
            c += 1

        if len(files) == 0:
            files = {'circ_allegato.pdf': 'https://youtu.be/kw1kc2U6NmA'}

        files = 'File allegati:\n  ‣ ' + '\n  ‣ '.join([f'[{escape_md(k)}]({v})' for k, v in files.items()])

        if len(urls) > 0:
            urls = '\n\n\nUrl allegati:\n  ‣ ' + '\n  ‣ '.join(urls)
        else:
            urls = ''

        if pv:
            pv = '\n\n\nNOTA: c\'è da confermare presa visione.'
        else:
            pv = ''

        res = ogg + escape_md(msg) + files + escape_md(urls) + escape_md(pv)

    send(news_channel, res)

    app = heroku3.from_key(hkey).app(hname)
    config = app.config()
    config['NEWS'] = save