from simplekml import (Kml, OverlayXY, ScreenXY, Units, RotationXY,
                       AltitudeMode, Camera)
import numpy as np
import matplotlib.pyplot as plt
import cmocean.cm as cmo
import xarray as xr
import numpy as np
import gsw
import warnings
warnings.filterwarnings("ignore")

path = '../data/kmz/' # Path to figure folder 

def make_kml(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat,
             figs,name, colorbar=None, **kw):
    """TODO: LatLon bbox, list of figs, optional colorbar figure,
    and several simplekml kw..."""

    kml = Kml()
    altitude = kw.pop('altitude', 2e7)
    roll = kw.pop('roll', 0)
    tilt = kw.pop('tilt', 0)
    altitudemode = kw.pop('altitudemode', AltitudeMode.relativetoground)
    camera = Camera(latitude=np.mean([urcrnrlat, llcrnrlat]),
                    longitude=np.mean([urcrnrlon, llcrnrlon]),
                    altitude=altitude, roll=roll, tilt=tilt,
                    altitudemode=altitudemode)

    kml.document.camera = camera
    draworder = 0
    for fig in figs:  # NOTE: Overlays are limited to the same bbox.
        draworder += 1
        ground = kml.newgroundoverlay(name='GroundOverlay')
        ground.draworder = draworder
        ground.visibility = kw.pop('visibility', 1)
        ground.name = kw.pop('name', name[draworder-1])
        ground.color = kw.pop('color', '9effffff')
        ground.atomauthor = kw.pop('author', 'Johan Edholm')
        ground.latlonbox.rotation = kw.pop('rotation', 0)
        ground.description = kw.pop('description', 'Matplotlib figure')
        ground.gxaltitudemode = kw.pop('gxaltitudemode',
                                       'clampToSeaFloor')
        ground.icon.href = fig
        ground.latlonbox.east = llcrnrlon
        ground.latlonbox.south = llcrnrlat
        ground.latlonbox.north = urcrnrlat
        ground.latlonbox.west = urcrnrlon

    if colorbar:  # Options for colorbar are hard-coded (to avoid a big mess).
        screen = kml.newscreenoverlay(name='ScreenOverlay')
        screen.icon.href = colorbar
        screen.overlayxy = OverlayXY(x=0, y=0,
                                     xunits=Units.fraction,
                                     yunits=Units.fraction)
        screen.screenxy = ScreenXY(x=0.015, y=0.075,
                                   xunits=Units.fraction,
                                   yunits=Units.fraction)
        screen.rotationXY = RotationXY(x=0.5, y=0.5,
                                       xunits=Units.fraction,
                                       yunits=Units.fraction)
        screen.size.x = 0
        screen.size.y = 0
        screen.size.xunits = Units.fraction
        screen.size.yunits = Units.fraction
        screen.visibility = 1

    kmzfile = kw.pop('kmzfile', 'overlay.kmz')
    kml.savekmz(kmzfile)
    
