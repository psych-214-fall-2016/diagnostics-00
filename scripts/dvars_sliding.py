"""
Script to calculate dvars values

For testing run:
    python3 scripts/dvars_sliding.py tests/data_file.nii win

Produces plot of dvars over volumes
"""

import sys
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import seaborn as sns

sns.set()

def calc_sliding_dvars(img, win, data = None):
    """
    Root mean squared difference between volumes in `img` over a sliding
    window.

    Input
    -----
    img : image object
        nibabel image object containing 4D file, with last dimension length
        ``t``.

    win : int
        Size of sliding window.

    data = None : will extract data from img.get_data() if data==None; otherwise
        can use func with numpy array (without img file)

    Output
    ------
    dvars : shape (t-1,) array
        1D array with root mean square difference values between each volume
        and the average over the previous (win) and future (win) volumes. The
        first (win) and last (win) volumes are lost.
    """
    if data is None:
        data = img.get_data()

    # For each voxel, calculate the differences between each volume and the
    # average of the win volumes around it
    diff = []
    for i in range(data.shape[3]-win):
        vol = i + win

        # Find avg of volumes around current volume
        win_vols = np.concatenate((data[..., vol-win:vol],
            data[..., vol+1:vol+win+1]), axis=3)
        win_avg = np.mean(win_vols, axis=3)

        diff.append(data[..., vol] - win_avg)

    diff_sq = np.array(diff)**2
    dvars_sq = diff_sq.mean(axis=(1, 2, 3))
    dvars = dvars_sq**0.5

    return dvars


def main():
    # Get the first command line argument
    filename = sys.argv[1]
    win = sys.argv[2]
    img = nib.load(filename)
    dvars = calc_sliding_dvars(img, int(win))
    plt.plot(dvars)

    plt.draw()
    plt.show()


if __name__ == '__main__':
    main()
