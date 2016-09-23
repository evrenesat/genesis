# -*-  coding: utf-8 -*-
"""
"""
from pprint import pprint

anlyzes = {}
def process_row(row):
    name = row[1]
    if name not in anlyzes:
        anlyzes[name]={
            'name': name,
            'sample': set(row[2].split('/')),
            'mediums': row[16].split(','),
            'process_time': row[23],
            'method': row[27],
            'amount': "%s %s" % (row[30], row[31]),
            'price': int(row[35].replace('TL', '').strip().replace('.00', '').replace(',', '') or 0),
        }
    else:
        anlyzes[name]['sample'].add(row[2])



import csv
with open('data.csv') as csvfile:
    for row in csv.reader(csvfile, delimiter=',', quotechar='"'):
        if row[1]:
            process_row(row)


pprint(anlyzes)
