import xarray as xr
import gsw
import matplotlib.dates as mdates
from cmocean import cm as cmo  
import cartopy.crs as ccrs
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import numpy as np
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import matplotlib
import geopandas as gpd

font = {'family' : 'Avenir',
        'weight' : 'normal',
        'size'   : 20}
matplotlib.rc('font', **font)

matplotlib.rcParams['xtick.major.size'] = 8
matplotlib.rcParams['xtick.major.width'] = 1
matplotlib.rcParams['xtick.minor.size'] = 8
matplotlib.rcParams['xtick.minor.width'] = 1
matplotlib.rcParams['ytick.major.size'] = 8
matplotlib.rcParams['ytick.major.width'] = 1
matplotlib.rcParams['ytick.minor.size'] = 8
matplotlib.rcParams['ytick.minor.width'] = 1

# Load the data

sst = xr.open_dataset('../../data/sst_latest.nc').sel(lat=slice(-45,-30),lon=slice(0,25)).squeeze()
fsle = xr.open_dataset('../../data/fsle.nc').sel(lat=slice(-45,-30),lon=slice(0,25)).squeeze()
adt = xr.open_dataset('../../data/adt_latest.nc').sel(latitude=slice(-45,-30),longitude=slice(0,25)).squeeze()
swath = gpd.read_file('../../data/swot/swot_calval_orbit_june2015-v2_swath.shp')

# Read the gliders metadata
#sb1812 = pd.read_csv('')
#sb2326 = pd.read_csv('')
#sg675  = pd.read_csv('')
#se057  = pd.read_csv('')
#se070  = pd.read_csv('')

# Calculate dx and dy for each grid cell
lons, lats = np.meshgrid(sst.lon,sst.lat)
diff_lons = gsw.distance(lons,lats)
diff_lats = gsw.distance(lons.T,lats.T).T

# Calculate sst gradient and gos magnitude
sst['gradient'] = ((sst['analysed_sst'].diff('lat')/diff_lats)**2 + (sst['analysed_sst'].diff('lon')/diff_lons)**2)**(1/2)*1000
adt['gos'] = (('latitude', 'longitude'), np.sqrt(adt.ugos**2+adt.vgos**2).data)

# Moorings
M1 = [16.049411,-37.157775] # When the moorings are deployed, these values might need to be updated to reflect the actual locations
M2 = [13.472228,-35.970445]

# Extens for the big map and the subset
bextent = [9.99,25.01,-40.01,-29.99] # Big extent
sextent = [11.99,18.01,-38.01,-33.99] # Small extent

def add_features(ax,left):
    
    ax.add_feature(cfeature.LAND,   facecolor='0.8',edgecolor='k',zorder=3)
    ax.add_feature(cfeature.RIVERS, edgecolor='w'  ,zorder=3)
    ax.add_feature(cfeature.LAKES,  facecolor='w'  ,zorder=3)
    ax.set(xlabel='',ylabel='')
    ax.set_title(sst.time.values.astype('datetime64[D]'),y=1,x=0.5)

    gls = ax.gridlines(crs=ccrs.PlateCarree(), 
                        draw_labels=True,
                        x_inline=False, 
                        y_inline=False,
                        linewidth=0.75,
                        alpha=0.75, 
                        linestyle='--', 
                        color='w',
                        ylocs=matplotlib.ticker.MultipleLocator(base=2),
                        xlocs=matplotlib.ticker.MultipleLocator(base=2))

    gls.top_labels = False
    gls.bottom_labels = True
    gls.right_labels = False    
    gls.left_labels = left
    gls.xpadding=10
    gls.ypadding=10   
    
def add_sla_contours(ax):
    ax.contour(adt.longitude, adt.latitude,
                    adt.sla.squeeze(),
                    linewidths=0.75, alpha=1,
                    levels=np.arange(-2, 2, 0.1), colors='w',zorder=2)
    
def add_moorings(ax,d):
    
    ax.scatter(M1[0],M1[1],marker='o',fc='w',s=200,zorder=6,ec='k',lw=2)
    ax.text(M1[0]+.0025*d,M1[1]-.01,'1',c='k',zorder=6,ha='center',va='center',fontsize=10)
    
    ax.scatter(M2[0],M2[1],marker='o',fc='w',s=200,zorder=6,ec='k',lw=2)
    ax.text(M2[0]+0.0025*d,M2[1]-0.01,'2',c='k',zorder=6,ha='center',va='center',fontsize=10)

def add_box(ax):
    ax.plot([12,18],[-34,-34],c='w',lw=2,ls='--',zorder=5)
    ax.plot([12,18],[-38,-38],c='w',lw=2,ls='--',zorder=5)
    ax.plot([12,12],[-34,-38],c='w',lw=2,ls='--',zorder=5)
    ax.plot([18,18],[-34,-38],c='w',lw=2,ls='--',zorder=5)
    
