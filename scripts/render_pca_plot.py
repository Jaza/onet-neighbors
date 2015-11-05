#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reduces the dimensions of the Occupation Matrix using PCA, and
renders the PCA data as a scatter plot.
"""

import argparse
import os

import pandas
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

parser = argparse.ArgumentParser()

parser.add_argument("--input-csv", help="Path to the Occupation Matrix CSV input file")

args = parser.parse_args()

input_path = os.path.abspath(os.path.expanduser(args.input_csv))

for v in (input_path,):
    if not os.path.exists(v):
        raise ValueError('Path {0} does not exist'.format(v))

# Open files for reading / writing
occupation_matrix = pandas.read_csv(input_path)

# Clean the data
good_columns = occupation_matrix._get_numeric_data().dropna(axis=1)

# Reduce dimensions of knowledge / skills / abilities with PCA
pca_2 = PCA(2)
plot_columns = pca_2.fit_transform(good_columns)

# Prepare scatter plot
plt.scatter(x=plot_columns[:,0], y=plot_columns[:,1])

# Add occupation titles as annotations to scatter plot
for label, x, y in zip(occupation_matrix.ix[:,1], plot_columns[:, 0], plot_columns[:, 1]):
    plt.annotate(
        label,
        xy=(x, y), xytext=(-20, 20),
        textcoords='offset points', ha='right', va='bottom',
        bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

# Draw scatter plot
plt.show()
