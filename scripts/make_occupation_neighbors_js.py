#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reduces the dimensions of the Occupation Matrix using PCA, finds each
occupation's nearest neighbors using kd-trees, and outputs a JavaScript
file with all neighbors in an array, suitable for including in a
web page.
"""

import argparse
import os

import pandas
from scipy.spatial import cKDTree
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

parser = argparse.ArgumentParser()

parser.add_argument("--input-csv", help="Path to the Occupation Matrix CSV input file")
parser.add_argument("--output-js", help="Path that the output JS will be written to")

args = parser.parse_args()

input_path = os.path.abspath(os.path.expanduser(args.input_csv))
output_path = os.path.abspath(os.path.expanduser(args.output_js))

for v in (input_path,):
    if not os.path.exists(v):
        raise ValueError('Path {0} does not exist'.format(v))

# Open files for reading / writing
occupation_matrix = pandas.read_csv(input_path)
num_occupations = len(occupation_matrix)

output_file = open(output_path, 'wb')

output_file.write('var linksArray = [\n')

# Clean the data
good_columns = occupation_matrix._get_numeric_data().dropna(axis=1)

# Reduce dimensions of knowledge / skills / abilities with PCA
pca_2 = PCA(2)
plot_columns = pca_2.fit_transform(good_columns)

# Represent PCA graph as a kd-tree for finding neighbors
tree = cKDTree(plot_columns)

# For each occupation, query the kd-tree for its nearest neighbors
min_dist = None
max_dist = None
min_count = None
max_count = None
min_count_fallback = None
max_count_fallback = None
zeroneighbors_count = 0
onlyoneneighbor_count = 0
distoverone_count = 0
total_fallback = 0
total_neighbors = 0

dist_limit = 0.3
dist_limit_fallback = 1.1
max_neighbors = 3
max_neighbors_fallback = 3

for i, o in enumerate(plot_columns):
    #print('Occupation: {0}'.format(occupation_matrix.ix[i,1]))
    dist, indexes = tree.query([o,], k=(max_neighbors + 1))
    neighbors = []
    #print('Neighbors:')

    indexes_count = 0
    for j, index in enumerate(indexes[0]):
        if dist[0][j] > 0.0 and dist[0][j] < dist_limit:
            weight = dist[0][j]
            if weight < 0.01:
                weight = 0.01
            if weight > 0.99:
                weight = 0.99
            weight = 1.0 - weight

            neighbors.append({
                'desc': '{0} -- {1}'.format(
                    occupation_matrix.ix[i,1],
                    occupation_matrix.ix[index,1]),
                'source': i,
                'target': index,
                'weight': weight})

            indexes_count += 1
            if min_dist is None or dist[0][j] < min_dist:
                min_dist = dist[0][j]
            if max_dist is None or dist[0][j] > max_dist:
                max_dist = dist[0][j]
            #print('{0:.2f}, {1}'.format(dist[0][j], str(occupation_matrix.ix[index,1])))

    if indexes_count >= max_neighbors:
        if min_count is None or indexes_count < min_count:
            min_count = indexes_count
        if max_count is None or indexes_count > max_count:
            max_count = indexes_count
    else:
        dist, indexes = tree.query([o,], k=(max_neighbors_fallback + 1))

        indexes_count = 0
        neighbors = []

        for j, index in enumerate(indexes[0]):
            if dist[0][j] > 0.0 and dist[0][j] < dist_limit_fallback:
                weight = dist[0][j]
                if weight < 0.01:
                    weight = 0.01
                if weight > 0.99:
                    weight = 0.99
                weight = 1.0 - weight

                neighbors.append({
                    'desc': '{0} -- {1}'.format(
                        occupation_matrix.ix[i,1],
                        occupation_matrix.ix[index,1]),
                    'source': i,
                    'target': index,
                    'weight': weight})

                indexes_count += 1
                total_fallback += 1
                if min_dist is None or dist[0][j] < min_dist:
                    min_dist = dist[0][j]
                if max_dist is None or dist[0][j] > max_dist:
                    max_dist = dist[0][j]
                if dist[0][j] > 0.99:
                    distoverone_count += 1

        if min_count_fallback is None or indexes_count < min_count_fallback:
            min_count_fallback = indexes_count
        if max_count_fallback is None or indexes_count > max_count_fallback:
            max_count_fallback = indexes_count

    if indexes_count == 0:
        zeroneighbors_count += 1
    if indexes_count == 1:
        onlyoneneighbor_count += 1

    j = 0
    num_neighbors = len(neighbors)
    for neighbor in neighbors:
        output_file.write('  {{desc: "{0}", source: {1}, target: {2}, weight: {3}}}{4}\n'.format(
            neighbor['desc'],
            neighbor['source'],
            neighbor['target'],
            neighbor['weight'],
            ((i < (num_occupations - 1) or j < (num_neighbors - 1)) and ',' or '')))

        j += 1

    total_neighbors += indexes_count

output_file.write('];\n')

#print('min_dist: {0:.3f}'.format(min_dist))
#print('max_dist: {0:.3f}'.format(max_dist))
#print('min_count: {0}'.format(min_count))
#print('max_count: {0}'.format(max_count))
#print('min_count_fallback: {0}'.format(min_count_fallback))
#print('max_count_fallback: {0}'.format(max_count_fallback))
#print('zeroneighbors_count: {0}'.format(zeroneighbors_count))
#print('onlyoneneighbor_count: {0}'.format(onlyoneneighbor_count))
#print('distoverone_count: {0}'.format(distoverone_count))
#print('total_fallback: {0}'.format(total_fallback))
#print('total_neighbors: {0}'.format(total_neighbors))
