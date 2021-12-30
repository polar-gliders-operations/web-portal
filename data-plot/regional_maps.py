# Create a figure
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmocean.cm as cmo
import matplotlib.pyplot as plt
import xarray as xr
import my_funcs
import time
import numpy as np
from matplotlib.animation import FuncAnimation
from scipy.interpolate import griddata as g

sst = xr.open_dataset('/home/mduplessis/web-portal/data/sst_latest.nc')

seaice_lnlt = xr.open_dataset('/home/mduplessis/web-portal/data/LongitudeLatitudeGrid-s6250-Antarctic.hdf',
                              engine='netcdf4'
                             )

seaice    = xr.open_dataset('/home/mduplessis/web-portal/data/seaice_latest.hdf', engine='netcdf4')

seaice = seaice.rename({'ASI Ice Concentration': 'si_conc'})
seaice = seaice.assign_coords(lon=(["x", "y"], np.array(seaice_lnlt.Longitudes)))
seaice = seaice.assign_coords(lat=(["x", "y"], np.array(seaice_lnlt.Latitudes)))
seaice = seaice.assign(si=(["x", "y"], seaice.si_conc.values))
seaice = seaice.drop('si_conc')

# regrid sea ice to linear grid

xnew=np.arange(-180, 180.1, 0.1)
ynew=np.arange(-85, -49.9, 0.1)

X = xnew # your longitudes you want to grid to
Y = ynew # your latitudies you want to grid to

x, y = np.meshgrid(xnew,ynew)

sic_new = np.ndarray([len(ynew), len(xnew)]) # setting a new sic array

x_, y_ = np.ravel(seaice.lon), np.ravel(seaice.lat)
x_[x_>180] = x_[x_>180]-360

si = np.ravel(seaice.si.values)
sic_new = g((y_, x_), si, (y, x), method='nearest')

sic_new[sic_new==0] = np.NaN
sic_new = np.ma.masked_invalid(sic_new)

sic = xr.Dataset(data_vars={'sic' : (('lat', 'lon'), sic_new)},
                 coords={'lat'  : ynew,
                         'lon'  : xnew})

# load etopo bathymetry 
etopo = xr.open_dataset('/home/mduplessis/web-portal/data/ETOPO1_Bed_g_gmt4.grd')
etopo_mr = etopo.sel(x=slice(0, 4.5), y=slice(-66, -62))
etopo_s1 = etopo.sel(x=slice(-2, 2), y=slice(-57, -53))

# site coordinates
site2_lats = [-64-(30/60),-64-(30/60),-64-(20/60),-64-(20/60),-64-(16/60),-64-(11/60),
              -64-(6/60), -64-(1/60), -63-(56/60),-63-(52/60),-63-(47/60),-63-(42/60),
              -63-(37/60),-63-(32/60),-63-(28/60),-63-(23/60),-63-(18/60),-63-(41/60)]

site2_lons = [3+(15/60),2+(27/60),2+(27/60),2+(27/60),2+(27/60),2+(27/60),2+(27/60),
              2+(27/60),2+(27/60),2+(27/60),2+(27/60),2+(27/60),2+(27/60),2+(27/60),
              2+(27/60),2+(27/60),2+(27/60),2+(27/60)]

site1_lats = [-55-(0/60),-55-(13/60),-55-(11/60),-55-(8/60),-55-(5/60),-55-(3/60),
              -55-(0/60),-54-(57/60),-54-(55/60),-54-(52/60),-54-(49/60),-54-(47/60),
              -55-(0/60)]

site1_lons = [0,0,0,0,0,0,0,0,0,0,0,0,0]

import matplotlib.ticker as mticker
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

sst_site1 = sst.sel(lon=slice(-2, 2), lat=slice(-57, -53))
sst_site2 = sst.sel(lon=slice(0, 4.5), lat=slice(-66, -62))

def gridlines():
    
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=0, alpha=0)
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 15}
    gl.ylabel_style = {'size': 15}

    return gl

def cbar(ticks, image):
    
    cb=plt.colorbar(mappable=image, 
                shrink=0.88, pad=0.1,
                aspect=35, orientation='horizontal',
                ticks=ticks,
               )
    
    cb.ax.tick_params(labelsize=14)
    
    return cb

## sst regional map for maud rise

fig = plt.figure(figsize=(5, 6))
ax  = fig.add_subplot(projection=ccrs.PlateCarree())

mean_sst_site2 = sst_site2.analysed_sst.isel(time=0).mean(dim={'lon', 'lat'})
min_sst_site2 = sst_site2.analysed_sst.isel(time=0).min(dim={'lon', 'lat'})
max_sst_site2 = sst_site2.analysed_sst.isel(time=0).max(dim={'lon', 'lat'})

levels = np.arange(np.round(min_sst_site2, decimals=2), np.round(max_sst_site2, decimals=2)+0.01, 0.01)

image = ax.contourf(sst_site2.lon, sst_site2.lat,
                      sst_site2.analysed_sst.isel(time=0),
                      cmap=cmo.thermal,
                      levels=levels,
                      transform=ccrs.PlateCarree())

