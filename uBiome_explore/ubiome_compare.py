"""
Analyze individual uBiome JSON raw result file and output top 20 ranks
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

path_to_JSON = "_RawData/"
json_file1 = "ubiome-export-data-2018-03-03.json"
json_file2 = "ubiome-export-data-2018-01-23.json"
# Select what taxonomy to extract: 'phylum', 'class', 'order', 'family', 'genus', 'species'
tax_list = ['phylum', 'genus', 'species']   # Input as a list, even for single entry (to loop through)
savefig = True  # To save figures as png, set to 'True'

def read_JSON(path_to_JSON):
    """
    Read in uBiome JSON data and set index to tax_rank (phylum, family, genus, etc.)
    """
    top_level = json.load(open(path_to_JSON))
    normal_cap = top_level['ubiome_bacteriacounts'][0]['count_norm']
    data = pd.io.json.json_normalize(top_level['ubiome_bacteriacounts'])

    return data, normal_cap

def plot_compare(df1, df2, json_file1, json_file2, category, savefig=False):
    """
    Plot comparison between two uBiome JSON Files
    Only those taxa that are common between the two datasets are plotted
    """
    data = pd.merge(df1, df2, how='inner', on=['tax_name'], sort=True)
    data['diff'] = data['count_norm_x'] - data['count_norm_y']
    data_sorted = data.sort_values(by='diff')

    data_indexed = data_sorted.set_index('tax_name', drop=True)
    data_indexed['normalized_diff'] = 100.0*(data_indexed['diff']/1000000)
    data_plot = data_indexed.loc[:, 'normalized_diff']
    # print(data_plot.tail(10))

    plt.style.use('ggplot')
    ax = data_plot.plot(kind='barh', figsize=(12, 10))
    ax.grid(which='major', linestyle='-')
    ax.grid(which='minor', linestyle='-', alpha=0.75)
    ax.minorticks_on()
    ax.tick_params(axis='y',which='minor',left='off')
    ax.set_xlabel("Normalized Difference (%)")
    ax.set_ylabel("")
    ax.set_title("Comparing %s level: '%s' vs. '%s'" % (category.capitalize(), json_file1, json_file2), fontsize=10)
    plt.tight_layout()

    if savefig:
        plt.savefig('compare_'+category+'.png')
    else: plt.show()
    plt.close()

if __name__ == "__main__":
    # Read JSON and index by tax_rank
    data1, normal_cap1 = read_JSON(os.path.join(path_to_JSON, json_file1))
    data2, normal_cap2 = read_JSON(os.path.join(path_to_JSON, json_file2))

    # Plot data as bar charts for each taxonomic classification
    for tax in tax_list:
        # Extract DataFrames based on taxonomy type
        df1 = data1.loc[data1['tax_rank'] == tax]
        df2 = data2.loc[data2['tax_rank'] == tax]
        plot_compare(df1, df2, json_file1, json_file2, tax, savefig)
