# Diagnostics project

Script go in the `scripts` directory.

Library code (such as Python modules or packages) goes in the `packages` directory.

You should put this `packages` directory on your Python PATH.

This file has instructions on how to get, validate and process the data.

## Outlier detection methods

Two different outlier detection methods are applied to each scan:

1. Center of mass: Using the center of mass (x,y,z) coordinates for each volume,
the root mean square difference (RMS) is calculated for the sliding window
average over the volumes along the time axis. The default window size is 1.
Volumes for which RMS is 3 times outside IQR are considered outliers.

2. **CHRISTINE**

Volumes are labeled as outliers if they (or +/- 1 neighbor) are identified
with both methods. Overall, scans with more than 2 outlier volumes are
considered to be problem scans.

## Get the data

    cd data
    curl -LO http://nipy.bic.berkeley.edu/psych-214/group00.tar.gz
    tar zxvf group00.tar.gz
    cd ..

## Check the data

    python3 scripts/validate_data.py data

## Find outliers

    python3 scripts/find_outliers.py data

This should print output to the terminal of form:

    <filename> <outlier_index>, <outlier_index>, ...
    <filename> <outlier_index>, <outlier_index>, ...

Where `<filename>` is the name of the image that has outlier scans, and
`<outlier_index>` is an index to the volume in the 4D image that you have
indentified as an outlier.  0 refers to the first volume.  For example:

    group00_sub01_run1.nii 3, 21, 22, 104
    group00_sub02_run2.nii 11, 33 91
    group00_sub04_run2.nii 101, 102, 132
    group00_sub07_run2.nii 0, 1, 2, 166, 167
    group00_sub09_run2.nii 3
