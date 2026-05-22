# Calculation of pressure indicators as established by ICES: average intensity, proportion of grid cells fished,
# proportion of area fished, aggregation of fishing pressure

import os
import pandas as pd

os.environ['USE_PYGEOS'] = '0'
import geopandas as gpd
from constants import *
import numpy as np
import rasterio
from rasterio.mask import mask


# Intensity:
# Average number of times the area is swept by bottom-contacting fishing gears. Estimated as the sum of
# swept area for all vessels using bottom-contacting gears or by métier divided by the total area of the considered
# area (regional/ subregional sea, or broadscale habitat type within that sea).


def average_intensity(raster_file, study_area):
    """
    Indicator 1: Fishing intensity
    Mean SAR across all valid cells.

    Parameters
    ----------
    raster_file : file of SAR
    study_area : vector of study area

    Returns
    -------
    float
        Mean SAR (average number of sweeps).
    """
    if isinstance(study_area, str):
        study_area = gpd.read_file(study_area)
    elif isinstance(study_area, gpd.GeoDataFrame):
        study_area = study_area
    # Mask by the study area
    with rasterio.open(raster_file) as src:
        # Ensure both datasets are in the same CRS
        if study_area.crs != src.crs:
            study_area = study_area.to_crs(src.crs)
        # Extract the geometries from the GeoDataFrame
        geometries = study_area.geometry.values
        # Mask the raster
        out_image, out_transform = mask(dataset=src, shapes=geometries, crop=True, nodata=0)
        data = out_image

    return np.nanmean(data)


def proportion_grids_fished(raster_file, threshold, study_area):
    """
        Indicator 2: Proportion of grid cells fished

        Parameters
        ----------
        raster_file : file of SAR
        threshold : float
            Minimum SAR considered as fished.
        study_area : vector of study area

        Returns
        -------
        float
            Proportion of cells fished (0-1).
        """

    if isinstance(study_area, str):
        study_area = gpd.read_file(study_area)
    elif isinstance(study_area, gpd.GeoDataFrame):
        study_area = study_area
    # Mask by the study area
    with rasterio.open(raster_file) as src:
        # Ensure both datasets are in the same CRS
        if study_area.crs != src.crs:
            study_area = study_area.to_crs(src.crs)
        # Extract the geometries from the GeoDataFrame
        geometries = study_area.geometry.values
        # Mask the raster
        out_image, out_transform = mask(dataset=src, shapes=geometries, crop=True, nodata=0)
        data = out_image

    total_cells = data.shape[1] * data.shape[2]
    fished_cells = np.sum(data > threshold)

    proportion = fished_cells / total_cells
    assert 0 <= proportion <= 1
    return proportion


def proportion_area_fished(raster_file, study_area):
    """
    Indicator 3: Proportion of area fished

    Uses:
        min(SAR, 1)

    Parameters
    ----------
    raster_file : file of SAR
    study_area : vector of study area

    Returns
    -------
    float
        Proportion of area fished (0-1).
    """
    if isinstance(study_area, str):
        study_area = gpd.read_file(study_area)
    elif isinstance(study_area, gpd.GeoDataFrame):
        study_area = study_area
    # Mask by the study area
    with rasterio.open(raster_file) as src:
        # Ensure both datasets are in the same CRS
        if study_area.crs != src.crs:
            study_area = study_area.to_crs(src.crs)
        # Extract the geometries from the GeoDataFrame
        geometries = study_area.geometry.values

        # Mask the raster
        out_image, out_transform = mask(dataset=src, shapes=geometries, crop=True, nodata=0)
        data = out_image

    fished_cells = np.minimum(data, 1.0)

    proportion = np.nanmean(fished_cells)
    assert 0 <= proportion <= 1

    return proportion


def aggregation_fishing_pressure(raster_file, study_area):
    """
    Indicator 4: Aggregation of fishing pressure

    Smallest proportion of cells containing 90%
    of total SAR.

    Parameters
    ----------
    raster_file : file of SAR
    study_area : vector of study area

    Returns
    -------
    float
        Proportion of cells containing 90% of fishing pressure (0-1).
    """

    if isinstance(study_area, str):
        study_area = gpd.read_file(study_area)
    elif isinstance(study_area, gpd.GeoDataFrame):
        study_area = study_area

    # Mask by the study area
    with rasterio.open(raster_file) as src:
        # Ensure both datasets are in the same CRS
        if study_area.crs != src.crs:
            study_area = study_area.to_crs(src.crs)
        # Extract the geometries from the GeoDataFrame
        geometries = study_area.geometry.values

        # Mask the raster
        out_image, out_transform = mask(dataset=src, shapes=geometries, crop=True, nodata=0)
        data = out_image

    # Flatten your 2D study grid into a 1D array
    flat_data = data.flatten()
    # Sort descending
    sorted_sar = np.sort(flat_data)[::-1]

    cumulative = np.nancumsum(sorted_sar)

    total = cumulative[-1]

    threshold_90 = 0.9 * total

    n_cells_90 = np.searchsorted(cumulative, threshold_90) + 1

    total_cells = data.shape[1] * data.shape[2]

    proportion = n_cells_90 / total_cells
    assert 0 <= proportion <= 1

    return proportion


