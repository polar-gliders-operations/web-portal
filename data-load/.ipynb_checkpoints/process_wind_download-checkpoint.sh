#!/bin/sh

chmod +x /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/process_wind_download.sh

/Users/marcel/opt/anaconda3/bin/python /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/download_winds.py

mv sst*.nc ../../data/sst_latest.nc