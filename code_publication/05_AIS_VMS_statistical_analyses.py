import numpy as np
import rasterio
from scipy.stats import pearsonr
from constants import *


def load_common_valid_cells(raster1, raster2):

    with rasterio.open(raster1) as src1:
        a = src1.read(1)
        a = np.where(np.isnan(a), 0, a)
        nodata1 = src1.nodata

    with rasterio.open(raster2) as src2:
        b = src2.read(1)
        b = np.where(np.isnan(b), 0, b)
        nodata2 = src2.nodata

    mask = np.isfinite(a) & np.isfinite(b)

    if nodata1 is not None:
        mask &= a != nodata1

    if nodata2 is not None:
        mask &= b != nodata2

    return a[mask], b[mask]


def mean_bias_error(raster_ais, raster_vms):

    ais, vms = load_common_valid_cells(raster_ais, raster_vms)

    return np.mean(vms - ais)


def rmse(raster_ais, raster_vms):

    ais, vms = load_common_valid_cells(raster_ais, raster_vms)

    return np.sqrt(np.mean((ais - vms) ** 2))


def pearson_correlation(raster_ais, raster_vms):

    ais, vms = load_common_valid_cells(raster_ais, raster_vms)

    r, p = pearsonr(ais, vms)

    return r, p


def jaccard_overlap(raster_ais, raster_vms, threshold=0):

    ais, vms = load_common_valid_cells(raster_ais, raster_vms)

    ais_bin = ais > threshold
    vms_bin = vms > threshold

    intersection = np.sum(ais_bin & vms_bin)
    union = np.sum(ais_bin | vms_bin)

    return intersection / union


def relative_difference_stats(raster_ais, raster_vms, epsilon=1e-10):

    ais, vms = load_common_valid_cells(raster_ais, raster_vms)

    rd = (ais - vms) / (vms + epsilon)

    return {
        "mean_relative_difference": np.mean(rd),
        "median_relative_difference": np.median(rd),
        "std_relative_difference": np.std(rd)
    }


ais = os.path.join(ais_dir, 'processed', f'SAR_ais_{grid}.tif')
vms = os.path.join(vms_dir, 'processed', f'SAR_vms_{grid}.tif')

print("MBE:", mean_bias_error(ais, vms))

print("RMSE:", rmse(ais, vms))

r, p = pearson_correlation(ais, vms)
print("Pearson r:", r)
print("p-value:", p)

print("Jaccard overlap:", jaccard_overlap(ais, vms))

print(relative_difference_stats(ais, vms))
