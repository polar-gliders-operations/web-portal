import wget
from datetime import datetime
import os

one = 'mduplessis2'
two = 'JurgenKlopp10*'
ftp = '@nrt.cmems-du.eu/Core/SEALEVEL_GLO_PHY_L4_NRT_OBSERVATIONS_008_046/dataset-duacs-nrt-global-merged-allsat-phy-l4/'
das = 'nrt_global_allsat_phy_l4_'

now = datetime.utcnow()
tday = now.strftime("%Y%m%d")
yr = now.strftime("%Y")
mnt = now.strftime("%m")
day = now.strftime("%d")

link = 'ftp://' + one + ':' + two + ftp + yr + '/' + mnt + '/' + das + tday + '_' + tday + '.nc'

path = '../data/'
filename = f'adt_{tday}.nc'

if os.path.exists(path + 'adt_latest.nc'):
    os.remove(path + 'adt_latest.nc') # if exist, remove it directly
if os.path.exists(path + filename):
    os.remove(path + filename) # if exist, remove it directly

wget.download(link,out = path + 'adt_latest.nc')
wget.download(link,out = path + filename)