def add_swath(ax):
    Swath = ax.add_geometries(swath.geometry, crs=ccrs.PlateCarree(),zorder=4)
    Swath._kwargs['facecolor'] = 'w'
    Swath._kwargs['edgecolor'] = 'k'
    Swath._kwargs['alpha'] = 0.25

def plot_gos(ax):
    
    image = ax.contourf(adt.longitude, adt.latitude,
                         adt.gos,
                         levels=np.arange(0, 1.6, 0.05),
                         cmap=plt.get_cmap('cmo.speed',31), extend='max',
                         transform=ccrs.PlateCarree(),zorder=1)
    
    vctrs = ax.quiver(adt.longitude[::1], adt.latitude[::1],
                       adt.ugos[::1, ::1], adt.vgos[::1, ::1],
                       scale=2.5e1, alpha=0.8, headaxislength=5, headlength=5, headwidth=5, width=1e-3,
                       transform=ccrs.PlateCarree(),zorder=1)
    
    cb = plt.colorbar(image,ax=ax,pad=0.01)
    
    qk = ax.quiverkey(vctrs, 0.855, 1.025, 0.5, '0.5 m s$^{-1}$', labelpos='E',
                   coordinates='axes',zorder=6,color='k')
    
    cb.set_label('Geostrophic velocity (m s$^{-1}$)\nAVISO', labelpad=20)
    
def plot_fsle(ax):
    im = ax.pcolor(fsle.lon,fsle.lat,fsle.lambda1.T,cmap='viridis',zorder=1)
    plt.colorbar(im,ax=ax, label="FLE associated to the maximum eigenvalues\nof Cauchy-Green strain tensor (day$^{-1}$)",pad=0.01)
    
def plot_sst(ax):
    im = ax.pcolor(sst.lon,sst.lat,sst['analysed_sst'],cmap=cmo.thermal,vmin=15,vmax=25,zorder=1)
    plt.colorbar(im,ax=ax, label='Sea surface temperature (°C)\nGHRSST MUR',pad=0.01)

def plot_sst_g(ax):
    im = ax.pcolor(sst.lon,sst.lat,sst.gradient,cmap=cmo.thermal,vmin=0,vmax=0.1,zorder=1)
    plt.colorbar(im,ax=ax, label='Sea surface temperature gradient (°C/km)\nGHRSST MUR',pad=0.01)

def plot_sla(ax):
    im = ax.pcolor(adt.longitude,adt.latitude,adt.sla,cmap=cmo.balance,vmin=-1,vmax=1,zorder=1)
    plt.colorbar(im,ax=ax, label='Sea level anomaly (m)\nAVISO',pad=0.01)

    
    
######## Plotting the maps ########

big = [True,True,True,True,True,False,False,False,False,False]
for i in range(10):
    fig,ax = plt.subplots(figsize=(14,8),sharey=True,subplot_kw={'projection':ccrs.PlateCarree()},constrained_layout=True)

    add_features(ax,True)
    add_swath(ax)
    
    if (i != 1) | (i != 6): # FSLE does not need contours
        add_sla_contours(ax)
    
    if big[i] == True:
        extent = bextent
        add_box(ax)
        add_moorings(ax,1)
        save = 'big'

    else:
        extent = sextent
        add_moorings(ax,-1)
        save = 'small'

    if (i == 0) | (i == 5):
        plot_gos(ax)
        ax.set_extent(extent)
        plt.savefig('../../plots/gos_{}_{}.png'.format(save,adt.time.dt.strftime("%Y%m%d").values))
        plt.savefig('../../plots/gos_{}_latest.png'.format(save))
    
    if (i == 1) | (i == 6):
        plot_fsle(ax)
        ax.set_title(f"Advection time: {fsle.attrs['advection_time'][:-9]} from {fsle.attrs['start_time'][:-9]}")
        ax.set_extent(extent)
        plt.savefig('../../plots/fsle_{}_{}_{}_days.png'.format(save,fsle.attrs['start_time'][:-9],int(fsle.attrs['advection_time'][:2])))
        plt.savefig('../../plots/fsle_{}_latest.png'.format(save))
    if (i == 2) | (i == 7):
        plot_sst(ax)
        ax.set_extent(extent)
        plt.savefig('../../plots/sst_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
        plt.savefig('../../plots/sst_{}_latest.png'.format(save))
    if (i == 3) | (i == 8):
        plot_sst_g(ax)
        ax.set_extent(extent)
        plt.savefig('../../plots/sst_g_{}_{}.png'.format(save,sst.time.dt.strftime("%Y%m%d").values))
        plt.savefig('../../plots/sst_g_{}_latest.png'.format(save))
    if (i == 4) | (i == 9):
        plot_sla(ax)
        ax.set_extent(extent)
        plt.savefig('../../plots/sla_{}_{}.png'.format(save,adt.time.dt.strftime("%Y%m%d").values))
        plt.savefig('../../plots/sla_{}_latest.png'.format(save))