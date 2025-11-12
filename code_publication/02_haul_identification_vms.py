# Identification of hauls using algorithm (Paradis et al., 2021)

# Import modules
import pandas as pd
import os

os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
import fishingeffort.fishingeffort as fe
from constants import *

# VMS haul identification
vms = fe.read_all_data(file_dir=os.path.join(vms_dir, 'interpolation'),
                       file_type='.csv')

# 3. Identify trawling activity based on speed

df_trawl, cnt = fe.identify_fishing(df=vms, datetime_column='Date_time', name_column='Dummy_ID',
                                    speed_column='Speed',
                                    min_trawl_speed=min_speed_vms, max_trawl_speed=max_speed_vms,
                                    min_nav_speed=min_nav_speed,
                                    max_duration_false_negative=max_duration_false_negative_vms,
                                    min_haul=min_haul,
                                    max_duration_false_positive=max_duration_false_positive_vms,
                                    turn_off_time=turn_off_time,
                                    remove_no_hauls=False)


fe.save_df(df_trawl, file='VMS_trawl_id.csv', dir_output=os.path.join(vms_dir, 'processed'))


# 4. Convert point to line based on Haul id
df_trawl['Date_day'] = pd.to_datetime(df_trawl['Date_time']).dt.date

# Clip out data within the study area before saving
pol_study_area = gpd.read_file(study_area)

gdf_hauls = fe.point_to_line(df=df_trawl, latitude='Latitude', longitude='Longitude', name_column='Dummy_ID',
                             haulid_column='Haul id', date_column='Date_day', input_crs='epsg:4326',
                             output_crs=pol_study_area.crs)

gdf_hauls['Date_day'] = gdf_hauls['Date_day'].astype(str)

ancillary_data_vms = vms[['Dummy_ID', 'VMS_Harbor']]
ancillary_data_vms.drop_duplicates(inplace=True)

gdf_hauls = pd.merge(left=gdf_hauls, right=ancillary_data_vms, left_on='Dummy_ID', right_on='Dummy_ID', how='left')

if pol_study_area.crs != gdf_hauls.crs:
    gdf_hauls.to_crs(pol_study_area.crs, inplace=True)
assert gdf_hauls.crs == pol_study_area.crs
gdf_hauls = gdf_hauls.clip(pol_study_area)

gdf_hauls.to_file(os.path.join(vms_dir, 'processed', 'vms_hauls.shp'),
                  index=False, driver='ESRI Shapefile')
