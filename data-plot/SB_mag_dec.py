### SAILBUOY UPDATING MAGNETIC DECLINATION

import os
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import pickle
import requests
import time
import geomag
import pandas as pd

df = pd.read_csv('/home/web/web-portal/data/SB_all_positions.csv') # Read the positions
declin = str(np.round(geomag.declination(df['Lat'].values[-1],df['Long'].values[-1]),1)) # Calculate the declination for the latest position
message = "$DCPS.DEV " + declin

chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")

driver = webdriver.Chrome(executable_path="/snap/bin/chromium.chromedriver",options=chrome_options)

driver.get("https://iridium2.azurewebsites.net/") # load webpage

driver.find_element_by_id("UserName").send_keys("ugot")
driver.find_element_by_id ("Password").send_keys("ugot2873")
element = driver.find_element_by_css_selector("input[type='submit']"); # find the submit button 
element.click() # click the submit button
time.sleep(2) # wait for 2 seconds to be sure the page actually loaded

session = requests.Session()
cookies = driver.get_cookies()
for cookie in cookies: 
    session.cookies.set(cookie['name'], cookie['value'])

driver.get("https://iridium2.azurewebsites.net/SendMessage?instrName=SB1812D2") # load webpage
driver.find_element_by_id("Comment").send_keys("Automated declination update")
driver.find_element_by_id ("Message").send_keys(str(message))
driver.find_element_by_id ("Password").send_keys("sb1812d")
element = driver.find_element_by_css_selector("input[type='submit']"); # find the submit button 
element.click() # click the submit button