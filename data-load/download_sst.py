#!/usr/bin/env python3
# run daily - outputs a Figure, but also saves the netcdf
import numpy as np
from siphon.catalog import TDSCatalog

server_path = '../data/'

ds = TDSCatalog('https://thredds.jpl.nasa.gov/thredds/catalog_ghrsst_gds2.xml')
ds = ds.datasets['MUR-JPL-L4-GLOB-v4.1 Aggregation']

ncss = ds.subset()
query = ncss.query()

from datetime import datetime, timedelta
now = datetime.utcnow()
query.time_range(now - timedelta(days=2), now) # time range between now and one day ahead - this is not available - only available at one day before resolution  

query.lonlat_box(north=-30, south=-45, east=25, west=0) # choose lat and lon boundaries
query.variables('analysed_sst')   

import xarray as xr
from xarray.backends import NetCDF4DataStore
import netCDF4

sst = ncss.get_data(query)
sst = xr.open_dataset(NetCDF4DataStore(sst))
sst['analysed_sst']=(('time', 'lat', 'lon'), sst.analysed_sst.data-273.15)

# mask land
from global_land_mask import globe
lat,lon=np.meshgrid(sst.lat,sst.lon)
is_in_ocean = globe.is_ocean(lat, lon)
masked_sst=(sst.analysed_sst.data.squeeze()*is_in_ocean.T)
masked_sst[masked_sst==0.]=np.nan
masked_sst_labels=xr.DataArray(data=masked_sst[np.newaxis,:,:],
                        dims=['time','lat','lon'])
sst['masked_sst']=masked_sst_labels

# # save sst data to netcdf
sst.to_netcdf(server_path + 'sst_{}.nc'.format((sst.time.dt.strftime("%Y%m%d")).values.tolist()[0]))
sst.to_netcdf(server_path + 'sst_latest.nc')
