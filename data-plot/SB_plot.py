# ------------------- Import Modules and Packages --------------------
# --------------------------------------------------------------------
# Ignore deprecation warnings
# import warnings
# warnings.filterwarnings('ignore')
# Import modules and packages
from matplotlib import pyplot as plt
import numpy as np
import matplotlib as mpl
import xarray as xr
import pandas as pd
import datetime
import matplotlib.dates as mdates
import cmocean as cmo
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import gsw
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import glidertools as gt
import matplotlib.gridspec as gridspec
import seaborn as sns
from tqdm import tqdm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from tqdm.notebook import tqdm_notebook
from matplotlib.projections import get_projection_class
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
import SB_load

pd.set_option('display.max_columns', 1000)
mpl.rcParams['font.size'] = 20

# cyclic_colorbar
# SB_plot

def cyclic_colorbar(cax,cmap):
    
    """
    Create a colorbar that shows 4 directions on a circle. I.e., north, east, south, and west.
    
    
    parameters
    ----------------
    ax: the axes the colorbar will be plotted in. Advisable to create you own, and place them smart.
    cmap: colormap or list of colours to split
    
    """
    
    azimuths = np.arange(0, 361, 1)
    zeniths = np.arange(40, 70, 1)
    values = azimuths * np.ones((30, 361))


    #ax1 = fig.add_subplot(1,5,5, polar=True)
    #ax1 = plt.subplots(subplot_kw=dict(projection='polar'))

    cax.pcolormesh(azimuths*np.pi/180.0, zeniths, values, cmap=cmap,shading='auto')
    cax.set_theta_zero_location("N")
    cax.set_theta_direction(-1)
    cax.set_yticks([])
    cax.set_xticks([0,90*np.pi/180.0,180*np.pi/180.0,270*np.pi/180.0])
    cax.set_xticklabels(['N','E','S','W'])

    cax.plot(np.linspace(0, 2*np.pi, 100), np.ones(100)*39, color='k', linestyle='-',lw=1.5,zorder=5)
    cax.plot(np.linspace(0, 2*np.pi, 100), np.ones(100)*51, color='k', linestyle='-',lw=2,zorder=5)

    cax.set_rmin(30)
    cax.set_rmax(51)



