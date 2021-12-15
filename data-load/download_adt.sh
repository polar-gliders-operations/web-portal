ymd=$(date +%Y%m%d)
mnth=$(date +%m)
yr=$(date +%Y)
wget -N ftp://mduplessis2:JurgenKlopp10*@nrt.cmems-du.eu/Core/SEALEVEL_GLO_PHY_L4_NRT_OBSERVATIONS_008_046/dataset-duacs-nrt-global-merged-allsat-phy-l4/${yr}/${mnth}/nrt_global_allsat_phy_l4_${ymd}_${ymd}.nc

count=`ls -1 nrt*.nc 2>/dev/null | wc -l`

if [ $count != 0 ]

then
    echo latest date stamp working

else
   ymd=$(date +%Y%m%d --date="1 days ago")
   mnth=$(date +%m --date="1 days ago")
   yr=$(date +%Y --date="1 days ago")
   wget -N ftp://mduplessis2:JurgenKlopp10*@nrt.cmems-du.eu/Core/SEALEVEL_GLO_PHY_L4_NRT_OBSERVATIONS_008_046/dataset-duacs-nrt-global-merged-allsat-phy-l4/${yr}/${mnth}/nrt_global_allsat_phy_l4_${ymd}_${ymd}.nc

fi