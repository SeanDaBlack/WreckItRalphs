import requests
import functools
import os
import random
import re
import sys
import time
import argparse
from selenium.webdriver.chrome import options

from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from WreckItRalphs.constants.parser import CLOUD_DISABLED, CLOUD_ENABLED
from resume_faker import make_resume
from pdf2image import convert_from_path

from webdriver_manager.chrome import ChromeDriverManager
os.environ['WDM_LOG_LEVEL'] = '0'

from constants.common import *
from constants.fileNames import *
from constants.classNames import *
from constants.elementIds import *
from constants.email import *
from constants.location import *
from constants.parser import *
from constants.urls import *
from constants.xPaths import *
from constants.areaCodes import *

os.environ["PATH"] += ":/usr/local/bin" # Adds /usr/local/bin to my path which is where my ffmpeg is stored

global appCount
fake = Faker()
from datetime import date

today = date.today()
# Add printf: print with flush by default. This is for python 2 support.
# https://stackoverflow.com/questions/230751/how-can-i-flush-the-output-of-the-print-function-unbuffer-python-output#:~:text=Changing%20the%20default%20in%20one%20module%20to%20flush%3DTrue
printf = functools.partial(print, flush=True)

#Option parsing
parser = argparse.ArgumentParser(SCRIPT_DESCRIPTION,epilog=EPILOG)
parser.add_argument('--cloud',action='store_true',default=CLOUD_DISABLED,required=False,help=CLOUD_DESCRIPTION,dest='cloud')
parser.add_argument('--mailtm',action='store_true',default=MAILTM_DISABLED,required=False,help=MAILTM_DESCRIPTION,dest='mailtm')
args = parser.parse_args()
# END TEST

def start_driver(random_city):
    options = Options()
    if (args.cloud == CLOUD_ENABLED):
        #options.add_argument(f"user-agent={USER_AGENT}")
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        #options.add_argument('disable-blink-features=AutomationControlled')
        #options.headless = True
        driver = webdriver.Chrome('chromedriver',options=options)
        driver = webdriver.Chrome(ChromeDriverManager().install(),options=options)
        #driver.set_window_size(1440, 900)
    elif (args.cloud == CLOUD_DISABLED):
        driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(CITIES_TO_URLS[random_city])
    driver.implicitly_wait(10)
    #time.sleep(15)
    #WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, CREATE_AN_ACCOUNT_BUTTON)))
    driver.find_element_by_xpath(APPLY_NOW_BUTTON_1).click()
    #driver.find_element_by_xpath(APPLY_NOW_BUTTON_2).click()
    driver.find_element_by_xpath(CREATE_AN_ACCOUNT_BUTTON).click()
    return driver


