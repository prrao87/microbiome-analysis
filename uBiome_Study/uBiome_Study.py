#!/usr/bin/env python3
"""
Compare a personal uBiome JSON raw result file with uBiome 2017 paper findings
http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0176555
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

path_to_xlsx = "_RawData/S3_Table.xlsx"
path_to_JSON = "_RawData/ubiome-export-data-2018-02-23.json"
savefig = True  # To save plot as png, set to 'True'

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

def create_boxplot_seaborn(genus, my_data, savefig):
    """
    Same as create_boxplot_matplotlib, but implemented with seaborn
    """
    fig, ax = plt.subplots(figsize=(10,6))
    ax.set_xticklabels(genus.columns.tolist(), rotation=30, fontsize=8)
    ax.set(yscale='log')
    ax.set_ylim(bottom=0.0001, top=100)
    ax.set_ylabel("Relative Abundance (%)")
    ax.set_title("Boxplot of Relative Abundance")

    # Seaborn boxplot of uBiome data
    sns.boxplot(data=genus, linewidth=0.75, width=0.5, fliersize=3, \
    whis=[0, 100.0], meanline=True, showfliers=False, showmeans=True)

    # Add transparency to colors (per Michael Waskom's method)
    # https://github.com/mwaskom/seaborn/issues/979
    for patch in ax.artists:
        r, g, b, a = patch.get_facecolor()
        patch.set_facecolor((r, g, b, .3))

    # Scatter plot with jitter enabled
    sns.stripplot(data=genus, alpha=0.1, jitter=True, marker='o', \
    edgecolor='k', linewidth=0.5)

    # Add individual values from user JSON
    plt.scatter(my_data.columns, my_data.values[0], \
    color='r', marker='*', s=150, zorder=25)
    plt.tight_layout()

    if savefig == True:
        plt.savefig('boxplot.png')
    else: plt.show()

def main(path_to_JSON, path_to_xlsx, json_rank_type, savefig=False):
    # Read JSON and index by tax_rank
    data, normal_cap = read_JSON(path_to_JSON)
    # Extract a DataFrame ranked by tax_rank relative percentage
    json_ranked = analyze_ranks(data, normal_cap, json_rank_type)
    # Pivot JSON dataframe to match user data data with uBiome data
    json_ranked_pivot = json_ranked.pivot(index='tax_rank', columns='tax_name', \
    values='percent_rank')

    # Read in data from uBiome study
    species, genus = read_xl(path_to_xlsx)

    # Find unique and common column names between my uBiome raw data and uBiome study
    common = genus.columns.intersection(json_ranked_pivot.columns)
    unique = genus.columns.difference(json_ranked_pivot.columns)

    # Cast zero-values for all genera that do not exist in my data
    my_data = json_ranked_pivot[common].copy()
    for col in unique:
        my_data[col] = 0.0

    # Comparison boxplot between my data and uBiome study
    create_boxplot_seaborn(genus, my_data, savefig)

if __name__ == "__main__":
    # Only plot w.r.t. genus level as individual species detection is not reliable for now
    main(path_to_JSON, path_to_xlsx, 'genus', savefig)
