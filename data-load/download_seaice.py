import wget
import requests
from bs4 import BeautifulSoup
import xarray as xr
import numpy as np
import cmocean
import pandas as pd

import datetime
year = datetime.datetime.now().year

# Download the latest sea ice from the AWI ftp data portal

# Sea ice concentration data were obtained from http://www.meereisportal.de (grant: REKLIM-2013-04). 
# Spreen, G.; Kaleschke, L. and Heygster, G. (2008), Sea ice remote sensing using AMSR-E 89 GHz channels J. Geophys. Res.,vol. 113, C02S03, doi:10.1029/2005JC003384.

# locates the server where the data is
url = 'http://data.meereisportal.de/data/iup/hdf/s/'+str(year)+'/'
ext = 'hdf' # choose the file extension of the data

# function to provide a list of the filenames within the data server so we can choose the most recent file
def listFD(url, ext=''):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    return [url + node.get('href') for node in soup.find_all('a') if node.get('href').endswith(ext)]

flist = listFD(url, ext) # get list of all data in the data server
url = flist[-1] # choose the most recent file
filename = wget.download(url) # download the data from the most recent file

# download the lat and lon info for the sea ice data
url = 'https://seaice.uni-bremen.de/data/grid_coordinates/s6250/LongitudeLatitudeGrid-s6250-Antarctic.hdf' 
filename_ll = wget.download(url)