def generate_account(driver, fake_identity):
    # make fake account info and fill

    email = fake.free_email()
    password = fake.password()

    for key in XPATHS_2.keys():
        if key in ('email', 'email-retype'):
            info = fake_identity['email']
        elif key in ('pass', 'pass-retype'):
            info = password
        elif key == 'first_name':
            info = fake_identity['first_name']
        elif key == 'last_name':
            info = fake_identity['last_name']
        elif key == 'pn':
            break
        #     info = fake_identity['phone']

        driver.find_element_by_xpath(XPATHS_2.get(key)).send_keys(info)

    time.sleep(random.randint(0, 2))
    # select = Select(driver.find_element_by_id(COUNTRY_REGION_CODE_LABEL))
    # select.select_by_value(COUNTRY_CODE_US)
    select = Select(driver.find_element_by_id(COUNTRY_REGION_OF_RESIDENCE_LABEL))
    select.select_by_value(COUNTRY_CODE_US)

    driver.find_element_by_xpath(READ_ACCEPT_DATA_PRIVACY_STATEMENT_ANCHORTAG).click()
    time.sleep(1.5)
    driver.find_element_by_xpath(ACCEPT_BUTTON).click()
    time.sleep(2)
    
    driver.find_element_by_xpath(CREATE_ACCOUNT_BUTTON).click()
    # time.sleep(1.5)
    # for i in range(120):
    #     time.sleep(1.5)
    #     if (args.mailtm == MAILTM_DISABLED):
    #         mail = requests.get(f'https://api.guerrillamail.com/ajax.php?f=check_email&seq=1&sid_token={fake_identity.get("sid")}').json().get('list')

    #         if mail:
    #             passcode = re.findall('(?<=n is ).*?(?=<)', requests.get(f'https://api.guerrillamail.com/ajax.php?f=fetch_email&email_id={mail[0].get("mail_id")}&sid_token={fake_identity.get("sid")}').json().get('mail_body'))[0]
    #             break

    #     elif (args.mailtm == MAILTM_ENABLED):
    #         mail = requests.get("https://api.mail.tm/messages?page=1", headers={'Authorization':f'Bearer {fake_identity.get("sid")}'}).json().get('hydra:member')

    #         if mail:
    #             passcode = re.findall('(?<=n is ).*', requests.get(f'https://api.mail.tm{mail[0].get("@id")}', headers={'Authorization':f'Bearer {fake_identity.get("sid")}'}).json().get('text'))[0]
    #             break
    # else:
    #     args.mailtm ^= True
    #     main() # I should probably find a better way to do this.

    # driver.find_element_by_xpath(VERIFY_EMAIL_INPUT).send_keys(passcode)
    # driver.find_element_by_xpath(VERIFY_EMAIL_BUTTON).click()

    printf(f"successfully made account for fake email {email}")


