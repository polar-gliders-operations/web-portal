from ..SB_download import SB_download
import SB_load
import SB_plot

SB_download.dl_sb(which='uni')
pld = SB_load.load_pld(start='2021')
SB_plot.sb_plot(pld,path='../public/img/Sailbuoy_plot.png')