def sb_plot(pld,path='SB_plots.png'):
    fig,ax = plt.subplots(7,1,figsize=(20,25),sharex=True,constrained_layout=True,facecolor='w')

    cyclic = [[],[],[],[],[],[],[],[]]
    colours = ListedColormap([[0.00392156862745098, 0.45098039215686275, 0.6980392156862745],
                          [0.8705882352941177, 0.5607843137254902, 0.0196078431372549],
                          [0.00784313725490196, 0.6196078431372549, 0.45098039215686275],
                          [0.8, 0.47058823529411764, 0.7372549019607844]])
    #test = ListedColormap(['C0',  'k', "#9EB0A7", 'gold']) # Estel's colours"#74A757"

    for i in range(3):
        cyclic[1 + 2*i] = colours(1+i)
        cyclic[2 + 2*i] = colours(1+i)

    cyclic[0] = colours(0)
    cyclic[7] = colours(0)

    cyclic_NESW = ListedColormap(cyclic)
    
    var = [['AirmarAirTemp'],                                 # Variables for first panel
           ['AADI_Temp'],
           ['SSS'],                                           # ------------- second ----
           ['AirmarWindSpeed'],                               # ------------- third  ----
           ['DCPSSpeed'],                                     # ------------- fourth ----
           ['AirmarWindDirection'],                           # ------------- fifth  ----
           ['DCPSDirection']]                                 # ------------- sixth  ----

    labels = [['Air temperature'],
              ['Sea surface temperature'],  # Labels for first panel
              ['Sea surface salinity'],                       # ---------- second ----
              ['Wind speed and gust'],                        # ---------- third  ----
              ['Surface current speed'],                      # ---------- fourth ----
              ['Wind direction'],                             # ---------- fifth  ----
              ['Current direction']]                          # ---------- sixth  ----

    units = ['°C','°C',                                            # Units for first panel
             'g kg$^{-1}$',                                   # --------- second ----        
             'm s$^{-1}$',                                    # --------- third  ----        
             'm s$^{-1}$',                                    # --------- fourth ----        
             'Latitude',                                      # --------- fifth  ----             
             'Latitude']                                      # --------- sixth  ----      


    c = [['C1'],
         ['C0'],                                         # Units for first panel    
         ['C0'],                                              # --------- second ----   
         ['C1'],                                              # --------- third  ----  
         ['C0'],                                              # --------- fourth ----       
         ['C1'],                                              # --------- fifth  ---- 
         ['C0']]                                              # --------- sixth  ----  
    
    for i in range(7):
        count = 0

        for variable in var[i]:

            if i < 5:

                mask = np.where(~np.isnan(pld[variable]))[0]
                temp = pld[variable][mask]

                if 'Airmar' in variable:

                    msk = np.where(pld['AirmarAirFix'][mask]==1)[0]
                    temp = temp[msk]

                if 'DCPS' in variable:

                    msk = np.where(pld['DCPSStatus'][mask]==0)[0]
                    temp = temp[msk]

                ax[i].plot(temp.Time,temp,zorder=3,c=c[i][count],label=labels[i][count],lw=2)

                count += 1

            if i > 4:
                mask = np.where(~np.isnan(pld[variable]))[0]
                temp = pld[variable][mask]
                ax[i].scatter(temp.Time.values,temp.Lat,c=temp,cmap=cyclic_NESW,label=labels[i][0])
                ax[i].set_ylim(temp.Lat.min()-temp.Lat.std(),temp.Lat.max()+temp.Lat.std())
                ax[i].yaxis.set_major_formatter(LatitudeFormatter(dms=True))
        if i < 2:
            ax[i].legend(fancybox=True,ncol=2,loc='upper left',shadow=True,framealpha=1,handletextpad=0.2,handlelength=0.75,columnspacing=0.5) 
        if i > 1:
            ax[i].legend(fancybox=True,ncol=2,loc='lower left',shadow=True,framealpha=1,handletextpad=0.2,handlelength=0.75) 
        ax[i].set_ylabel(units[i])

    ax[3].fill_between(pld['AirmarWindGust'].Time[msk].values, pld['AirmarWindSpeed'][msk],pld['AirmarWindGust'][msk],fc='C1',ec=None,alpha=0.4)

    cax1 = inset_axes(ax[5],width='6%',height='25%' ,axes_class=get_projection_class("polar"),loc='center left') # fig.add_axes([0.94, 0.275, 0.04, .04],polar=True)
    cax2 = inset_axes(ax[6],width='6%',height='25%' ,axes_class=get_projection_class("polar"),loc='center left') # fig.add_axes([0.94, 0.275, 0.04, .04],polar=True)

    cyclic_colorbar(cax1,cyclic_NESW)
    cyclic_colorbar(cax2,cyclic_NESW)
    
    #ax[0].set_ylim(np.min([np.min(pld.AADI_Temp),np.min(pld.AirmarAirTemp)])-1,np.max([np.max(pld.AADI_Temp),np.max(pld.AirmarAirTemp)])+1)
    ax[4].set_ylim(0,0.8)

    if (pld.Time[-1] - pld.Time[0]).data.astype('timedelta64[D]') < 7 :
        ax[0].xaxis.set_minor_locator(mdates.HourLocator([0,12]))
        ax[0].xaxis.set_major_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%H:%M"))
        
    if ((pld.Time[-1] - pld.Time[0]).data.astype('timedelta64[D]') > 6) and ((pld.Time[-1] - pld.Time[0]).data.astype('timedelta64[D]') < 15):
        ax[0].xaxis.set_minor_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax[0].xaxis.set_major_locator(mdates.DayLocator(np.arange(2,32,2)))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        ax[0].xaxis.set_minor_formatter(mdates.DateFormatter(""))
        ax[6].set_xlabel('January')
    
    if ((pld.Time[-1] - pld.Time[0]).data.astype('timedelta64[D]') > 14) and ((pld.Time[-1] - pld.Time[0]).data.astype('timedelta64[D]') < 31):
        ax[0].xaxis.set_minor_locator(mdates.DayLocator(np.arange(1,32,1)))
        ax[0].xaxis.set_major_locator(mdates.DayLocator([5,10,15,20,25,30]))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%b"))
        #ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
        
    if ((pld.Time[-1] - pld.Time[0]).data.astype('timedelta64[D]') > 30):
        ax[0].xaxis.set_major_locator(mdates.MonthLocator())
        ax[0].xaxis.set_minor_locator(mdates.DayLocator([1,10,20]))
        ax[0].xaxis.set_major_formatter(mdates.DateFormatter("%d\n%B"))
        ax[0].xaxis.set_minor_formatter(mdates.DateFormatter("%d"))
    
    ax[0].axhline(0,ls='--',lw=1,c='k')
    ax[1].axhline(0,ls='--',lw=1,c='k')
    ax[0].tick_params(axis="x", which="both", length=4)   
    plt.setp(ax[0].get_xticklabels(), rotation=0, ha="center")

    plt.savefig(path,dpi=150)
    