def gearth_fig(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat, pixels=1024):
    """Return a Matplotlib `fig` and `ax` handles for a Google-Earth Image."""
    aspect = np.cos(np.mean([llcrnrlat, urcrnrlat]) * np.pi/180.0)
    xsize = np.ptp([urcrnrlon, llcrnrlon]) * aspect
    ysize = np.ptp([urcrnrlat, llcrnrlat])
    aspect = ysize / xsize

    if aspect > 1.0:
        figsize = (10.0 / aspect, 10.0)
    else:
        figsize = (10.0, 10.0 * aspect)

    if False:
        plt.ioff()  # Make `True` to prevent the KML components from poping-up.
    fig = plt.figure(figsize=figsize,
                     frameon=False,
                     dpi=pixels//10)
    # KML friendly image.  If using basemap try: `fix_aspect=False`.
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(llcrnrlon, urcrnrlon)
    ax.set_ylim(llcrnrlat, urcrnrlat)
    return fig, ax

def make_gearth_fig(ds,pixels):
    
    fig, ax = gearth_fig(llcrnrlon=ds.longitude.min(),
                         llcrnrlat=ds.latitude.min(),
                         urcrnrlon=ds.longitude.max(),
                         urcrnrlat=ds.latitude.max(),
                         pixels=pixels)
    return fig, ax

# Load the data
sst = xr.open_dataset('../data/sst_latest.nc').sel(lat=slice(-45,-30),lon=slice(0,25)).squeeze()
adt = xr.open_dataset('../data/adt_latest.nc').sel(latitude=slice(-45,-30),longitude=slice(0,25)).squeeze()
swath = xr.open_dataset('../data/calval_orbit.nc')
sst = sst.rename({'lon':'longitude','lat':'latitude'})

lons, lats = np.meshgrid(sst.longitude,sst.latitude)
diff_lons = gsw.distance(lons,lats)
diff_lats = gsw.distance(lons.T,lats.T).T

sst['gradient'] = (((sst['analysed_sst'].diff('latitude')/diff_lats)**2 + (sst['analysed_sst'].diff('longitude')/diff_lons)**2)**(1/2))*1000
adt['gos'] = (('latitude', 'longitude'), np.sqrt(adt.ugos**2+adt.vgos**2).data)

M1 = [16.049411,-37.157775]
M2 = [13.472228,-35.970445]

pixels = 1024 * 10

############################################
########## --- Plot SLA field --- ##########
############################################

fig, ax = make_gearth_fig(adt,pixels)

cs = ax.pcolormesh(adt.longitude,
                   adt.latitude,
                   adt.sla,
                   cmap=cmo.balance)
ax.set_axis_off()

fig.savefig(path + 'figures/sla_pcm_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values), transparent=False, format='png')
fig.savefig(path + 'figures/sla_pcm_latest.png', transparent=False, format='png')

#############################################
########## --- Plot GOS quiver --- ##########
#############################################

fig, ax = make_gearth_fig(adt,pixels)

Q = ax.quiver(adt.longitude,
              adt.latitude,
              adt.ugos,
              adt.vgos,
              scale=5e1,
              alpha=0.8,
              headaxislength=5,
              headlength=5,
              headwidth=5,
              width=1e-3,
              color='w')

ax.quiverkey(Q, 0.86, 0.45, 1, '1 m s$^{-1}$', labelpos='W')
ax.set_axis_off()

fig.savefig(path + 'figures/gos_quiver_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values), transparent=True, format='png')
fig.savefig(path + 'figures/gos_quiver_latest.png', transparent=False, format='png')

###############################################
########## --- Plot SLA contours --- ##########
###############################################

fig, ax = make_gearth_fig(adt,pixels)

cs = ax.contour(adt.longitude,
                adt.latitude,
                adt.sla.squeeze(),
                linewidths=0.75, 
                alpha=1,
                levels=np.arange(-2, 2, 0.1),
                colors='w')

ax.set_axis_off()

fig.savefig(path + 'figures/sla_contour_{}.png'.format(adt.time.dt.strftime("%Y%m%d").values), transparent=True, format='png')
fig.savefig(path + 'figures/sla_contour_latest.png', transparent=True, format='png')

###############################################
########## --- Plot SST gradient --- ##########
###############################################

fig, ax = make_gearth_fig(sst,pixels)

cs = ax.pcolor(sst.longitude,
               sst.latitude,
               sst.gradient,
               cmap=cmo.thermal,
               vmin=0,
               vmax=0.1)

ax.set_axis_off()

fig.savefig(path + 'figures/sst_gradient_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values), transparent=False, format='png')
fig.savefig(path + 'figures/sst_gradient_latest.png', transparent=False, format='png')

######################################
########## --- Plot SST --- ##########
######################################

fig, ax = make_gearth_fig(sst,pixels)

cs = ax.pcolor(sst.longitude,
               sst.latitude,
               sst.analysed_sst,
               cmap=cmo.thermal,
               vmin=15,
               vmax=25)

ax.set_axis_off()

fig.savefig(path + 'figures/sst_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values), transparent=False, format='png')
fig.savefig(path + 'figures/sst_latest.png', transparent=False, format='png')

##############################################
########## --- Plot SST anomaly --- ##########
##############################################

fig, ax = make_gearth_fig(sst,pixels)

cs = ax.pcolor(sst.longitude,
               sst.latitude,
               sst.analysed_sst - sst.analysed_sst.mean(),
               cmap=cmo.balance,
               vmin=-5,
               vmax=5)

ax.set_axis_off()

fig.savefig(path + 'figures/sst_anomaly_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values), transparent=False, format='png')
fig.savefig(path + 'figures/sst_anomaly_latest.png', transparent=False, format='png')

###########################################
########## --- Make KMZ-file --- ##########
###########################################

make_kml(llcrnrlon=adt.longitude.min().values, llcrnrlat=adt.latitude.min().values,
         urcrnrlon=adt.longitude.max().values, urcrnrlat=adt.latitude.max().values,
         figs=[path + 'figures/sla_pcm_latest.png',
               path + 'figures/gos_quiver_latest.png',
               path + 'figures/sla_contour_latest.png',
               path + 'figures/sst_gradient_latest.png',
               path + 'figures/sst_latest.png',
               path + 'figures/sst_anomaly_latest.png'],
         kmzfile=path + 'quicche_latest.kmz',
         name=['SLA',
               'GOS Quiver',
               'SLA Contours',
               'SST Gradient',
               'SST',
               'SST Anomaly'])

make_kml(llcrnrlon=adt.longitude.min().values, llcrnrlat=adt.latitude.min().values,
         urcrnrlon=adt.longitude.max().values, urcrnrlat=adt.latitude.max().values,
         figs=[path + 'figures/sla_pcm_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values),
               path + 'figures/gos_quiver_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values),
               path + 'figures/sla_contour_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values),
               path + 'figures/sst_gradient_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values),
               path + 'figures/sst_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values),
               path + 'figures/sst_anomaly_{}.png'.format(sst.time.dt.strftime("%Y%m%d").values)],
         kmzfile=path + 'quicche_{}.kmz'.format(sst.time.dt.strftime("%Y%m%d").values),
         name=['SLA',
               'GOS Quiver',
               'SLA Contours',
               'SST Gradient',
               'SST',
               'SST Anomaly'])