#!/bin/sh

chmod +x /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/process_wind_download.sh

rm *.hdf
rm *.nc
echo .hdf and .nc files deleted, starting sea ice.

/Users/marcel/opt/anaconda3/bin/python /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/download_seaice.py
echo sea ice code complete, now sst.

/Users/marcel/opt/anaconda3/bin/python /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/download_sst.py
echo sst code complete, now winds.

/Users/marcel/opt/anaconda3/bin/python /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/download_winds.py
echo wind code complete, now adt.

sh /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/download_adt.sh
echo adt code complete, now moving files.

sh /Users/marcel/Google\ Drive/Projects/PG-web-portal/web-portal/data-load/move_files.sh
echo moving files complete, end.