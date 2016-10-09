""" Python script to find outliers

Run as:

    python3 scripts/find_outliers.py data
"""
import os
import sys
sys.path.append("scripts/")

import calc_centerofmass as com
import outliers_mean_brain as mb
import nibabel as nib

def find_outliers(data_directory):
    """ Print filenames and outlier indices for images in `data_directory`.

    Print filenames and detected outlier indices to the terminal.

    Parameters
    ----------
    data_directory : str
        Directory containing containing images.

    Returns
    -------
    None
    """
    data_names = [f for f in os.listdir(data_directory) if f[-4:]==".nii"]


    for filename in data_names:
        # Use center of mass method
        img = nib.load(data_directory+'/'+filename, mmap=False)
        data_com = com.calc_image_COM(img)
        outliers_com = com.get_outlier_coords(data_com, 1, filename, 0) #don't make plots

        # Use mean method
        outliers_mean = mb.mean_brain(data_directory+'/'+filename, 'z')

        # Get outliers picked up by both methods
        outliers = []
        for i in outliers_mean:
            if i in outliers_com or i+1 in outliers_com or i-1 in outliers_com:
                outliers.append(i)

        print(filename+' outlier volumes: ')
        print(outliers)



def main():
    # This function (main) called when this file run as a script.
    #
    # Get the data directory from the command line arguments
    if len(sys.argv) < 2:
        raise RuntimeError("Please give data directory on "
                           "command line")
    data_directory = sys.argv[1]
    # Call function to validate data in data directory
    find_outliers(data_directory)


if __name__ == '__main__':
    # Python is running this file as a script, not importing it.
    main()
