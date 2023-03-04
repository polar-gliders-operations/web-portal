import sb_utils as sbu
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, DayLocator, HourLocator
import gsw
import geomag
import matplotlib.dates as mdates
from cmocean import cm as cmo
import matplotlib as mpl
from tqdm.notebook import tqdm_notebook as tqdm
import sys
import cartopy.crs as ccrs
from matplotlib.colors import ListedColormap, LinearSegmentedColormap

font = {'family' : 'Avenir',
        'weight' : 'normal',
        'size'   : 30}

mpl.rc('font', **font)

def rot_ticks(axs,rot,ha):
    for xlabels in axs.get_xticklabels():
                xlabels.set_rotation(rot)
                xlabels.set_ha(ha)


mpl.rcParams['xtick.major.size'] = 8
mpl.rcParams['xtick.major.width'] = 2
mpl.rcParams['xtick.minor.size'] = 8
mpl.rcParams['xtick.minor.width'] = 1
mpl.rcParams['ytick.major.size'] = 8
mpl.rcParams['ytick.major.width'] = 2
mpl.rcParams['ytick.minor.size'] = 8
mpl.rcParams['ytick.minor.width'] = 1

wind_c1 = ListedColormap(["k", '#9EB0A7', '#9EB0A7', 'gold','gold',"#74A757", "#74A757","k"]) # Estel's paper
wind_c2 = ListedColormap(['#FCC681','#FF819E','#FF819E','#A0A3E0','#A0A3E0','#99D4E5','#99D4E5','#FCC681']) # Soft pastels, use this
wind_c3 = ListedColormap(['#c76674','#9a9945','#9a9945','#6779d0','#6779d0','#974d9d','#974d9d','#c76674']) # iWantHue colors

c1 = '#ff6600'
c0 = '#006699'

sbpp = sbu.load_pimpim(path='',start='2023-02-22')
sbk = sbu.load_kringla(path='',start='2023-02-21')

sbpp['FT_WindDir'] = (sbpp['FT_WindDir'] + 180) % 360
sbk['AirmarWindDirection'] = (sbk['AirmarWindDirection'] + 180) % 360

sbu.save_csv(sbk,'SB1812')
sbu.save_csv(sbpp,'SB2326')

def plot_line_sct(ds,ax,cbar_ax,speed,direction,gust,gusts):
    
    # Plot current speed
    ds[speed].plot(ax=ax,lw=3,c='k',zorder=2)

    # Plot scatters for wind speed and direction
    sct = ds.plot.scatter(x='time',
                            y=speed,
                            hue=direction,
                            ax=ax,
                            cmap=wind_c2,
                            vmin=0,
                            vmax=360,
                            s=250,
                            add_guide=False,
                            zorder=2)

    if gusts == True:
        var = 'Wind'
        ax.fill_between(ds['time'],
                   ds[speed],
                   ds[gust],
                   alpha=0.25,
                   ec=None,
                   fc='silver',
                   zorder=1)
    else:
        var='Current'
        
    cb = plt.colorbar(sct,cax=cbar_ax,
                      ax=ax,
                      pad=-0.06,
                      label=f'{var} to',
                      aspect=10,
                      ticks=[0,90,180,270,360])

    cb.ax.set_yticklabels(['N',
                           'E',
                           'S',
                           'W',
                           'N'])
    ax.set_xlabel('')
    ax.set_ylabel('(m s$^{-1}$)')
    
def plot_surface(ds,ax,left,right,units):
    
    ax_s = ax.twinx()
    ds[right].plot(x='time',ax=ax_s,c=c0,lw=3)
    ds[left].plot(x='time',ax=ax,c=c1,lw=3)
    ax_s.set_ylabel(f"({ds[right].attrs['units']})",c=c0)
    ax_s.set_title('',loc='center')
    ax_s.set_xlabel('')
    ax.set_xlabel('')
    ax.set_ylabel(units[0],color=c1)
    ax_s.set_ylabel(units[1])

    for i in range(2):
        [ax,ax_s][i].tick_params(axis='y', color=[c1,c0][i], labelcolor=[c1,c0][i])
        ax_s.spines[['left','right'][i]].set_edgecolor([c1,c0][i])
        ax_s.spines[['left','right'][i]].set_linewidth(2)
        ax.set_title('',loc='center')
    
    #a_b = gsw.alpha_on_beta(ds[right].mean('time'),ds[left].mean('time'),0).values
    #ds = 0.3
    #ss = 34.5
    #st = 13.5
    #ax_s.set_ylim(ss,ss+ds)
    #ax[2].set_ylim(st,st+(1/a_b)*ds)
    
