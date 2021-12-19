import xarray as xr
from tqdm.notebook import trange, tqdm
from matplotlib.animation import FuncAnimation
import cartopy
import cmocean.cm as cmo
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from urllib.request import urlopen# start the client
import numpy as np

# adjust_lon_xr_dataset
# cartopy_era5_animation
# make_cmap

def adjust_lon_xr_dataset(ds, lon_name='longitude'):
    
    # whatever name is in the data - lon_name = 'lon'  

    # Adjust lon values to make sure they are within (-180, 180)
    ds['_longitude_adjusted'] = xr.where(
        ds[lon_name] > 180,
        ds[lon_name] - 360,
        ds[lon_name])
    
    # reassign the new coords to as the main lon coords
    # and sort DataArray using new coordinate values
    ds = (
        ds
        .swap_dims({lon_name: '_longitude_adjusted'})
        .sel(**{'_longitude_adjusted': sorted(ds._longitude_adjusted)})
        .drop(lon_name))
    
    ds = ds.rename({'_longitude_adjusted': lon_name})
    
    return ds

def cartopy_era5_animation(ds, vmin, vmax, cmap=cmo.thermal, out_name='t2m', out_type='.mp4', var_label='Air temperature ($^{\circ}$C)', fps=25, dpi=200, interval=200, save_animation=True, plot_wg=True, vector_plot=False):
    
    # Setup the initial plot
    fig = plt.figure(figsize=(5, 5))
    ax  = fig.add_subplot(projection=ccrs.NearsidePerspective(satellite_height=2000000.0, 
                                                              central_longitude=-15, 
                                                              central_latitude=-52
                                                             )
                         )
    
    ax.coastlines(resolution='110m')
    
    # Set up levels etc in this call
    image = ds.sel(time=ds.time[0].values).plot(ax=ax, 
                                                vmin=vmin, vmax=vmax, 
                                                cmap=cmap,
                                                cbar_kwargs={'orientation': 'horizontal',
                                                             'aspect': 30,
                                                             'shrink': 0.73,
                                                             'pad': 0.03,
                                                             'label': var_label
                                                            },
                                                transform=ccrs.PlateCarree(),                                               
                                               )

    
    if plot_wg:
        ax.scatter(0, -54, s=50, marker='*', c='k', transform=ccrs.PlateCarree()) 
        
        
    def update(t):
        ax.set_title("time = %s"%str(t)[:13])
        image.set_array(ds.sel(time=t))
        return image,
       
        
    # Run the animation, applying `update()` for each of the times in the variable
    anim = FuncAnimation(fig, 
                         update, 
                         frames=tqdm(ds.time.values),
                         blit=True,
                         interval=interval
                        )

    
    # Save to file or display on screen
    if save_animation:
        anim.save('../animations/'+str(out_name)+str(out_type), 
                  fps=fps, 
    #               extra_args=['-vcodec', 'libx264'],
                  dpi=dpi,
                 ) 
        
    return

###########################################################################################################################

def cartopy_era5_animation_vector(ds, color_var, vmin, vmax, cmap=cmo.thermal, out_name='t2m', out_type='.mp4', var_label='Air temperature ($^{\circ}$C)', fps=25, dpi=200, interval=200, save_animation=True, plot_wg=True):
    
    # Setup the initial plot
    fig = plt.figure(figsize=(5, 5))
    ax  = fig.add_subplot(projection=ccrs.NearsidePerspective(satellite_height=2000000.0, 
                                                              central_longitude=-15, 
                                                              central_latitude=-52
                                                             )            
                         )
    
    ax.coastlines(resolution='110m')
    
    # Set up levels etc in this call
    image = ds[color_var].sel(time=ds.time[0].values).plot(ax=ax, 
                                                           vmin=vmin, vmax=vmax, 
                                                           cmap=cmap,
                                                           cbar_kwargs={'orientation': 'horizontal',
                                                                        'aspect': 30,
                                                                        'shrink': 0.73,
                                                                        'pad': 0.03,
                                                                        'label': var_label
                                                                       },
                                                           transform=ccrs.PlateCarree(),                                               
                                                          )

    ds_vctrs = ds.sel(longitude=ds.longitude[::5], latitude=ds.latitude[::5])
    
    
    vctrs = ds_vctrs.sel(time=ds.time[0].values).plot.quiver(ax=ax,
                                                             x='longitude', y='latitude',                                               
                                                             u='u10', v='v10',
                                                             scale=5e2,
                                                             transform=ccrs.PlateCarree()
                                                            )
  
    if plot_wg:
        ax.scatter(0, -54, s=50, marker='*', c='k', transform=ccrs.PlateCarree())   
        
    def update(t):
        
        ax.set_title("time = %s"%str(t)[:13])
        
        image.set_array(ds[color_var].sel(time=t))

#         u = ds_vctrs.sel(time=t)['u10']
#         v = ds_vctrs.sel(time=t)['v10']
        
#         vctrs.set_UVC(
#                       u, v
#                      )
                
        return image,
     
    # Run the animation, applying `update()` for each of the times in the variable
    anim = FuncAnimation(fig, 
                         update, 
                         frames=tqdm(ds.time.values),
                         blit=False,
                         interval=interval
                        )

    
    # Save to file or display on screen
    if save_animation:
        anim.save('../animations/'+str(out_name)+str(out_type), 
                  fps=fps, 
                  dpi=dpi,
                 ) 
        
    return


##############################################################################################################################

def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    '''
    import matplotlib as mpl
    import numpy as np
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = mpl.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return cmap