def fill_out_application_and_submit(driver, random_city, fake_identity, ap):
    # make resume
    resume_filename = fake_identity['last_name']+'-Resume'
    make_resume(fake_identity['first_name']+' '+fake_identity['last_name'],
                fake_identity['email'], resume_filename+'.pdf')

    # wait for page to load
    #time.sleep(100)
    WebDriverWait(driver, 10).until(expected_conditions.presence_of_element_located((By.XPATH, PROFILE_INFORMATION_DROPDOWN)))

    # fill out form parts of app
    driver.find_element_by_xpath(PROFILE_INFORMATION_DROPDOWN).click()

    for key in XPATHS_1.keys():

        if key == 'resume':
            #driver.find_element_by_xpath(UPLOAD_A_RESUME_BUTTON).click()
            info = os.getcwd() + '/'+resume_filename+'.pdf'
        elif key == 'address':
            time.sleep(7)
            info = fake.street_address()
            driver.find_element_by_name(key).send_keys(info)
            continue
        elif key == 'city':
            info = random_city
            driver.find_element_by_name(key).send_keys(info)
            continue
        elif key == 'zip':
            info = random.choice(CITIES_TO_ZIP_CODES[random_city])
            driver.find_element_by_name(key).send_keys(info)
        # elif key == 'job':
        #     info = fake.job()
            continue
        elif key == 'pn':
            info = fake_identity['phone']
            driver.find_element_by_name('cellPhone').send_keys(info)
            continue
        # elif key == 'salary':
        #     first = random.randrange(15000, 30000, 5000)
        #     info = f'{format(first, ",")}-{format(random.randrange(first + 5000, 35000, 5000), ",")}'
        #print(key)
        driver.find_element_by_xpath(XPATHS_1.get(key)).send_keys(info)

    select = Select(driver.find_element_by_name('state'))
    select.select_by_visible_text("California")

    driver.find_element_by_name('ssn').send_keys(random.randrange(100000000,9999999999))


    
    l = [55711, 79609, 55712, 72682, 55703, 79612]
    l1 = [NO, YES]
    select = Select(driver.find_element_by_name('referralSourceExternal'))
    select.select_by_value(str(random.choice(l)))
    
    
    select = Select(driver.find_element_by_name('app_EdHighestLevelDiscipline'))
    select.select_by_visible_text(random.choice(l1))

    select = Select(driver.find_element_by_name('app_EdHighestLevel'))
    select.select_by_value(str(random.randrange(449, 456)))
    
    
    select = Select(driver.find_element_by_name('app_ACERelatives'))
    select.select_by_visible_text(NO)

    select = Select(driver.find_element_by_name('veteranStatus'))
    select.select_by_value(str(random.randrange(48385,48386)))

    select = Select(driver.find_element_by_name('app_18yearsofage'))
    select.select_by_visible_text(random.choice(l1))

    select = Select(driver.find_element_by_name('app_TobaccotoMinors'))
    select.select_by_visible_text(NO)
    
    select = Select(driver.find_element_by_name('app_DeptFirstChoice'))
    select.select_by_visible_text("Any")
    
    select = Select(driver.find_element_by_name('app_DeptSecondChoice'))
    select.select_by_visible_text("Any")

    d3 = today.strftime("%m/%d/%Y")
    
    driver.find_element_by_xpath("//input[@value='MM/DD/YYYY']").send_keys(d3)

    select = Select(driver.find_element_by_name('app_WorkEvenings'))
    select.select_by_visible_text(YES)

    select = Select(driver.find_element_by_name('app_WorkWeekends'))
    select.select_by_visible_text(YES)

    select = Select(driver.find_element_by_name('app_WorkHolidays'))
    select.select_by_visible_text(YES)

    
    select = Select(driver.find_element_by_name('app_EmpTypeDesired'))
    select.select_by_value(str(random.randrange(57751,57754)))

    select = Select(driver.find_element_by_name('app_timeToCall'))
    select.select_by_value(str(random.randrange(72371,72374)))

    select = Select(driver.find_element_by_name('availSun'))
    select.select_by_visible_text("Available Anytime")

    select = Select(driver.find_element_by_name('availSun'))
    select.select_by_visible_text("Available Anytime")

    select = Select(driver.find_element_by_name('availMon'))
    select.select_by_visible_text("Available Anytime")
    select = Select(driver.find_element_by_name('availTue'))
    select.select_by_visible_text("Available Anytime")
    select = Select(driver.find_element_by_name('availWed'))
    select.select_by_visible_text("Available Anytime")
    select = Select(driver.find_element_by_name('availThu'))
    select.select_by_visible_text("Available Anytime")
    select = Select(driver.find_element_by_name('availFri'))
    select.select_by_visible_text("Available Anytime")
    select = Select(driver.find_element_by_name('availSat'))
    select.select_by_visible_text("Available Anytime")


    tA = driver.find_element_by_xpath("//label[contains(text(), 'Have you ever worked for the Kroger Family of Companies or its subsidiaries?  If so, please provide details.')]/following-sibling::span")
    tA1 = tA.find_elements_by_xpath(".//*")[0].send_keys(NO)

    tA = driver.find_element_by_xpath("//label[contains(text(), 'Have you ever worked for any other retail, manufacturing, or logistics companies in the past?  If so, please provide details.')]/following-sibling::span")
    tA1 = tA.find_elements_by_xpath(".//*")[0].send_keys(NO)

    select = Select(driver.find_element_by_name('app_EverBeenTerminated'))
    select.select_by_visible_text(NO)

    driver.find_element_by_name('app_BackgroundSignature').send_keys(fake_identity['first_name']+' '+fake_identity['last_name'])

    select = Select(driver.find_element_by_name('app_ConvictionQuestion'))
    select.select_by_visible_text(NO)

    select = Select(driver.find_element_by_name('app_CashShortages'))
    select.select_by_visible_text(NO)

    driver.find_element_by_name('app_JOEmergencyContactFirstName').send_keys(fake.first_name())
    driver.find_element_by_name('app_JOEmergencyContactLastName').send_keys(fake.last_name())
    driver.find_element_by_name('app_JOEmergencyContactPhone').send_keys(random_phone())

    select = Select(driver.find_element_by_name('app_JOEmergencyContactRelationship'))
    select.select_by_value(str(random.randrange(55941,55947)))


    driver.find_element_by_name('app_ApplicantStatementSignature').send_keys(fake_identity['first_name']+' '+fake_identity['last_name'])

    select = Select(driver.find_element_by_name('app_ApplicantStatementConfirmation'))
    select.select_by_visible_text("I Understand")


    tA1 = driver.find_elements_by_xpath("//label[contains(text(), 'Yes')]")
    for t in tA1:
        try:
            t.click()
        except:
            pass
    #print(tA1)


    tA = driver.find_element_by_xpath("//label[contains(text(), 'In what neighborhood would you prefer to work?')]/following-sibling::span")
    tA1 = tA.find_elements_by_xpath(".//*")[0].send_keys("Any")

    time.sleep(1)
    printf(f"successfully filled out app forms for {random_city}")

   

    driver.find_element_by_xpath(APPLY_BUTTON).click()
    printf(f"successfully submitted application")
    time.sleep(2)


    print(ap)

    # take out the trash
    os.remove(resume_filename+'.pdf')


