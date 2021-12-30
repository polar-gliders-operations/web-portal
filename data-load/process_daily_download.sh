#!/bin/sh

chmod -R 777 /home/web/web-portal/
chmod +x /home/web/web-portal/data-load/process_daily_download.sh

echo .hdf and .nc files deleted, starting sea ice.

/home/web/miniconda3/envs/web/bin/python /home/web/web-portal/data-load/download_seaice.py
echo sea ice code complete, now sst.

/home/web/miniconda3/envs/web/bin/python /home/web/web-portal/data-load/download_sst.py
echo sst code complete, now winds.

/home/web/miniconda3/envs/web/bin/python /home/web/web-portal/data-load/download_winds.py
echo wind code complete, now adt.

sh /home/web/web-portal/data-load/download_adt.sh
echo adt code complete, now moving files.

sh /home/web/web-portal/data-load/move_files.sh
echo moving files complete, end.
