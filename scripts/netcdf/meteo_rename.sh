# cdo expr,Tdewmean=d2m-273.15 africa_era5-land_daily_d2m-average_rempacon-150-arcsec_daily.nc africa_era5-land_daily_d2m-average_rempacon-150-arcsec_daily_fin.nc
cdo expr,Tdewmax=d2m-273.15 africa_era5-land_daily_d2m-maximum_rempacon-150-arcsec_daily.nc africa_era5-land_daily_d2m-maximum_rempacon-150-arcsec_daily_fin.nc
cdo expr,Tdewmin=d2m-273.15 africa_era5-land_daily_d2m-minimum_rempacon-150-arcsec_daily.nc africa_era5-land_daily_d2m-minimum_rempacon-150-arcsec_daily_fin.nc
# cp africa_era5-land_daily_fal-average_rempacon-150-arcsec_daily.nc africa_era5-land_daily_fal-average_rempacon-150-arcsec_daily_fin.nc
cdo chname,sp,Surfpress africa_era5-land_daily_spressu-avg_rempacon-150-arcsec_daily.nc africa_era5-land_daily_spressu-avg_rempacon-150-arcsec_daily_fin.nc
cdo expr,tmoy=t2m-273.15 africa_era5-land_daily_t2m-average_rempacon-150-arcsec_daily.nc africa_era5-land_daily_t2m-average_rempacon-150-arcsec_daily_fin.nc
cdo expr,tmax=t2m-273.15 africa_era5-land_daily_t2m-maximum_rempacon-150-arcsec_daily.nc africa_era5-land_daily_t2m-maximum_rempacon-150-arcsec_daily_fin.nc
cdo expr,tmin=t2m-273.15 africa_era5-land_daily_t2m-minimum_rempacon-150-arcsec_daily.nc africa_era5-land_daily_t2m-minimum_rempacon-150-arcsec_daily_fin.nc
# cp africa_era5-land_daily_total-preci_rempacon-150-arcsec_daily.nc africa_era5-land_daily_total-preci_rempacon-150-arcsec_daily_fin.nc
cdo expr,srad=ssr/1000000 africa_era5-land_daily_total-ssrad_rempacon-150-arcsec_daily.nc africa_era5-land_daily_total-ssrad_rempacon-150-arcsec_daily_fin.nc
cdo chname,wind_speed_10m,wind africa_era5-land_daily_wind10m-avg_rempacon-150-arcsec_daily.nc africa_era5-land_daily_wind10m-avg_rempacon-150-arcsec_daily_fin.nc
cdo chname,pr,rain pr_W5E5v2.0_1981-2019_mm_per_day_africa_downscaled_with_chirps.nc pr_W5E5v2.0_1981-2019_mm_per_day_africa_downscaled_with_chirps_fin.nc

