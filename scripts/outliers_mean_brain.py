import sys
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from skimage import filters

def mean_img(data, ax):
    """
    Return mean thresholded (Otsu) volume
    Also return threshold value
    """
    # Average volume over time
    mean_img = data.mean(axis=3)

    thresh = np.zeros((1, data.shape[ax]))
    for s in range(data.shape[ax]):
        if ax == 0:
            img = mean_img[s, :, :]
        elif ax == 1:
            img = mean_img[:, s, :]
        else:
            img = mean_img[..., s]

        thresh[0, s] = filters.threshold_otsu(img)
        img[img < thresh[0, s]] = 0

    return mean_img, thresh


def projection_on_mean(data, mean_brain, ax):
    """
    Return projection of each slice to slice mean.
    Values returned in (# volume, # slice) array
    """

    # Reshape data and mean
    n_slices = data.shape[ax]
    n_pixels = int(np.prod(data.shape[0:3]) / n_slices)
    n_voxels = data.shape[3]
    data = data.reshape((n_pixels, n_slices, n_voxels))
    mean_brain = mean_brain.reshape((n_pixels, n_slices))

    # Project
    projections = np.zeros((n_voxels, n_slices))
    for v in range(n_voxels):
        proj = np.sum(data[..., v] * mean_brain, axis=0)
        projections[v, :] = proj

    return projections

def find_outlier_volumes(projections):
    """
    Find volumes that had outlier slices using IQR
    """
    outliers = np.zeros(projections.shape)

    for s in range(projections.shape[1]):
        proj = projections[:, s]
        q75, q25 = np.percentile(proj, [75, 25])
        iqr = q75 - q25
        outliers[:, s] = (proj < (q25 - 1.75 * iqr)).astype(int)

    return outliers

def mean_brain(filename, ax):
    """
    Filename : file containing scan data
    dir      : direction of slicing, 'x', 'y', 'z'
    """
    # Load scan
    img = nib.load(filename)
    data = img.get_data()

    # Find how many bad slices are in each volume
    ax_dict = {'x':0, 'y':1, 'z':2}
    mean_brain, threshold = mean_img(data, ax_dict[ax])
    p = projection_on_mean(data, mean_brain, ax_dict[ax])
    bad_slices = np.sum(find_outlier_volumes(p), axis=1)

    # Return list of bad volumes
    # Volume is bad if more than 1/4 of its slices are outliers
    thresh = np.round(data.shape[ax_dict[ax]] / 4)
    bad_volumes = [vol for vol, num in enumerate(bad_slices) if num > thresh ]

    return bad_volumes
