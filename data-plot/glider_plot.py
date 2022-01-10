import numpy as np
import xarray as xr
import glidertools as gt
import os
import cmocean.cm as cmo
import hvplot.xarray
import matplotlib.pyplot as plt

# open glider files
glid_folder = '/mnt/data/sg675/'

names = [
    'ctd_depth',
    'ctd_time',
    'ctd_pressure',
    'salinity',
    'temperature',
    'aanderaa4831_dissolved_oxygen',
    'eng_wlbb2fl_FL1sig'
    ]

ds_dict = gt.load.seaglider_basestation_netCDFs(os.path.join(glid_folder,'p*.nc'), names, return_merged=True, keep_global_attrs=False)
ds_640 = ds_dict['sg_data_point']
ds_640 = ds_640.rename({'aanderaa4831_dissolved_oxygen':'oxygen',
                        'eng_wlbb2fl_FL1sig':'fluorescence'
                       })


latest_dive = ds_640.where(ds_640.dives==ds_640.dives.max())
latest_dive_plot=latest_dive.hvplot(y=['temperature','salinity','fluorescence','oxygen'], x='ctd_pressure', invert=True,flip_yaxis=True, shared_axes=False,
                 subplots=True, width=250, height=400,grid=True,line_width=3).cols(4)

hvplot.save(latest_dive_plot, 'img/profiles.html')


dive_time=gt.utils.time_average_per_dive(ds_640.dives,ds_640.ctd_time)

from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica'],'size':16})
params = {'mathtext.default': 'regular' }          
plt.rcParams.update(params)

fig, ax = plt.subplots(4, figsize=[12, 12])

gt.plot(dive_time, ds_640.ctd_depth, ds_640.temperature,
        cmap=cmo.thermal, robust=True, ax=ax[0])

gt.plot(dive_time, ds_640.ctd_depth, ds_640.salinity,
        cmap=cmo.haline, robust=True, ax=ax[1])

gt.plot(dive_time, ds_640.ctd_depth, ds_640.fluorescence, 
        cmap=cmo.delta, robust=True,ax=ax[2])

gt.plot(dive_time, ds_640.ctd_depth, ds_640.oxygen, 
        cmap=cmo.oxy,robust=True, ax=ax[3])

ax[0].cb.set_label('temperature', labelpad=15)
ax[1].cb.set_label('salinity', labelpad=15)
ax[2].cb.set_label('fluorescence_raw', labelpad=20)
ax[3].cb.set_label('dissolved_oxygen', labelpad=20)

for i in range(3):  
    ax[i].set_xlabel('')

for i in range(4):  
    ax[i].set_title('')
    ax[i].set_ylim(400, 0)

# ax[0].set_title('SG662')

fig.autofmt_xdate()
fig.subplots_adjust(hspace=0.45)

plt.savefig('img/sg640_sections.png', dpi=300, bbox_inches='tight', transparent=True)
