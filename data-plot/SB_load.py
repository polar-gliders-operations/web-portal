import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import xarray as xr
import pandas as pd
import datetime
import matplotlib.dates as mdates
import xarray as xr
import pandas as pd
import cmocean as cmo
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import glidertools as gt
import matplotlib.gridspec as gridspec
import cmocean as cmo
from tqdm import tqdm
import gsw
from matplotlib.dates import datestr2num

#########################################################
# ----------------------------------------------------- #
# --------------------- Sailbuoy  --------------------- #
# ----------------------------------------------------- #
#           Author: Johan M. Edholm (2021)              #
# ----------------------------------------------------- #
# ----------------------------------------------------- #
#########################################################

"""
Module to load and work with SailBuoy data.
"""

##################
#    SAILBUOY    #
##################

##################
#  Loading data  #
##################

def load_pld(path='../data-load/data.csv', start='2021', end='2023'):

    """
    Loading the paylod data from the SailBuoy. Accurate for SB1812 as of Dec 2021.

    Parameters
    ---------
    path: str
        Path to the csv-file.
    start, end: string
        Time limits, e.g. '2021-05-01','2021-06-01' to plot the month of May, or '2021','2022' for 2021.

    Returns
    ---------
    ds: xr.Dataset
        Containing payload

    """
    print('Loading sensor data...')

    df = pd.read_csv(path,sep=None,engine='python')
    ds = df.set_index(df['Time']).to_xarray()
    ds = ds.assign_coords({'Time':(ds.Time.values.astype('datetime64[s]'))}).set_coords({'Lat','Long'})
    ds = ds.sel({'Time':slice((start), (end))})

    names = ['Latitude',
             'Longitude',
             'Time to first GPS fix',
             'Transmitter counter',
             'Recieved commands count',
             'Iridium transmission tries',
             'On time (Time in acquisition mode)',
             'Disk used to store data',
             'Sent files count',
             'Current consumption',
             'Battery voltage',
             'Payload temperature',
             'Mean air temperature',
             'Mean wind direction',
             'Mean wind speed',
             '95% largest wind speed value',
             'Mean heading',
             'GPS corrected data',
             'Sea Surface Conductivity',
             'Sea Surface Temperature',
             'Status indicator',
             'Acquisition period',
             'Surface Current Speed',
             'Surface Current Direction',
             '']

    units = ['DD.dd°',
             'DD.dd°',
             'seconds',
             'integer',
             'integer',
             'integer',
             'seconds',
             'integer',
             'integer',
             'A',
             'V',
             '°C',
             '°C',
             'degrees',
             'm/s',
             'm/s',
             'degrees',
             'integer',
             'Conductivity units',
             '°C',
             'integer',
             'minutes',
             'm/s',
             'degrees',
             '']

    for i in tqdm(range(len(df.columns.values)-1)):
        ds[df.columns.values[i+1]].attrs['Name'] = names[i]
        ds[df.columns.values[i+1]].attrs['Units'] = units[i]
    ds.attrs['Name'] = 'SB Kringla Datalogger'

    print('Converting conductivity to Absolute Salinity...')
    ds = ds.assign(SSS=gsw.SA_from_SP(gsw.SP_from_C(ds.AADI_Cond, ds.AADI_Temp, 0),0,ds.Lat,ds.Long))
    ds['SSS'].attrs['Name'] = 'Sea Surface Salinity'
    ds['SSS'].attrs['Units'] = 'g/kg'

    print('Calculating density...')
    ds = ds.assign(Density=gsw.density.rho(ds['SSS'], gsw.CT_from_t(ds['SSS'], ds.AADI_Temp, 0),0))
    ds['Density'].attrs['Name'] = 'Density'
    ds['Density'].attrs['Units'] = 'kg/m3'
    ds = ds.assign(Sigma=gsw.density.rho(ds['SSS'], gsw.CT_from_t(ds['SSS'], ds.AADI_Temp, 0),0)-1000)
    ds['Sigma'].attrs['Name'] = 'Density'
    ds['Sigma'].attrs['Units'] = 'kg/m3'
    
    print('Calculating distance...')
    ds['Distance'] = xr.DataArray(gt.utils.distance(ds.Lat,ds.Long).cumsum(),dims={'Time':ds.Time},coords={'Time':ds.Time})
    ds['Distance'].attrs['Name'] = 'Distance'
    ds['Distance'].attrs['Units'] = 'm'
    ds = ds.set_coords({'Distance'})
    
    return ds

def load_nav(path='../data-load/pilot.csv', start='2019', end='2020'):

    """
    Loading the navigational data from the SailBuoy. Accurate for SB Kringla as of Dec 2021.

    Parameters
    ---------
    
    path: str
        Path do the csv-file
    
    start, end: string
        Time limits, e.g. '2021-05-01','2021-06-01' to plot the month of May.

    Returns
    ---------
    ds: xr.Dataset
        Containing payload

    """
    
    print('Loading nav data...')

    df = pd.read_csv(path,sep=None,engine='python')
    ds = df.set_index(df['Time']).to_xarray()
    ds = ds.assign_coords({'Time':(ds.Time.values.astype('datetime64[s]'))})
    ds = ds.sel({'Time':slice((start), (end))})

    names = ['Latitude',
             'Longitude',
             'Time to first GPS fix',
             'Warning indicator',
             'Tack counter',
             'Leak switch indicator',
             'Recieved commands count',
             'Current consumption',
             'Battery voltage',
             'Payload temperature',
             'Payload pressure',
             'Payload humidity',
             'Iridium transmission tries',
             'On time (Time in acquisition mode)',
             'Velocity over ground',
             'GPS Tack direction',
             'Distance from the line defined by the start and end waypoint',
             'GPS Waypoint direction',
             'Allowed distance from the track',
             'Calculated wind direction',
             'Autopilot on/off',
             'Switch waypoint mode enabled',
             'The next autopilot tack',
             'Current tack',
             'Previous tack',
             'Tack history 1',
             'Tack history 2',
             'Tack history 3',
             'Waypoint reached',
             'Within corridor',
             'Sail at port bow count',
             'Sail at port count',
             'Sail at center count',
             'Sail at starboard count',
             'Sail at starboard bow count',
             'Heavy weather indicator',
             'Sail rotation indicator',
             'Big leak indicator',
             '',
             '',
             '',
             '',
             '',
             '',
             '']

    units = ['DD.dd°',
             'DD.dd°',
             'seconds',
             'True/False',
             'integer',
             'True/False',
             'integer',
             'A',
             'V',
             '°C',
             'hPa',
             '%',
             'integer',
             'seconds',
             'm/s',
             'degrees',
             'm',
             'degrees',
             'm',
             'degrees',
             'True/False',
             'True/False',
             'integer',
             'integer',
             'integer',
             'integer',
             'integer',
             'integer',
             'True/False',
             'True/False',
             'integer',
             'integer',
             'integer',
             'integer',
             'integer',
             'True/False',
             'True/False',
             'True/False',
             '',
             '',
             '',
             '',
             '',
             '',
             '']

    for i in tqdm(range(len(df.columns.values)-1)):
        ds[df.columns.values[i+1]].attrs['Name'] = names[i]
        ds[df.columns.values[i+1]].attrs['Units'] = units[i]
    ds.attrs['Name'] = 'SB Kringlam Autopilot'
    
    return ds