# Analysis by harbor and grid

columns = ['Harbor',
           'Dataset',
           'Grid size (m)',
           'Average intensity',
           'Proportion of grid cells fished',
           'Proportion of area fished',
           'Aggregation of fishing pressure']

grids = [100, 200, 500, 1000, 2000, 3000, 4000, 5000]
harbors = ['BLANES', 'PALAMOS']
datasets = ['ais', 'vms']

df = pd.DataFrame(columns=columns, index=list(range(len(grids) * len(harbors) * len(datasets))))

idx = 0
for grid in grids:
    for harbor in harbors:
        for dataset in datasets:
            print(f'Calculating fishing effort indicators for {harbor} {dataset} at {grid} m resolution')
            df.loc[idx, 'Harbor'] = harbor
            df.loc[idx, 'Dataset'] = dataset.upper()
            df.loc[idx, 'Grid size (m)'] = grid
            df.loc[idx, 'Average intensity'] = average_intensity(raster_file=os.path.join(r'../data_publication', dataset.upper(),
                                                                                          'processed',
                                                                                          f'SAR_{dataset}_{harbor}_{grid}.tif'),
                                                                 study_area=os.path.join(
                                                                     r'../constants',
                                                                     f'{harbor.lower()}.shp')
                                                                 )
            df.loc[idx, 'Proportion of grid cells fished'] = proportion_grids_fished(raster_file=os.path.join(r'../data_publication',
                                                                                                              dataset.upper(),
                                                                                                              'processed',
                                                                                                              f'SAR_{dataset}_{harbor}_{grid}.tif'),
                                                                                     threshold=0,
                                                                                     study_area=os.path.join(
                                                                                         r'../constants',
                                                                                         f'{harbor.lower()}.shp'))
            df.loc[idx, 'Proportion of area fished'] = proportion_area_fished(
                raster_file=os.path.join(r'../data_publication', dataset.upper(),
                                         'processed',
                                         f'SAR_{dataset}_{harbor}_{grid}.tif'),
                study_area=os.path.join(r'../constants', f'{harbor.lower()}.shp'))
            df.loc[idx, 'Aggregation of fishing pressure'] = aggregation_fishing_pressure(
                raster_file=os.path.join(r'../data_publication', dataset.upper(),
                                         'processed',
                                         f'SAR_{dataset}_{harbor}_{grid}.tif'),
                study_area=os.path.join(r'../constants', f'{harbor.lower()}.shp'))
            idx += 1

df.to_csv(os.path.join(file_dir, 'ICES_fishing_pressure_indicators.csv'), index=False)

df.set_index('Dataset', inplace=True)
df_comparison = df.groupby(['Harbor', 'Grid size (m)']).diff()
df_comparison.dropna(axis=0, inplace=True)
df_comparison.reset_index(drop=True, inplace=True)
df_comparison['Harbor'] = ['BLANES', 'PALAMOS'] * len(grids)
df_comparison['Grid size (m)'] = sorted(grids * 2)
df_comparison.rename(columns={'Average intensity': 'Average intensity (VMS-AIS)',
                              'Proportion of grid cells fished': 'Proportion of grid cells fished (VMS-AIS)',
                              'Proportion of area fished': 'Proportion of area fished (VMS-AIS)',
                              'Aggregation of fishing pressure': 'Aggregation of fishing pressure (VMS-AIS)'},
                     inplace=True)
df_comparison.to_csv(os.path.join(file_dir, 'ICES_fishing_pressure_indicators_comparison.csv'), index=False)

# Analysis by harbor and fishing fleet at 200 m grid resolution (Table 1)
columns = ['Harbor',
           'Fishing ground',
           'Dataset',
           'Average intensity',
           'Proportion of grid cells fished',
           'Proportion of area fished',
           'Aggregation of fishing pressure']

datasets = ['ais', 'vms']
grid = 200

