#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Using the Occupation Matrix CSV as input, outputs a JavaScript file
with all occupations in an array, suitable for including in a
web page.
"""

import argparse
import csv
import os

parser = argparse.ArgumentParser()

parser.add_argument("--input-csv", help="Path to the Occupation Matrix CSV file")
parser.add_argument("--output-js", help="Path that the output JS will be written to")

args = parser.parse_args()

input_path = os.path.abspath(os.path.expanduser(args.input_csv))
output_path = os.path.abspath(os.path.expanduser(args.output_js))

for v in (input_path,):
    if not os.path.exists(v):
        raise ValueError('Path {0} does not exist'.format(v))

# Open files for reading / writing

num_occupations = sum(1 for line in open(input_path, 'rb')) - 1
input_file = open(input_path, 'rb')
input_csv = csv.DictReader(input_file)

output_file = open(output_path, 'wb')

output_file.write('var nodesArray = [\n')

soc_code_key = 'O*NET-SOC Code'

# Write a line for each occupation
i = 0
for input_line in input_csv:
    output_file.write('  {{label: "{0}", id: "{1}"}}{2}\n'.format(
        input_line['Title'],
        input_line[soc_code_key],
        ((i < (num_occupations - 1)) and ',' or '')))

    i += 1

output_file.write('];\n\n')

input_file.seek(0)
next(input_csv)

output_file.write('var nodesHash = {\n')

# Write the hash of occupations
i = 0
for input_line in input_csv:
    output_file.write('  "{0}": {1}{2}\n'.format(
        input_line[soc_code_key],
        i,
        ((i < (num_occupations - 1)) and ',' or '')))

    i += 1

output_file.write('};\n')

input_file.close()
output_file.close()
