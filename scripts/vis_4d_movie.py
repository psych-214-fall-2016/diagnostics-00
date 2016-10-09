
""" scan through volumes in 4d over multiple slices
--> This will display multiple slices (can change #) and display voxel values moving
through all the volumes (100ms/vol)


To run:

python3 scripts/vis_4d.py data/*.nii

**TO DO: this is a quick way to visually inspect the 4d files for glaring
issues; should probably be much nicer!!**
"""

import sys
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import time

def display_4d(img, filename, nrows, ncols):

    """
    Root mean squared difference between volumes in `img` over a sliding
    window.

    Input
    -----
    img : image object
        nibabel image object containing 4D file, with last dimension length
        ``t``.

    filename : str
        will display as title in plot

    nrows : int
        number of rows on figure with slices (nrows*ncols = #slices)

    ncols : int
        number of rows on figure with slices (nrows*ncols = #slices)


    """

    data = img.get_data()

    nslices = nrows*ncols

    gap = int(np.floor(data.shape[2]/(nslices+1))) #decide spacing between slices
    idx = [gap*(i+1) for i in range(nslices)] #display these slices

    print(idx)
    fig,ax = plt.subplots(nrows,ncols)
    im = [] #save subplot info in list
    for R in range(nrows):
        for C in range(ncols):
            im.append(ax[R][C].imshow(data[...,R*ncols+C,0]))
            ax[R][C].xaxis.set_visible(False)
            ax[R][C].yaxis.set_visible(False)
    fig.suptitle(filename)
    fig.show()

    for t in range(data.shape[3]):
        time.sleep(0.1) #wait 100ms between updating vols
        for s in range(nslices): #update each slice with next vol
            im[s].set_data(data[...,s,t])
        fig.canvas.draw() #update fig


def main():
    # Get the first command line argument
    filename = sys.argv[1]
    img = nib.load(filename)

    #decide number of slices to display: nrows*ncols
    nrows = 3
    ncols = 3

    display_4d(img, filename, nrows, ncols)


if __name__ == '__main__':
    main()