gdf_fishing_grounds = gpd.read_file(fishing_grounds)

fishing_ground_names = gdf_fishing_grounds['Fishground'].to_list()
fishing_ground_names.extend(['All'])

df = pd.DataFrame(columns=columns, index=list(range(18)))

idx = 0
for harbor in harbors:
    for dataset in datasets:
        for fishing_ground_name in fishing_ground_names:
            print(f'Calculating fishing effort indicators for {harbor} ({fishing_ground_name}) {dataset} at '
                  f'{grid} m resolution')
            df.loc[idx, 'Harbor'] = harbor
            df.loc[idx, 'Dataset'] = dataset.upper()
            df.loc[idx, 'Fishing ground'] = fishing_ground_name

            if fishing_ground_name in gdf_fishing_grounds['Fishground'].unique():
                # Mask per fishing ground
                gdf_fishing_ground = gdf_fishing_grounds[gdf_fishing_grounds['Fishground'] == fishing_ground_name]

                df.loc[idx, 'Average intensity'] = average_intensity(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=gdf_fishing_ground)
                df.loc[idx, 'Proportion of grid cells fished'] = proportion_grids_fished(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=gdf_fishing_ground, threshold=0)
                df.loc[idx, 'Proportion of area fished'] = proportion_area_fished(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=gdf_fishing_ground)
                df.loc[idx, 'Aggregation of fishing pressure'] = aggregation_fishing_pressure(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=gdf_fishing_ground)
                idx += 1
            else:
                df.loc[idx, 'Average intensity'] = average_intensity(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=os.path.join(r'../constants', f'{harbor.lower()}.shp'))
                df.loc[idx, 'Proportion of grid cells fished'] = proportion_grids_fished(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=os.path.join(r'../constants', f'{harbor.lower()}.shp'), threshold=0)
                df.loc[idx, 'Proportion of area fished'] = proportion_area_fished(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=os.path.join(r'../constants', f'{harbor.lower()}.shp'))
                df.loc[idx, 'Aggregation of fishing pressure'] = aggregation_fishing_pressure(
                    raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                             f'SAR_{dataset}_{harbor}_{grid}.tif'),
                    study_area=os.path.join(r'../constants', f'{harbor.lower()}.shp'))
                idx += 1

# Finally, extract metrics of VMS-AIS for the whole dataset
for dataset in datasets:
    print(f'Calculating fishing effort indicators for the whole coverage {dataset} at {grid} m resolution')
    df.loc[idx, 'Harbor'] = 'All'
    df.loc[idx, 'Dataset'] = dataset.upper()
    df.loc[idx, 'Fishing ground'] = 'All'
    with rasterio.open(os.path.join(file_dir, dataset.upper(), 'processed',
                                    f'SAR_{dataset}_{grid}.tif')) as src:
        fe = src.read(1)
        fe = np.where(np.isnan(fe), 0, fe)
    df.loc[idx, 'Average intensity'] = average_intensity(
        raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                 f'SAR_{dataset}_{grid}.tif'),
        study_area=study_area)
    df.loc[idx, 'Proportion of grid cells fished'] = proportion_grids_fished(
        raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                 f'SAR_{dataset}_{grid}.tif'),
        study_area=study_area, threshold=0)
    df.loc[idx, 'Proportion of area fished'] = proportion_area_fished(
        raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                 f'SAR_{dataset}_{grid}.tif'),
        study_area=study_area)
    df.loc[idx, 'Aggregation of fishing pressure'] = aggregation_fishing_pressure(
        raster_file=os.path.join(file_dir, dataset.upper(), 'processed',
                                 f'SAR_{dataset}_{grid}.tif'),
        study_area=study_area)
    idx += 1

df.to_csv(os.path.join(file_dir, 'ICES_fishing_pressure_indicators_fishing_fleet.csv'), index=False)

# reshape so each Dataset becomes a column
wide = df.pivot_table(
    index=["Harbor", "Fishing ground"],
    columns="Dataset",
    values=['Average intensity',
            'Proportion of grid cells fished',
            'Proportion of area fished',
            'Aggregation of fishing pressure']
)

diff = wide.xs("VMS", level=1, axis=1) - wide.xs("AIS", level=1, axis=1)

diff.columns = [f"{c} (VMS-AIS)" for c in diff.columns]
# bring back to flat table (optional)
df_comparison = diff.reset_index()

df_comparison.to_csv(os.path.join(file_dir, 'ICES_fishing_pressure_indicators_comparison_fishing_fleet.csv'),
                     index=False)
