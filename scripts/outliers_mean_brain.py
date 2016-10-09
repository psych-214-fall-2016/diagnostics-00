import sys
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
from skimage import filters

def mean_img(data, ax):
    """
    Return mean brain volume over time. Each slice is thresholded (Otsu) to
    remove noise. The thresholds for each slice are also returned (currently
    unused).

    Input
    -----
    data : 4D numpy array
        Data from scan.

    ax : int | 0 | 1 | 2
        Axis along which the slices are defined. Values 0, 1, 2 correspond to
        the x, y, and z axes respectively.

    Output
    ------
    mean_img : 3D numpy array
        Thresholded mean brain volume over time.

    thresh : numpy array (1, # slices)
        Threshold for each slice.
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
    Return projection of each slice (in each volume) to the mean slice (from the
    thresholded mean brain volume).

    Input
    -----
    data : 4D numpy array
        Data from scan.

    mean_brain : 3D numpy array
        Thresholded mean brain volume over time.

    ax : int | 0 | 1 | 2
        Axis along which the slices are defined. Values 0, 1, 2 correspond to
        the x, y, and z axes respectively.

    Output
    ------
    projections : numpy array (# volumes, # slices)
        Projection/dot product of each slice in each volume on the corresponding
        slice in the mean_brain.
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
    Count the number of outlier slices (using 1.5 * IQR) in each volume.

    Input
    -----
    projections : numpy array (# volumes, # slices)
        Projection/dot product of each slice in each volume on the corresponding
        slice in the mean_brain.

    Output
    ------
    outliers : numpy array (# volumes, # slices)
        Binary array. Entry (i, j) = 1 if slice j in volume i is an outlier,
        and (i, j) = 0 otherwise.
    """
    outliers = np.zeros(projections.shape)

    for s in range(projections.shape[1]):
        proj = projections[:, s]
        q75, q25 = np.percentile(proj, [75, 25])
        iqr = q75 - q25
        outliers[:, s] = (proj < (q25 - 1.5 * iqr)).astype(int)

    return outliers

def mean_brain(filename, ax):
    """
    Find the outlier brain volumes in the scan.

    Input
    -----
    filename : string
        Filename where data is contained, probably .nii file.

    ax : string | 'x' | 'y' | 'z'
        Direction over which to slice. For example, if ax is 'x', then each
        slice is a slice in the y-z plane.
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
