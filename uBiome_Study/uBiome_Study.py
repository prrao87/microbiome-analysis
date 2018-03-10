#!/usr/bin/env python3
"""
Compare a personal uBiome JSON raw result file with uBiome 2017 paper findings
http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0176555
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path_to_xlsx = "_RawData/S3_Table.xlsx"
path_to_JSON = "_RawData/ubiome-export-data-2018-02-23.json"
savefig = False  # To save plot as png, set to 'True'

def read_xl(path_to_xlsx):
    """Read in Excel data from uBiome paper into a pandas DataFrame"""
    data = pd.read_excel(path_to_xlsx, header=5)
    species = data.iloc[:, 2:16]
    genus = data.iloc[:, 16:]

    return species, genus

def read_JSON(path_to_JSON):
    """Read in individual uBiome test results JSON into a pandas DataFrame"""
    top_level = json.load(open(path_to_JSON))
    normal_cap = top_level['ubiome_bacteriacounts'][0]['count_norm']
    data = pd.io.json.json_normalize(top_level['ubiome_bacteriacounts'])

    return data, normal_cap

def analyze_ranks(df, normal_cap, rank_type):
    """
    Calculate relative percentage based on a particular tax_rank
    (phylum, family, genus, etc.)
    """
    rank_data = df.loc[df['tax_rank'] == rank_type].copy()
    rank_data['percent_rank'] = (rank_data['count_norm']/normal_cap*100).round(decimals=3)
    rank_data_sorted = rank_data.sort_values('count_norm', ascending=False)

    return rank_data_sorted

def create_boxplot(example_data, my_data, savefig):
    """
    Plot a box plot at the genus level to replicate Fig 3. in the uBiome paper
    The individual JSON uBiome result is overlayed on the boxplot as red squares
    """
    # flierprops = {'color': 'black', 'marker': '+', 'alpha':0.1}
    ax = example_data.plot.box(logy=True, figsize=(10, 8), whis=[0, 100.0], meanline=True, \
    showmeans=True, showfliers=False)
    ax.set_xticklabels(my_data.columns.tolist(), rotation=30, fontsize=8)
    ax.set_ylim(bottom=0.0001, top=100)
    ax.set_ylabel("Relative Abundance (%)")
    ax.set_title("Boxplot of Relative Abundance")

    # Bee-swarm plot of all data points on top of boxplot - plain ol' matplotlib scatter
    for i in range(len(example_data.columns)):
        y = example_data.iloc[:, i]
        x = np.random.normal(1+i, 0.04, size=len(y))
        plt.scatter(x, y, color='k', marker='+', alpha=0.1)

    # Add individual values from my JSON (boxplot starts indexing from 1, which is weird)
    # Hence we begin the range of x-values from 1 instead of zero
    plt.scatter(list(range(1, len(example_data.columns)+1)), my_data.values[0], \
    color='r', marker='*', s=150)
    if savefig == True:
        plt.savefig('boxplot.png')
    else: plt.show()

def main(path_to_JSON, path_to_xlsx, json_rank_type, savefig=False):
    # Read JSON and index by tax_rank
    data, normal_cap = read_JSON(path_to_JSON)
    # Extract a DataFrame ranked by tax_rank relative percentage
    json_ranked = analyze_ranks(data, normal_cap, json_rank_type)
    json_ranked_pivot = json_ranked.pivot(index='tax_rank', columns='tax_name', \
    values='percent_rank')

    species, genus = read_xl(path_to_xlsx)

    # Pivoted data from JSON is matched with corresponding column name in the research study
    example_data = genus[genus.columns & json_ranked_pivot.columns]
    my_data = json_ranked_pivot[genus.columns & json_ranked_pivot.columns]
    my_data = my_data.reset_index(drop=True)
    print("Found the following genera in JSON matching with those in research study:\n")
    print(my_data.head())

    create_boxplot(example_data, my_data, savefig)

if __name__ == "__main__":
    # Only plot w.r.t. genus level as individual species detection is not reliable for now
    main(path_to_JSON, path_to_xlsx, 'genus', savefig)
