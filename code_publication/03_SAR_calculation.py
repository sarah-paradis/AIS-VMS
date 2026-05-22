import os

import pandas as pd

os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from constants import *
from fishingeffort import fishingeffort as fe
import numpy as np
import rasterio
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

print('Reading data')
ais = gpd.read_file(os.path.join(ais_dir, 'processed', 'ais_hauls.shp'))
vms = gpd.read_file(os.path.join(vms_dir, 'processed', 'vms_hauls.shp'))

bounds = best_bounding_box(ais, vms)


print(f'Calculating fishing effort of AIS data')
fe.swept_area_ratio(grid_size=grid,
                    gdf=ais,
                    file_name=f'SAR_ais_{grid}.tif',
                    gear_width=100, bounds=bounds,
                    dir_out=os.path.join(ais_dir, 'processed'),
                    crs=ais.crs)

print(f'Calculating fishing effort of VMS data')
fe.swept_area_ratio(grid_size=grid,
                    gdf=vms,
                    file_name=f'SAR_vms_{grid}.tif',
                    gear_width=100, bounds=bounds,
                    dir_out=os.path.join(vms_dir, 'processed'),
                    crs=ais.crs)

# Calculate difference between AIS and VMS
with rasterio.open(os.path.join(ais_dir, 'processed', f'SAR_ais_{grid}.tif')) as src:
    ais_fe = src.read(1)
    ais_fe = np.where(np.isnan(ais_fe), 0, ais_fe)
with rasterio.open(os.path.join(vms_dir, 'processed', f'SAR_vms_{grid}.tif')) as src:
    vms_fe = src.read(1)
    vms_fe = np.where(np.isnan(vms_fe), 0, vms_fe)
    meta = src.meta

ais_vms = vms_fe - ais_fe

with rasterio.open(os.path.join(file_dir, f'SAR_ais_vms_{grid}.tif'), 'w', **meta) as src_out:
    src_out.write(ais_vms, 1)

grids = [100, 200, 500, 1000, 2000, 3000, 4000, 5000]

for grid in grids:
    # SAR calculation for each fishing fleet
    for harbor in ['BLANES', 'PALAMOS']:

        print(f'Calculating SAR for {harbor} fishing fleet at {grid} m resolution')
        ais_harbor = ais[ais['AIS_Harbor'] == harbor]
        vms_harbor = vms[vms['VMS_Harbor'] == harbor]

        print(f'Calculating fishing effort of AIS data')
        fe.swept_area_ratio(grid_size=grid,
                            gdf=ais_harbor,
                            file_name=f'SAR_ais_{harbor}_{grid}.tif',
                            gear_width=100, bounds=bounds,
                            dir_out=os.path.join(ais_dir, 'processed'),
                            crs=ais_harbor.crs)

        print(f'Calculating fishing effort of VMS data')
        fe.swept_area_ratio(grid_size=grid,
                            gdf=vms_harbor,
                            file_name=f'SAR_vms_{harbor}_{grid}.tif',
                            gear_width=100, bounds=bounds,
                            dir_out=os.path.join(vms_dir, 'processed'),
                            crs=vms_harbor.crs)

        # Calculate difference between AIS and VMS
        with rasterio.open(os.path.join(ais_dir, 'processed', f'SAR_ais_{harbor}_{grid}.tif')) as src:
            ais_fe = src.read(1)
            ais_fe = np.where(np.isnan(ais_fe), 0, ais_fe)
        with rasterio.open(os.path.join(vms_dir, 'processed', f'SAR_vms_{harbor}_{grid}.tif')) as src:
            vms_fe = src.read(1)
            vms_fe = np.where(np.isnan(vms_fe), 0, vms_fe)
            meta = src.meta

        ais_vms = vms_fe - ais_fe

        with rasterio.open(os.path.join(file_dir, f'SAR_ais_vms_{harbor}_{grid}.tif'), 'w', **meta) as src_out:
            src_out.write(ais_vms, 1)


