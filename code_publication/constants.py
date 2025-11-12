# List of constant variables

# Polygons
import pandas as pd
import os
import seaborn as sns

study_area = r'../constants/study_area.shp'
fishing_grounds = r'../data_publication/fishing_grounds.shp'

file_dir = r'../data_publication'

vms_dir = os.path.join(file_dir, 'VMS')
ais_dir = os.path.join(file_dir, 'AIS')

# Fishing effort parameters
min_haul = 60
turn_off_time = 60
min_nav_speed = 6.68

min_speed_vms = 0.87
max_speed_vms = 3.76
max_duration_false_negative_vms = 20
max_duration_false_positive_vms = 40

min_speed_ais = 0.83
max_speed_ais = 3.80
max_duration_false_negative_ais = 5
max_duration_false_positive_ais = 10

extent = [2.7, 3.7, 41.25, 42]

grid = 200


def dataframe_intersection(df1, df2, df1_cols, df2_cols):
    """
    Function to extract the intersection of two dataframes based on specific set of columns
    :param df1: DataFrame 1
    :param df2: DataFrame 2
    :param df1_cols: Columns that need to be matched in DataFrame 1
    :param df2_cols: Columns that need to be matched in DataFrame 2
    :return: 2 DataFrames (df1, df2)
    """
    # Identify the unique combination of columns
    df1_subset = set(df1.groupby(df1_cols).first().index.to_list())
    df2_subset = set(df2.groupby(df2_cols).first().index.to_list())

    # Check columns that are in both dataframes
    intersection = list(df1_subset.intersection(df2_subset))

    # Extract subset of each dataframe
    df1_out = df1[df1.set_index(df1_cols).index.isin(intersection)]
    df2_out = df2[df2.set_index(df2_cols).index.isin(intersection)]
    return df1_out, df2_out


def best_bounding_box(dataset1, dataset2):
    minx_ais, miny_ais, maxx_ais, maxy_ais = dataset1.total_bounds
    minx_vms, miny_vms, maxx_vms, maxy_vms = dataset2.total_bounds
    if minx_ais < minx_vms:
        min_x = minx_ais
    else:
        min_x = minx_vms
    if miny_ais < miny_vms:
        min_y = miny_ais
    else:
        min_y = miny_vms
    if maxx_ais < maxx_vms:
        max_x = maxx_ais
    else:
        max_x = maxx_vms
    if maxy_ais < maxy_vms:
        max_y = maxy_ais
    else:
        max_y = maxy_vms
    return min_x, min_y, max_x, max_y
