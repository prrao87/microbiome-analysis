#!/usr/bin/env python3
"""
Analyze individual uBiome JSON raw result file and output top 20 ranks
"""
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

path_to_JSON = "_RawData/ubiome-export-data-2018-03-03.json"
# Select what taxonomy to extract: 'phylum', 'class', 'order', 'family', 'genus', 'species'
tax_list = ['phylum', 'genus', 'species']   # Input as a list, even for single entry (to loop through)
top = 20   # For now, plot top 20 bacterial taxonomy ranks
savefig = True  # To save figures as png, set to 'True'

def read_JSON(path_to_JSON):
    """
    Read in uBiome JSON data and set index to tax_rank (phylum, family, genus, etc.)
    """
    top_level = json.load(open(path_to_JSON))
    normal_cap = top_level['ubiome_bacteriacounts'][0]['count_norm']
    data = pd.io.json.json_normalize(top_level['ubiome_bacteriacounts'])

    return data, normal_cap

def analyze_ranks(df, normal_cap, category):
    """
    Calculate relative percentage based on a particular tax_rank (phylum, family, genus, etc.)
    """
    rank_data = df.loc[df['tax_rank'] == category].copy()
    rank_data['percent_rank'] = (rank_data['count_norm']/normal_cap*100).round(decimals=2)
    rank_data_sorted = rank_data.sort_values('count_norm', ascending=False)

    return rank_data_sorted

def plot_bars(df, category, savefig=False):
    """
    Plot top 20 tax_ranks from DataFrame
    """
    data = df[['tax_name', 'percent_rank']][:top]

    def autolabel(rects):
        """Attach a text label above each bar displaying its height"""
        for rect in rects:
            height = rect.get_height()
            ax.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                    '%.2f' % float(height),
                    ha='center', va='bottom')

    # Fig settings
    fig, ax = plt.subplots()
    fig.set_size_inches(8, 8)

    # Plot each bar separately and give it a label, with number displayed above label
    for index, row in data.iterrows():
        rects = ax.bar([row['tax_name']], [row['percent_rank']], label=row['tax_name'],
               alpha=0.5, align='center')
        autolabel(rects)

    # Axis settings
    ax.set_title("Relative bacterial percentages ranked by "+category)
    ax.margins(0.05)
    ax.legend(loc='best', prop={'size': 10}, frameon=False)
    ax.set_ylim(bottom=0)
    ax.patch.set_facecolor('0.95')
    ax.grid(color='white', linestyle='-')
    ax.set(axisbelow=True, xticklabels=[])
    plt.tight_layout()

    if savefig:
        plt.savefig('individual_'+category+'.png')
    else: plt.show()
    plt.close()

if __name__ == "__main__":
    # Read JSON and index by tax_rank
    data, normal_cap = read_JSON(path_to_JSON)

    # Plot data as bar charts for each taxonomic classification
    for tax in tax_list:
        # Extract DataFrames ranked by tax_rank relative percentage
        ranked = analyze_ranks(data, normal_cap, tax)
        plot_bars(ranked, tax, savefig)
