""" try finding outliers by using center of mass for each volume w/in run

run as:
    python3 scripts/calc_centerofmass.py data/*.nii

will produce plot with x, y, z coords of center of mass for each volume (and histogram of values)

to do: can use this as summary stat for each volume; do outlier detection over com values?

"""

import numpy as np
import nibabel as nib
from scipy import ndimage
import matplotlib.pyplot as plt
import sys
import seaborn as sns
import dvars_sliding



def calc_image_COM(img):
    """
    returns center of mass xyz coordinates for each volume in 4d data of img

    Parameters
    ----------
    img : image object
        nibabel image object containing 4D file, with last dimension length
        ``t``.

    Returns
    -------
    com : list of 3-tuples with com coordinate (x,y,z), length number of volumes

    """
    data = img.get_data() #get 4d array from img

    com = [] #init array for COM

    #get COM for each volume
    for v in range(data.shape[-1]):
        temp_vol = data[...,v]
        com.append(ndimage.measurements.center_of_mass(temp_vol))
    return com


def plot_COM(com,filename):
    fig, axes = plt.subplots(nrows=3)
    dim = ['X', 'Y', 'Z']
    gap = 0.2

    for i in range(3):
        temp = [c[i] for c in com]
        temp_mean = sum(temp)/len(temp)

        axes[i].plot(temp,color = [0,0,1])
        axes[i].plot(list(axes[0][0].get_xlim()),[temp_mean, temp_mean], color = [1,0,0])
        axes[i].set_ylabel('COM'+dim[i])
        axes[i].set_xlabel('vol')
        axes[i].set_ylim([temp_mean-gap, temp_mean+gap])

    plt.suptitle('center of mass: '+filename)
    plt.show()



def plot_com_dvars(com_dvars, coords, window, filename):

    plt.suptitle('dvars for center of mass coords; window = '+str(window)+'; '+str(filename))
    plt.plot(com_dvars)
    plt.scatter(coords[0,:],coords[1,:], c = 'r')
    plt.xlim([0, len(com_dvars)])
    plt.show()



def get_outlier_coords(com, window, filename, fig):
    """
    get outlier volumes from com list

    Parameters
    ----------
    com : list of 3-tuples with com coordinate (x,y,z), length number of volumes

    window: int, window size for sliding dvars

    filename: str, .nii filename for plot title

    fig: 1 or 0, 1=show plot & 0 = no plot

    Returns
    -------
    outlier_vols : list outlier volume numbers (or None)

    """
    temp = np.array([[i[0] for i in com], [i[1] for i in com],[i[2] for i in com]])
    temp = np.reshape(temp,(3,1,1,temp.shape[1]))
    values = dvars_sliding.calc_sliding_dvars(None, window, temp)

    q1, q3 = np.percentile(values, [25, 75])
    p = 1.5 #large values make outlier threshold higher
    x = (q3-q1)*p
    outlier_high = values> q3 + x
    outlier_low = values< q1 - x
    outlier_idx = np.logical_or(outlier_high, outlier_low)
    if outlier_idx.sum() >0:
        outlier_coords = [[i,values[i]] for i in range(len(outlier_idx)) if outlier_idx[i]]
        outlier_coords = np.array(outlier_coords).T

        if fig:
            plot_com_dvars(values, outlier_coords, window, filename)
        outlier_vols = [int(outlier_coords[0,i])+window for i in range(outlier_coords.shape[1])]
        return outlier_vols

    else:
        return None

def main():

    sns.set_style("white")

    sys.path.append("scripts/")

    filename = sys.argv[1]
    img = nib.load(filename, mmap=False)

    #find center of mass coords for each vol
    data_com = calc_image_COM(img)
    #plot_COM(data_com,filename)

    #calc dvars over com coords
    window = 1 #size of sliding window for dvars
    fig = 0 #1= display plot, 0= no plot
    outliers = get_outlier_coords(data_com, window, filename, fig)

    #print results
    print(filename+' outlier volumes: ')
    print(outliers)


if __name__ == '__main__':
    main()
