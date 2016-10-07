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
sns.set_style("white")


def calc_image_COM(img):

    data = img.get_data() #get 4d array from img

    com = [] #init array for COM

    #get COM for each volume
    for v in range(data.shape[-1]):
        temp_vol = data[...,v]
        com.append(ndimage.measurements.center_of_mass(temp_vol))
    return com


def plot_COM(com,filename):
    fig, axes = plt.subplots(nrows=3, ncols=2, tight_layout=True)

    dim = ['X', 'Y', 'Z']
    gap = 0.2
  
    for i in range(3):
        temp = [c[i] for c in com]
        temp_mean = sum(temp)/len(temp)

        axes[i][0].plot(temp,color = [0,0,1])
        axes[i][0].plot(list(axes[0][0].get_xlim()),[temp_mean, temp_mean], color = [1,0,0])
        axes[i][0].set_ylabel('COM'+dim[i])
        axes[i][0].set_xlabel('vol')
        axes[i][0].set_ylim([temp_mean-gap, temp_mean+gap])

        #SHOW BOXPLOTS
        #axes[i][1].boxplot(temp, 0, 'rs', 0)
        #axes[i][1].set_xlim([temp_mean-gap, temp_mean+gap])
        #axes[i][1].set_xlabel('COM'+dim[i])

        #SHOW HISTOGRAMS
        axes[i][1].hist(temp, bins = 30, range = (temp_mean-gap, temp_mean+gap), color = [0,0,1])
        axes[i][1].plot([temp_mean, temp_mean],list(axes[0][1].get_ylim()), color = [1,0,0])
        axes[i][1].set_ylabel('freq')
        axes[i][1].set_xlabel('COM'+dim[i])
        axes[i][1].set_xlim([temp_mean-gap, temp_mean+gap])
        
    plt.suptitle('center of mass: '+filename)
    plt.show()


def main():
    filename = sys.argv[1]
    img = nib.load(filename, mmap=False)
    data_com = calc_image_COM(img)
    plot_COM(data_com,filename)

if __name__ == '__main__':
    main()
