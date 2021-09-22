# letteralmente io che aggiro i limiti del server che mi hosta il Bot, così da tenerlo attivo 24/7 per sempre

from selenium.webdriver.support             import expected_conditions as EC
from selenium.webdriver.support.ui          import WebDriverWait
from selenium                               import webdriver
from selenium.webdriver.chrome.options      import Options
from selenium.webdriver.common.by           import By

from .utils                                 import send

import heroku3
import os

import globals


__all__ = [
    'change_heroku',
    'hkey',
    'hkey2',
    'hname'
]


hkey   = None if globals.name else os.environ['HKEY']
hkey2  = None if globals.name else os.environ['HKEY2']
hname  = None if globals.name else os.environ['HNAME']
hpass  = None if globals.name else os.environ['HPASS']
hemail = None if globals.name else os.environ['HEMAIL']


def change_heroku(ctx):
    res = get_remaining_time(hemail, hpass)

    string = bool(hname.replace('attentialbot', ''))

    send(
        -1001533648966,
        f'rimangono `{res}` ore su `' +  ['attentialbot', 'attentialbot2'][string] + '`\.'
    )

    if res < 100:
        api = heroku3.from_key(hkey2)
        app = api.app(['attentialbot2', 'attentialbot'][string])
        app.process_formation()['worker'].scale(1)

        api = heroku3.from_key(hkey)
        app = api.app(hname)
        app.process_formation()['worker'].scale(0)


def get_remaining_time(email, passw):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    with webdriver.Chrome(options = options) as driver:
        driver.get('https://dashboard.heroku.com/account/billing')

        WebDriverWait(driver, 20) \
            .until(EC.presence_of_element_located((By.ID, 'onetrust-reject-all-handler'))).click()

        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_id('password').send_keys(passw)
        driver.find_element_by_xpath('//*[@id="login"]/form/button').click()

        WebDriverWait(driver, 10) \
            .until(EC.presence_of_element_located((By.XPATH, '//*[@id="mfa-later"]/button'))).click()

        a = WebDriverWait(driver, 30) \
            .until(EC.presence_of_element_located((By.XPATH, '//*[@id="ember31"]/table/thead/th[1]/div/span[2]')))

        return float(a.text.split()[0])