ticks = np.linspace(np.round(min_sst_site2, decimals=1), np.round(max_sst_site2, decimals=1), num=5)

cb = cbar(ticks, image)
gl = gridlines()

levels = np.arange(np.round(min_sst_site2, decimals=2), np.round(max_sst_site2, decimals=2), 0.2)

cs=ax.contour(sst_site2.lon, sst_site2.lat,
           sst_site2.analysed_sst.isel(time=0),
           levels=levels, linestyles='-',
           colors='k', linewidths=1,
           transform=ccrs.PlateCarree())

plt.clabel(cs, fontsize=9, inline=1,fmt = '%1.1f', zorder=1)

ax.scatter(site2_lons, site2_lats, s=30, c='cyan', zorder=5,
           edgecolor='k', lw=1, transform=ccrs.PlateCarree())

gl.xlocator = mticker.FixedLocator([0, 1, 2, 3, 4])
gl.ylocator = mticker.FixedLocator([-66, -65, -64, -63])
ax.set_extent([0.5, 4.501, -66.001, -61.999])

ax.set_title('Sea surface temperature ($^{\circ}$C)', fontweight='bold', fontsize=15)

ax.contour(etopo_mr.x, etopo_mr.y, etopo_mr.z,
           levels=np.arange(-8000, 400, 400),
           alpha=0.75, linestyles='-',
           linewidths=0.5, colors='k', zorder=2)

ax.pcolormesh(sic.lon, sic.lat,
              sic.sic, transform=ccrs.PlateCarree(),
              zorder=2,
              cmap='gray')

ax.text(3.15, -65.9, str(sst.time[0].values)[:10], fontsize=14, c='w')
ax.text(3.15, -65.9, str(sst.time[0].values)[:10], fontsize=14, c='w')

time_stamp = str(sst.time[0].values)[:4]+str(sst.time[0].values)[5:7]+str(sst.time[0].values)[8:10]


plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/sst_MR_'+str(time_stamp)+'.png', dpi=300)
plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/sst_MR_latest.png', dpi=300)

#############################################################################################################

## sst map for site 1 ##

fig = plt.figure(figsize=(5, 6))
ax  = fig.add_subplot(projection=ccrs.PlateCarree())

mean_sst_site1 = sst_site1.analysed_sst.isel(time=0).mean(dim={'lon', 'lat'})
min_sst_site1 = sst_site1.analysed_sst.isel(time=0).min(dim={'lon', 'lat'})
max_sst_site1 = sst_site1.analysed_sst.isel(time=0).max(dim={'lon', 'lat'})

levels = np.arange(np.round(min_sst_site1, decimals=2), np.round(max_sst_site1, decimals=2)+0.01, 0.01)

image = ax.contourf(sst_site1.lon, sst_site1.lat,
                      sst_site1.analysed_sst.isel(time=0),
                      cmap=cmo.thermal,
                      levels=levels,
                      transform=ccrs.PlateCarree())

levels = np.arange(np.round(min_sst_site1, decimals=2), np.round(max_sst_site1, decimals=2), 0.5)

cs=ax.contour(sst_site1.lon, sst_site1.lat,
           sst_site1.analysed_sst.isel(time=0),
           levels=levels, linestyles='-',
           colors='k', linewidths=1,
           transform=ccrs.PlateCarree())

plt.clabel(cs, fontsize=9, inline=1,fmt = '%1.1f', zorder=1)


ticks = np.linspace(np.round(min_sst_site1, decimals=1), np.round(max_sst_site1, decimals=1), num=5)

cb = cbar(ticks, image)
gl = gridlines()

ax.scatter(site1_lons, site1_lats, s=30, c='cyan', zorder=5,
           edgecolor='k', lw=1, transform=ccrs.PlateCarree())

gl.xlocator = mticker.FixedLocator([-2, -1, 0, 1, 2])
gl.ylocator = mticker.FixedLocator([-57, -56, -55, -54, -53])
ax.set_extent([-2, 2.001, -57.001, -52.999])

cs=ax.contour(etopo_s1.x, etopo_s1.y, etopo_s1.z,
              levels=np.arange(-8000, 2000, 2000),
              alpha=0.75, linestyles='-',
              linewidths=0.5, colors='k', zorder=2)

ax.pcolormesh(sic.lon, sic.lat,
              sic.sic, transform=ccrs.PlateCarree(),
              zorder=2,
              cmap='gray')

ax.set_title('Sea surface temperature ($^{\circ}$C)', fontweight='bold', fontsize=15)

ax.text(0.65, -56.9, str(sst.time[0].values)[:10], fontsize=14, c='w')

time_stamp = str(sst.time[0].values)[:4]+str(sst.time[0].values)[5:7]+str(sst.time[0].values)[8:10]

plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/sst_S1_'+str(time_stamp)+'.png', dpi=300)
plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/sst_S1_latest.png', dpi=300)

##############################################################################################################

### load adt data ###

adt = xr.open_dataset('/home/mduplessis/web-portal/data/adt_latest.nc')
adt['gos'] = (('time', 'latitude', 'longitude'), np.sqrt(adt.ugos**2+adt.vgos**2).data)

