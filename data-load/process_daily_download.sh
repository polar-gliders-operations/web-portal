#!/bin/sh

chmod -R 777 /home/mduplessis/web-portal/
chmod +x /home/mdplessis/web-portal/web-portal/data-load/process_daily_download.sh

echo .hdf and .nc files deleted, starting sea ice.

/opt/anaconda3/bin/python /home/mduplessis/web-portal/web-portal/data-load/download_seaice.py
echo sea ice code complete, now sst.

/opt/anaconda3/bin/python /home/mduplessis/web-portal/web-portal/data-load/download_sst.py
echo sst code complete, now winds.

/opt/anaconda3/bin/python /home/mduplessis/web-portal/web-portal/data-load/download_winds.py
echo wind code complete, now adt.

sh /home/mduplessis/web-portal/web-portal/data-load/download_adt.sh
echo adt code complete, now moving files.

sh /home/mduplessis/web-portal/web-portal/data-load/move_files.sh
echo moving files complete, end.
