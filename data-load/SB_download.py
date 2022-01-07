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
import matplotlib
from matplotlib import pyplot as plt
import numpy
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pickle
import requests
import time

def dl_sb(which='uni',):
    driver = webdriver.Chrome(executable_path='/home/web/chromedriver')
    #driver = webdriver.PhantomJS() # executable_path="/home/mduplessis/python_modules/phantomjs-prebuilt/bin/phantomjs") #(executable_path="/home/martin/Doktorarbeit_SWE/ctd/sailbuoyplotting/node_modules/phantomjs-prebuild/bin/phantomjs") # open a virtual browser
    #driver = webdriver.PhantomJS()
    driver.get("https://ids.sailbuoy.no") # load webpage
    if which == 'uni':
        driver.find_element_by_id("UserName").send_keys("ugot") # type in username # ugot for University, voto for VOTO
        driver.find_element_by_id ("Password").send_keys("ugot2873") # type in password # ugot2873 for University, oce243 for VOTO
    if which == 'voto':
        driver.find_element_by_id("UserName").send_keys("voto") # type in username # ugot for University, voto for VOTO
        driver.find_element_by_id ("Password").send_keys("oce243") # type in password # ugot2873 for University, oce243 for VOTO
    element = driver.find_element_by_css_selector("input[type='submit']"); # find the submit button 
    element.click() # click the submit button
    time.sleep(2) # wait for 2 seconds to be sure the page actually loaded

    #pickle.dump( driver.get_cookies() , open("cookies.pkl","wb")) 
    # make the cookies acessible for the session
    session = requests.Session()
    cookies = driver.get_cookies()
    for cookie in cookies: 
        session.cookies.set(cookie['name'], cookie['value'])
    if which == 'uni':
        download_link1 = "https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName=SB1812D2" # SB1812D2 Uni, SB2016D VOTO
        download_link2 = "https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName=SB1812A2" # SB1812A2 Uni, SB2016A VOTO
    if which == 'voto':
        download_link1 = "https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName=SB2016D" # SB1812D2 Uni, SB2016D VOTO
        download_link2 = "https://ids.sailbuoy.no/GenCustomData/_DownloadAllAsCSV?instrName=SB2016A" # SB1812A2 Uni, SB2016A VOTO    
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
dl_sb()
