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
#           Author: Johan M. Edholm (2023)              #
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

def load_pimpim(path='../data/SB2326D.csv', start='2023', end='2025'):

    """
    Loading the paylod data from the SailBuoy. Accurate for SB2326 as of Mar 2023.

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
    #print('Loading sensor data...')

    df = pd.read_csv(path)
    ds = df.set_index(df['Time']).to_xarray()
    ds = ds.assign_coords({'Time':(ds.Time.values.astype('datetime64[s]'))}).set_coords({'Lat','Long'})
    ds = ds.sel({'Time':slice((start), (end))})
    long_names = ['Latitude',
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
             'Relative humidity',
             'Mean air temperature',
             'Mean air temperature FT',
             'Mean wind direction',
             'Mean wind speed',
             '95% largest wind speed value',
             'Mean heading',
             'Sea Surface Temperature',
             'Sea Surface Conductivity',
             'Sea Surface Salinity',
             'Status indicator',
             'Acquisition period',
             'Surface Current Speed',
             'Surface Current Direction',
             '','','']

    std_names = ['latitude',
             'longitude',
             'time_to_first_GPS_fix',
             'transmitter_counter',
             'recieved_commands',
             'transmission_tries',
             'sampling_time',
             'disk_storage',
             'count',
             'current',
             'voltage',
             'temperature',
             'relative_humidity',
             'air_temperature',
             'air_temperature',
             'wind_from_direction',
             'wind_speed',
             'wind_speed_of_gust',
             'platform_yaw_angle',
             'sea_water_temperature',
             'sea_water_electrical_conductivity',
             'sea_water_practical_salinity',
             'status_indicator',
             'sampling_time',
             'sea_water_velocity',
             'current_to_direction',
             '','','']

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
             '%',
             '°C',
             '°C',
             'degrees',
             'm/s',
             'm/s',
             'degrees',
             '°C',
             'Conductivity units',
             'PSU',
             'integer',
             'minutes',
             'm/s',
             'degrees',
             '','','']

    # Add attributes to the variables
    for i in range(len(df.columns.values)-1):
        ds[df.columns.values[i+1]].attrs['standard_name'] = std_names[i]
        ds[df.columns.values[i+1]].attrs['long_name'] = long_names[i]
        ds[df.columns.values[i+1]].attrs['units'] = units[i]
    ds.attrs['name'] = 'SB PimPim Datalogger'
    ds = ds.rename({'Lat':'latitude','Long':'longitude','Time':'time'})
    
    # Remove any variables called Unnamed
    for key in list(ds.keys()):
        if 'Unnamed' in key:
            ds = ds.drop(key)
            
    # Converting practical to absolute salinity
    ds['SA'] = (('time'),gsw.SA_from_SP(ds.RBRL_Sal,0,ds.latitude,ds.longitude).values)
    ds['SA'].attrs['standard_name'] = 'sea_water_absolute_salinity'
    ds['SA'].attrs['long_name'] = 'Seawater salinity'
    ds['SA'].attrs['units'] = 'g/kg'

    # Calculating distance
    ds['distance'] = (('time'), gt.utils.distance(ds.latitude,ds.longitude).cumsum())
    ds['distance'].attrs['standard_name'] = 'distance'
    ds['distance'].attrs['long_name'] = 'Distance'
    ds['distance'].attrs['units'] = 'm'
    ds = ds.set_coords({'distance'})
    
    return ds

def load_kringla(path='../data/SB1812D.csv', start='2023', end='2025'):

    """
    Loading the paylod data from the SailBuoy. Accurate for SB1812 as of Mar 2023.

    Parameters
    ---------
    path: str
        Path to the csv-file.
    start, end: string
        Time limits, e.g. '2022-05-01','2022-06-01' to plot the month of May, or '2023','2024' for 2023.

    Returns
    ---------
    ds: xr.Dataset
        Containing payload

    """
    #print('Loading sensor data...')

    df = pd.read_csv(path)
    ds = df.set_index(df['Time']).to_xarray()
    ds = ds.assign_coords({'Time':(ds.Time.values.astype('datetime64[s]'))}).set_coords({'Lat','Long'})
    ds = ds.sel({'Time':slice((start), (end))})

    std_names = ['latitude',
             'longitude',
             'time_to_first_GPS_fix',
             'transmitter_counter',
             'recieved_commands',
             'transmission_tries',
             'sampling_time',
             'disk_storage',
             'count',
             'current',
             'voltage',
             'temperature',
             'air_temperature',
             'wind_from_direction',
             'wind_speed',
             'wind_speed_of_gust',
             'platform_yaw_angle',
             'gps_corrected_data',
             'sea_water_electrical_conductivity',
             'sea_water_temperature',
             'status_indicator',
             'sampling_time',
             'sea_water_velocity',
             'current_to_direction',
             '','','']

    long_names = ['Latitude',
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
             '','','']

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
             '','','']

    # Add attributes to the variables
    for i in range(len(df.columns.values)-1):
        ds[df.columns.values[i+1]].attrs['standard_name'] = std_names[i]
        ds[df.columns.values[i+1]].attrs['long_name'] = long_names[i]
        ds[df.columns.values[i+1]].attrs['units'] = units[i]
    ds.attrs['name'] = 'SB Kringla Datalogger'
    ds = ds.rename({'Lat':'latitude','Long':'longitude','Time':'time'})
    
    # Remove any variables called Unnamed
    for key in list(ds.keys()):
        if 'Unnamed' in key:
            ds = ds.drop(key)
            
    # Converting practical to absolute salinity
    ds['SA'] = (('time'),gsw.SA_from_SP(gsw.SP_from_C(ds.AADI_Cond, ds.AADI_Temp, 0),0,ds.latitude,ds.longitude).values)
    ds['SA'].attrs['standard_name'] = 'sea_water_absolute_salinity'
    ds['SA'].attrs['long_name'] = 'Seawater salinity'
    ds['SA'].attrs['units'] = 'g/kg'

    # Calculating distance
    ds['distance'] = (('time'), gt.utils.distance(ds.latitude,ds.longitude).cumsum())
    ds['distance'].attrs['standard_name'] = 'distance'
    ds['distance'].attrs['long_name'] = 'Distance'
    ds['distance'].attrs['units'] = 'm'
    ds = ds.set_coords({'distance'})
    
    return ds