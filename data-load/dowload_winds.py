from siphon.catalog import TDSCatalog
import numpy as np
from datetime import datetime, timedelta
import xarray as xr
from xarray.backends import NetCDF4DataStore
import pandas as pd
import cmocean.cm as cmo


def read_gfs_forecast(hindcast=0, forecast=72, bounds=[-30, -80, 50, -50]):

    # identify the latest collection of GFS 0.25 deg forecast
    ds = TDSCatalog('http://thredds.ucar.edu/thredds/catalog/'
                    'grib/NCEP/GFS/Global_0p25deg/catalog.xml').datasets['Latest Collection for GFS Quarter Degree Forecast']
    
    ncss = ds.subset()
    
    query = ncss.query()
    
    now = datetime.utcnow()
    query.time_range(now-timedelta(hours=hindcast), now+timedelta(hours=forecast)) # time range between now and 6 hours (reduced for now)
    
    query.lonlat_box(north=bounds[0], south=bounds[1], east=bounds[2], west=bounds[3]) # choose lat and lon boundaries
    query.accept('netcdf4')
    query.variables('u-component_of_wind_height_above_ground')   # test case only select u and v components
    query.variables('v-component_of_wind_height_above_ground')
    
    # import the data with xarray
    
    data = ncss.get_data(query)
    
    wind = xr.open_dataset(NetCDF4DataStore(data)) 
    
    wind.assign_coords(lon=(((wind.lon + 180) % 360) - 180))
    wind=wind.sortby(wind.lon).sel(height_above_ground4=10)
    
#     for i in wind.coords.keys():
#         if 'time' in i:
#             wind=wind.rename({i: 'time'})

    times=[]
    
    for i in wind.coords.keys():
        if 'time' in i:
            times+=i,
            
    wind=wind.rename({times[0]: 'time'})
            
    uwind = wind['u-component_of_wind_height_above_ground'].values
    vwind = wind['v-component_of_wind_height_above_ground'].values
    
    wind = wind.drop('u-component_of_wind_height_above_ground')
    wind['u-component_of_wind_height_above_ground'] = (('time', 'lat', 'lon'), uwind)
    
    if len(times)>1:   
        wind=wind.drop_dims(times[1])
    
    wind['wind_magnitude'] = (('time', 'lat', 'lon'), np.sqrt(uwind**2+vwind**2))

    time_start = str(wind.time[0].values)[:4] +str(wind.time[0].values)[5:7] +str(wind.time[0].values)[8:10] +str(wind.time[0].values)[11:13]
    time_end   = str(wind.time[-1].values)[:4]+str(wind.time[-1].values)[5:7]+str(wind.time[-1].values)[8:10]+str(wind.time[-1].values)[11:13]
    
    wind.to_netcdf('/Users/marcel/Google Drive/Projects/PG-web-portal/web-portal/data/'
                   'wind_gfs_'+str(time_start)+'_'+str(time_end)+'.nc')

    wind.to_netcdf('/Users/marcel/Google Drive/Projects/PG-web-portal/web-portal/data/'
                   'wind_gfs_latest.nc')
    
    return wind

read_gfs_forecast()