def fix_xticks(ax,ds):
    
    if (ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 1 :
        ax[0].xaxis.set_minor_locator(mdates.MinuteLocator([0,30]))
        ax[0].xaxis.set_major_locator(mdates.HourLocator())
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        ax[-1].set_xlabel(f"{ds.time[0].values.astype('datetime64[D]')}")

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') > 1) and ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 7):
        ax[0].xaxis.set_minor_locator(mdates.HourLocator([0,12]))
        ax[0].xaxis.set_major_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') > 6) and ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 15):
        ax[0].xaxis.set_minor_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax[0].xaxis.set_major_locator(mdates.DayLocator(np.arange(2,32,2)))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        ax[0].xaxis.set_minor_formatter(mdates.DateFormatter(""))
        ax[-1].set_xlabel('2023')

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') > 14) and ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') < 31):
        ax[0].xaxis.set_minor_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax[0].xaxis.set_major_locator(mdates.DayLocator([5,10,15,20,25,30]))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        #ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%d"))

    if ((ds.time[-1] - ds.time[0]).data.astype('timedelta64[D]') > 30):
        ax[0].xaxis.set_major_locator(mdates.MonthLocator())
        ax[0].xaxis.set_minor_locator(mdates.DayLocator([1,5,10,15,20,25]))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%B"))
        ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    
    rot_ticks(ax[-1],0,'center')

##### Plot Kringla #####    

fig, ax = plt.subplots(4,1,figsize=(30,15),sharex=True,constrained_layout=True)

cbar_ax = ax[0].inset_axes([1.01, 0, 0.01, 1])
cbar_dx = ax[3].inset_axes([1.01, 0, 0.01, 1])

ds = sbk

#### Panel 1 ####
plot_line_sct(ds,ax[0],cbar_ax,'AirmarWindSpeed','AirmarWindDirection','AirmarWindGust',gusts=True)
ax[0].set_title(f"(a) {ds['AirmarWindSpeed'].attrs['long_name'].lower().capitalize()} and gusts",loc='left',x=0.01)

#### Panel 2 ####
ds['AirmarAirTemp'].plot(ax=ax[1], c=c1,lw=3)
ax[1].set_title(f"(b) {ds['AirmarAirTemp'].attrs['long_name'].lower().capitalize()}",loc='left',x=0.01)
ax[1].set_xlabel('')
ax[1].set_ylabel('(°C)')

#### Panel 3 ####
plot_surface(ds,ax[2],left = 'AADI_Temp', right = 'SA',units=['(°C)','(g kg$^{-1}$)'])
ax[2].set_title(f"(c) {ds['AADI_Temp'].attrs['long_name'].lower().capitalize()} and salinity",loc='left',x=0.01)

#### Panel 4 ####
plot_line_sct(ds,ax[3],cbar_dx,'DCPSSpeed','DCPSDirection','',gusts=False)
ax[3].set_title(f"(d) {sbpp['DCPSSpeed'].attrs['long_name'].lower().capitalize()} and direction",loc='left',x=0.01)

fig.suptitle('Sailbuoy Kringla',fontsize='xx-large')

fix_xticks(ax,ds)

plt.savefig('../../plots/SB1812_20230310.png')

##### Plot PimPim #####    

fig, ax = plt.subplots(4,1,figsize=(30,15),sharex=True,constrained_layout=True)

cbar_ax = ax[0].inset_axes([1.01, 0, 0.01, 1])
cbar_dx = ax[3].inset_axes([1.01, 0, 0.01, 1])

ds = sbpp

#### Panel 1 ####
plot_line_sct(ds,ax[0],cbar_ax,'FT_WindSpeed','FT_WindDir','FT_WindGust',gusts=True)
ax[0].set_title(f"(a) {ds['FT_WindSpeed'].attrs['long_name'].lower().capitalize()} and gusts",loc='left',x=0.01)

#### Panel 2 ####
plot_surface(ds,ax[1],left = 'T9602_T', right = 'T9602_H',units=['(°C)','(%)'])
ax[1].set_title(f"(b) {ds['T9602_T'].attrs['long_name'].lower().capitalize()} and relative humidity",loc='left',x=0.01)

#### Panel 3 ####
plot_surface(ds,ax[2],left = 'RBRL_T', right = 'RBRL_Sal',units=['(°C)','(PSU)'])
ax[2].set_title(f"(c) {ds['RBRL_T'].attrs['long_name'].lower().capitalize()} and salinity",loc='left',x=0.01)

#### Panel 4 ####
plot_line_sct(ds,ax[3],cbar_dx,'DCPSSpeed','DCPSDirection','',gusts=False)
ax[3].set_title(f"(d) {ds['DCPSSpeed'].attrs['long_name'].lower().capitalize()} and direction",loc='left',x=0.01)

fig.suptitle('Sailbuoy PimPim',fontsize='xx-large')

fix_xticks(ax,sbpp)
plt.savefig('../../plots/SB2326_20230310.png')


