#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Using TSV dump files from the O*NET database as input, outputs a CSV
of all O*NET occupations and their knowledge / skills / abilities
in a single matrix.
"""

import argparse
import csv
import os

parser = argparse.ArgumentParser()

parser.add_argument("--occupation-tsv", help="Path to the Occupation Data ONET TSV file")
parser.add_argument("--knowledge-tsv", help="Path to the Knowledge ONET TSV file")
parser.add_argument("--skills-tsv", help="Path to the Skills ONET TSV file")
parser.add_argument("--abilities-tsv", help="Path to the Abilities ONET TSV file")
parser.add_argument("--output-csv", help="Path that the output CSV will be written to")

args = parser.parse_args()

occupation_path = os.path.abspath(os.path.expanduser(args.occupation_tsv))
knowledge_path = os.path.abspath(os.path.expanduser(args.knowledge_tsv))
skills_path = os.path.abspath(os.path.expanduser(args.skills_tsv))
abilities_path = os.path.abspath(os.path.expanduser(args.abilities_tsv))
output_path = os.path.abspath(os.path.expanduser(args.output_csv))

for v in (occupation_path, knowledge_path, skills_path, abilities_path):
    if not os.path.exists(v):
        raise ValueError('Path {0} does not exist'.format(v))

# Open files for reading / writing

occupation_file = open(occupation_path, 'rb')
occupation_tsv = csv.DictReader(occupation_file, delimiter='\t')

knowledge_file = open(knowledge_path, 'rb')
knowledge_tsv = csv.DictReader(knowledge_file, delimiter='\t')

skills_file = open(skills_path, 'rb')
skills_tsv = csv.DictReader(skills_file, delimiter='\t')

abilities_file = open(abilities_path, 'rb')
abilities_tsv = csv.DictReader(abilities_file, delimiter='\t')

output_file = open(output_path, 'wb')
output_csv = csv.writer(output_file)

soc_code_key = 'O*NET-SOC Code'
el_name_key = 'Element Name'
scale_id_key = 'Scale ID'
data_value_key = 'Data Value'
header_row = [soc_code_key, 'Title', 'Description']
dimension_keys = {}

# Write header values for knowledge / skills / abilities dimensions

for (dg, input_file, input_csv) in (('knowledge', knowledge_file, knowledge_tsv), ('skills', skills_file, skills_tsv), ('abilities', abilities_file, abilities_tsv)):
    curr_soc_code = None
    for line in input_csv:
        if curr_soc_code is None:
            curr_soc_code = line[soc_code_key]
        elif curr_soc_code != line[soc_code_key]:
            break

        v = '{0} ({1})'.format(line[el_name_key], line[scale_id_key])

        if not(dg in dimension_keys):
            dimension_keys[dg] = []

        dimension_keys[dg].append({
            'el_name': line[el_name_key],
            'scale_id': line[scale_id_key]})
        header_row.append(v)

    input_file.seek(0)
    next(input_csv)

output_csv.writerow(header_row)

dl = None

# Write a row for each occupation

for occupation_line in occupation_tsv:
    row = [occupation_line[soc_code_key], occupation_line['Title'], occupation_line['Description']]

    # Write all knowledge / skills / abilities values for the given
    # occupation
    for (dg, input_csv) in (('knowledge', knowledge_tsv), ('skills', skills_tsv), ('abilities', abilities_tsv)):
        i = 0

        if dl is None:
            try:
                dl = next(input_csv)
            except StopIteration:
                dl = None

        while dl and (dl[soc_code_key] == occupation_line[soc_code_key]):
            if ((dl[el_name_key] == dimension_keys[dg][i]['el_name'])
                and
                (dl[scale_id_key] == dimension_keys[dg][i]['scale_id'])):
                data_value = None

                try:
                    data_value = float(dl[data_value_key])

                    data_value_lowbound = (
                        (dl[scale_id_key] == 'IM')
                        and 1.0
                        or 0.0)
                    data_value_hibound = (
                        (dl[scale_id_key] == 'IM')
                        and 5.0
                        or 7.0)

                    data_value_stdized = (
                        (data_value - data_value_lowbound)
                        /
                        (data_value_hibound - data_value_lowbound))

                    data_value = data_value_stdized
                except ValueError:
                    data_value = dl[data_value_key]

                row.append(data_value)

            i += 1

            if i == len(dimension_keys[dg]):
                dl = None
            else:
                try:
                    dl = next(input_csv)
                except StopIteration:
                    dl = None

    # Omit rows for which no knowledge / skills / abilities data
    # could be found
    if len(row) > 3:
        output_csv.writerow(row)

occupation_file.close()
knowledge_file.close()
skills_file.close()
abilities_file.close()
output_file.close()
