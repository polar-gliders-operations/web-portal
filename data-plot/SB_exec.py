import SB_download
import SB_load
import SB_plot
import pandas as pd
import time 

SB_download.dl_sb() # Download the data to the /home/web/web-portal/data folder
time.sleep(15)      # Just make sure it has time to download the files

pld = SB_load.load_pld(path='data.csv',start='2022-01-10 15:00') # Load the data-file

pld.Time.to_dataframe().drop('Distance',axis=1).to_csv('../data/SB_all_positions.csv',index=False) # Save the positions and time as a .csv

SB_plot.sb_plot(pld,path='img/Sailbuoy_plot.png')

print('Done, finally...')
