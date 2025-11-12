# Import modules
import pandas as pd
import os

os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from fishingeffort import fishingeffort as fe
from constants import *

# VMS haul identification
vms = fe.read_all_data(os.path.join(vms_dir, 'raw'), file_type='.csv')

# Identifying fishing speeds
vms = vms[vms['Speed'] > 0]

vms_speed = fe.define_fishing_speed(df=vms, speed_column='Speed', mean_trawl=2, mean_nav=8)

vms_speed.to_csv(os.path.join(vms_dir, 'VMS_speed_limits.csv'))

# VMS interpolation
vms_int = fe.read_all_data(os.path.join(vms_dir, 'interpolation'), file_type='.csv')

# Identifying fishing speeds
vms_int = vms_int[vms_int['Speed'] > 0]

vms_int_speed = fe.define_fishing_speed(df=vms_int, speed_column='Speed', mean_trawl=2.6, mode='unimodal')

vms_int_speed.to_csv(os.path.join(vms_dir, 'VMS_int_speed_limits.csv'))