def random_email(name=None):
    if name is None:
        name = fake.name()

    mailGens = [lambda fn, ln, *names: fn + ln,
                lambda fn, ln, *names: fn + "_" + ln,
                lambda fn, ln, *names: fn[0] + "_" + ln,
                lambda fn, ln, *names: fn + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn + "_" + ln + str(int(1 / random.random() ** 3)),
                lambda fn, ln, *names: fn[0] + "_" + ln + str(int(1 / random.random() ** 3)), ]

    return random.choices(mailGens, MAIL_GENERATION_WEIGHTS)[0](*name.split(" ")).lower() + "@" + \
           requests.get('https://api.mail.tm/domains').json().get('hydra:member')[0].get('domain')

def random_phone(format=None):
    area_code = str(random.choice(AREA_CODES))
    middle_three = str(random.randint(0,999)).rjust(3,'0')
    last_four = str(random.randint(0,9999)).rjust(4,'0')

    if format is None:
        format = random.randint(0,4)

    if format==0:
        return area_code+middle_three+last_four
    elif format==1:
        return area_code+' '+middle_three+' '+last_four
    elif format==2:
        return area_code+'.'+middle_three+'.'+last_four
    elif format==3:
        return area_code+'-'+middle_three+'-'+last_four
    elif format==4:
        return '('+area_code+') '+middle_three+'-'+last_four

def main():
    appCount = 0
    while True:
        appCount += 1
        random_city = random.choice(list(CITIES_TO_URLS.keys()))
        try:
            driver = start_driver(random_city)
        except Exception as e:
            if not args.cloud:
                printf(f"FAILED TO START DRIVER: {e}")
            pass

        time.sleep(2)

        fake_first_name = fake.first_name()
        fake_last_name = fake.last_name()
        fake_phone = random_phone()
        if (args.mailtm == MAILTM_DISABLED):
            printf(f"USING GUERRILLA TO CREATE EMAIL")
            response = requests.get('https://api.guerrillamail.com/ajax.php?f=get_email_address').json()

            fake_email = response.get('email_addr')
            mail_sid = response.get('sid_token')
            printf(f"EMAIL CREATED")

        elif (args.mailtm == MAILTM_ENABLED):
            printf(f"USING MAILTM TO CREATE EMAIL")
            fake_email = requests.post('https://api.mail.tm/accounts', data='{"address":"'+random_email(fake_first_name+' '+fake_last_name)+'","password":" "}', headers={'Content-Type': 'application/json'}).json().get('address')
            mail_sid = requests.post('https://api.mail.tm/token', data='{"address":"'+fake_email+'","password":" "}', headers={'Content-Type': 'application/json'}).json().get('token')
            printf(f"EMAIL CREATED")

        fake_identity = {
            'first_name': fake_first_name,
            'last_name': fake_last_name,
            'email': fake_email,
            'phone': fake_phone,
            'sid' : mail_sid
        }

        try:
            generate_account(driver, fake_identity)
        except Exception as e:
            printf(f"FAILED TO CREATE ACCOUNT: {e}")
            pass

        try:
            fill_out_application_and_submit(driver, random_city, fake_identity, appCount)
        except Exception as e:
            printf(f"FAILED TO FILL OUT APPLICATION AND SUBMIT: {e}")
            pass
            driver.close()
            continue

        driver.close()
        time.sleep(5)


if __name__ == '__main__':
    main()
    sys.exit()
