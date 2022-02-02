# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.11.5
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
### SAILBUOY DOWNLOADING DATA

import os
import numpy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pickle
import requests
import time

def dl_sb():
	
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument('--remote-debugging-port=9222')

    #driver = webdriver.Chrome(executable_path='/snap/bin/chromium.chromedriver',options=chrome_options)
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver",options=chrome_options)

    driver.get("https://ids.sailbuoy.no") # load webpage
    
    driver.find_element_by_id("UserName").send_keys("ugot")
    driver.find_element_by_id ("Password").send_keys("ugot2873")
    element = driver.find_element_by_css_selector("input[type='submit']"); # find the submit button 
    element.click() # click the submit button
    time.sleep(2) # wait for 2 seconds to be sure the page actually loaded

    #pickle.dump( driver.get_cookies() , open("cookies.pkl","wb")) 
    # make the cookies acessible for the session
    session = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies: 
        session.cookies.set(cookie['name'], cookie['value'])
    
    download_link1 = "https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName=SB1812D2" # SB1812D2 Uni, SB2016D VOTO
    download_link2 = "https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName=SB1812A2" # SB1812A2 Uni, SB2016A VOTO
    response1 = session.get(download_link1)
    response2 = session.get(download_link2)
    # at this point, the downloadable csv files are stored in the response object
    file1 = open("data.csv", "w")
    file2 = open("pilot.csv", "w")
    file1.write(str(response1.text))
    file2.write(str(response2.text))
    file1.close()
    file2.close()

    #print('Sailbuoy data downloaded...')

#dl_sb()
