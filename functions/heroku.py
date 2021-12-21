# letteralmente io che aggiro i limiti del server che mi hosta il Bot, così da tenerlo attivo 24/7 per sempre

from selenium.webdriver.support             import expected_conditions as EC
from selenium.webdriver.support.ui          import WebDriverWait
from selenium                               import webdriver
from selenium.webdriver.chrome.options      import Options
from selenium.webdriver.common.by           import By

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
        wait10 = WebDriverWait(driver, 10).until

        wait10(EC.presence_of_element_located((By.ID, 'onetrust-reject-all-handler'))).click()

        driver.find_element_by_id('email').send_keys(email)
        driver.find_element_by_id('password').send_keys(passw)
        driver.find_element_by_xpath('//*[@id="login"]/form/button').click()

        wait10(EC.presence_of_element_located((By.XPATH, '//*[@id="mfa-later"]/button'))).click()
        wait10(EC.presence_of_element_located((By.CLASS_NAME, 'account-quota-usage')))

        result = driver.find_element_by_class_name('account-quota-usage').find_element_by_class_name('gray')

        return float(result.text.split()[0])