adt_site1 = adt.sel(longitude=slice(-3, 3), latitude=slice(-58, -52))
adt_site2 = adt.sel(longitude=slice(0, 5), latitude=slice(-67, -61))

## plot adt site 1 ##

fig = plt.figure(figsize=(5, 6))
ax  = fig.add_subplot(projection=ccrs.PlateCarree())

image = ax.contourf(adt_site1.longitude, adt_site1.latitude,
                    adt_site1.gos.isel(time=0),
                    levels=np.arange(0, 0.36, 0.01),
                    cmap=cmo.speed,
                    transform=ccrs.PlateCarree())

vctrs = ax.quiver(adt_site1.longitude, adt_site1.latitude,
                  adt_site1.ugos.isel(time=0), adt_site1.vgos.isel(time=0),
                  scale=3e0, alpha=0.5,
                  transform=ccrs.PlateCarree())

cs = ax.contour(adt_site1.longitude, adt_site1.latitude,
                adt_site1.gos.isel(time=0),
                linewidths=0.75,
                levels=np.arange(0, 1, 0.05), colors='k',
                transform=ccrs.PlateCarree())

plt.clabel(cs, fontsize=12, inline=1,fmt = '%1.1f', zorder=1)

ax.scatter(site1_lons, site1_lats, s=30, c='cyan', edgecolor='k',
           zorder=5, lw=1, transform=ccrs.PlateCarree())

ticks=np.arange(0, 0.4, 0.05)

cb = cbar(ticks, image)
gl = gridlines()

gl.xlocator = mticker.FixedLocator([-2, -1, 0, 1, 2])
gl.ylocator = mticker.FixedLocator([-57, -56, -55, -54, -53])

ax.set_extent([-2, 2.001, -57.001, -52.999])

cs=ax.contour(etopo_s1.x, etopo_s1.y, etopo_s1.z,
              levels=np.arange(-8000, 2000, 2000),
              alpha=0.75, linestyles='-',
              linewidths=0.5, colors='k', zorder=2)

ax.pcolormesh(sic.lon, sic.lat,
              sic.sic, transform=ccrs.PlateCarree(),
              zorder=2,
              cmap='gray')

ax.set_title('Geostrophic velocity (m/s)', fontweight='bold', fontsize=15)

ax.text(0.65, -56.9, str(adt.time[0].values)[:10], fontsize=14, c='k')

time_stamp = str(adt.time[0].values)[:4]+str(adt.time[0].values)[5:7]+str(adt.time[0].values)[8:10]

plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/geovel_S1_'+str(time_stamp)+'.png', dpi=300)
plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/geovel_S1_latest.png', dpi=300)

################################################################################################################

### plot adt maud rise ###

fig = plt.figure(figsize=(5, 6))
ax  = fig.add_subplot(projection=ccrs.PlateCarree())

image = ax.contourf(adt_site2.longitude, adt_site2.latitude,
                    adt_site2.gos.isel(time=0),
                    levels=np.arange(0, 0.36, 0.01),
                    cmap=cmo.speed,
                    transform=ccrs.PlateCarree())

vctrs = ax.quiver(adt_site2.longitude, adt_site2.latitude,
                  adt_site2.ugos.isel(time=0), adt_site2.vgos.isel(time=0),
                  scale=2e0, alpha=0.5,
                  transform=ccrs.PlateCarree())

cs = ax.contour(adt_site2.longitude, adt_site2.latitude,
                adt_site2.gos.isel(time=0),
                levels=np.arange(0, 1, 0.05), colors='0.5',
                transform=ccrs.PlateCarree())

plt.clabel(cs, fontsize=12, inline=1,fmt = '%1.1f', zorder=1)

ticks=np.arange(0, 0.4, 0.05)

cb = cbar(ticks, image)
gl = gridlines()

ax.scatter(site2_lons, site2_lats, s=30, c='cyan', zorder=5,
           edgecolor='k', lw=1, transform=ccrs.PlateCarree())

gl.xlocator = mticker.FixedLocator([0, 1, 2, 3, 4])
gl.ylocator = mticker.FixedLocator([-66, -65, -64, -63])
ax.set_extent([0.5, 4.501, -66.001, -61.999])

ax.set_title('Geostrophic velocity (m/s)', fontweight='bold', fontsize=15)

ax.contour(etopo_mr.x, etopo_mr.y, etopo_mr.z,
           levels=np.arange(-8000, 400, 400),
           alpha=0.75, linestyles='-',
           linewidths=0.5, colors='k', zorder=2)

ax.pcolormesh(sic.lon, sic.lat,
              sic.sic, transform=ccrs.PlateCarree(),
              zorder=2,
              cmap='gray')

ax.text(3.15, -65.9, str(adt.time[0].values)[:10], fontsize=14, c='k')

time_stamp = str(adt.time[0].values)[:4]+str(adt.time[0].values)[5:7]+str(adt.time[0].values)[8:10]

plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/geovel_MR_'+str(time_stamp)+'.png', dpi=300)
plt.savefig('/home/mduplessis/web-portal/web-portal/data-plot/img/geovel_MR_latest.png', dpi=300)
