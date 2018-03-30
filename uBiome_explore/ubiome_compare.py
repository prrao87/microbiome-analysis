"""
Compare the results between two uBiome JSON files
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

path_to_JSON = "_RawData/"
json_file1 = "ubiome-export-data-2018-03-03.json"
json_file2 = "ubiome-export-data-2018-01-23.json"

# Input a list of taxonomies that we want to compare between JSON files
tax_list = ['phylum', 'family', 'genus', 'species']   # ['phylum', 'class', 'order', 'family', 'genus', 'species']
plotCompare = True  # To save comparison figures as png, set to 'True'
plotUnique = True  # To save unique figures as png, set to 'True'

def read_JSON(path_to_JSON):
    """
    Read in uBiome JSON data and set index to tax_rank (phylum, family, genus, etc.)
    """
    top_level = json.load(open(path_to_JSON))
    normal_cap = top_level['ubiome_bacteriacounts'][0]['count_norm']
    data = pd.io.json.json_normalize(top_level['ubiome_bacteriacounts'])

    return data, normal_cap

def plot_compare(df1, df2, json_file1, json_file2, category, plotCompare=False):
    """
    Plot comparison between two uBiome JSON Files
    Only those taxa that are common between the two datasets are plotted
    """
    data = pd.merge(df1, df2, how='inner', on=['tax_name'], sort=True)
    data['diff'] = data['count_norm_x'] - data['count_norm_y']
    data_sorted = data.sort_values(by='diff')

    data_indexed = data_sorted.set_index('tax_name', drop=True)
    data_indexed['normalized_diff'] = data_indexed['diff']/10000
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

    if plotCompare:
        plt.savefig('compare_'+category+'.png')
    else: plt.show()
    plt.close()

def plot_unique(df1, df2, json_file1, json_file2, category, plotUnique=False):
    """
    Plot the genera and species that are unique to each sample
    """
    unique1 = df1[~df1.tax_name.isin(df2.tax_name)].copy()
    unique1['percent_rank'] = (unique1['count_norm']/10000)
    unique1 = unique1.sort_values(by='percent_rank')
    unique1 = unique1.set_index('tax_name')
    # print(unique1.tail())

    unique2 = df2[~df2.tax_name.isin(df1.tax_name)].copy()
    unique2['percent_rank'] = (unique2['count_norm']/10000)
    unique2 = unique2.sort_values(by='percent_rank')
    unique2 = unique2.set_index('tax_name')

    # Error check: If DataFrame is empty, create a blank DatFrame for plotting
    if unique1.empty:
        unique1 = pd.DataFrame({'percent_rank': [0]})
    if unique2.empty:
        unique2 = pd.DataFrame({'percent_rank': [0]})

    # Begin plotting with subplots
    plt.style.use('ggplot')
    fig, ax = plt.subplots(1, 2)
    fig.set_size_inches(14, 8)

    # Plot horizontal barcharts as subplots in pandas
    # The width here is set as a function of
    unique1['percent_rank'].plot(kind='barh', ax=ax[0], legend=False, width=0.01*len(unique1))
    unique2['percent_rank'].plot(kind='barh', ax=ax[1], legend=False, width=0.01*len(unique2))
    ax[0].set_ylabel('')
    ax[1].set_ylabel('')
    ax[0].set_title('Unique to New Sample (%s)' % category.capitalize(), fontsize=11)
    ax[1].set_title('Unique to Old Sample (%s)' % category.capitalize(), fontsize=11)
    plt.tick_params(axis='y', which='both', labelleft='off', labelright='on')
    plt.tight_layout()

    if plotUnique:
        plt.savefig('unique_'+category+'.png')
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
        plot_compare(df1, df2, json_file1, json_file2, tax, plotCompare)
        plot_unique(df1, df2, json_file1, json_file2, tax, plotUnique)
