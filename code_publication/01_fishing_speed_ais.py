# Import modules
import pandas as pd
import os

os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from fishingeffort import fishingeffort as fe
from constants import *

# AIS haul identification
ais = fe.read_all_data(os.path.join(ais_dir, 'raw'), file_type='.csv')

# Sample every minute to reduce the memory usage
ais = fe.data_reduction_min(df=ais, datetime_column='Date_time', name_column='Dummy_ID',
                            additional_columns=['Latitude', 'Longitude', 'Speed', 'AIS_Harbor'])

fe.save_df(ais, file='AIS_data_min.csv', dir_output=os.path.join(ais_dir, 'processed'))

# Identify trawling speeds
ais = ais[ais['Speed'] > 0]

ais_speed = fe.define_fishing_speed(df=ais, speed_column='Speed', mean_trawl=2, mean_nav=8)

ais_speed.to_csv(os.path.join(ais_dir, 'AIS_speed_limits.csv'))
