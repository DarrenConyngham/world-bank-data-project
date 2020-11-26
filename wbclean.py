from pandas_datareader import wb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

def to_flourish(indicator, start_yr, end_yr, country='all', save_csv=True):
    """
    Downloads data from the World Bank and converts it to the format for making bar chart races in Flourish.
    Parameters:
    * indicator: the world bank code available on the World Bank Page.
    * country: a string if single or a list if multiple of the ISO3 codes of the locations.
    * start_yr: the first year of data that you want to get.
    * end_yr: the final year of data that you want to collect.
    * save_csv: saves the file as a csv in your working directory.
    """
    df = wb.download(indicator=indicator, country=country, start=start_yr, end=end_yr)
    df = df.reset_index()
    df = pd.pivot_table(df, values=indicator, columns='year', index='country').reset_index()
    print("Processed the Indicator Data")

    country_info = wb.get_countries()
    country_info = country_info[country_info.region != 'Aggregates']

    df_merged = pd.merge(country_info[['iso2c', 'name', 'region']], df, left_on='name', right_on='country')
    df_merged.insert(3, 'Image URL', df_merged['iso2c'].apply(lambda i: f"https://www.countryflags.io/{i}/flat/64.png"))
    df_merged = df_merged.drop(columns=['iso2c', 'country'])

    if save_csv:
        df_merged.to_csv(f"flourish_data/flourish_{indicator}_{datetime.now().strftime('%d-%m-%Y %H-%M')}.csv", index=False)

    return df_merged


def get_wb_data(indicator, start_yr, end_yr, country='all', save_csv=False):
    """
    Downloads and formats World Bank Data with year as index.
    Parameters:
    * indicator: the world bank code available on the World Bank Page.
    * start_yr: the first year of data that you want to get.
    * end_yr: the final year of data that you want to collect.
    * country: a string if single or a list if multiple of the ISO3 codes of the locations.
    * save_csv: saves the file as a csv in your working directory.
    """
    global indicator_name
    indicator_name = indicator
    temp_df = wb.download(indicator=indicator, country=country, start=start_yr, end=end_yr)
    temp_df = temp_df.dropna()
    temp_df.index.names = ['Region', 'Year']
    temp_df = temp_df.reset_index(level=0).sort_values(by = 'Region')
    if save_csv:
        temp_df.to_csv(f"{indicator}_{datetime.now().strftime('%d-%m-%Y %H-%M')}.csv", index=False)
    return temp_df


def plot_line_chart(indicator, start_yr, end_yr, country='all', title='Graph', figure_size=(18,10), ylim=None, save=False):
    """
    Plots a line chart of the World Bank data with the year on the x-axis.
    Must have a dataframe in the correct format. This format is where the year is the index
    Parameters:
    * indicator: the world bank code available on the World Bank Page.
    * start_yr: the first year of data that you want to get.
    * end_yr: the final year of data that you want to collect.
    * country: a string if single or a list if multiple of the ISO3 codes of the locations.
    * title: The title that you want for your graph.
    * figure_size: The size of the figure that you want as output.
    * ylim: The bottom and top limits of the y-axis as a tuple. Can just include a single number for the bottom.
    * save: Saves the graph to your current working directory.
    """
    df = get_wb_data(indicator, start_yr, end_yr, country, save_csv=False)
    plt.figure(figsize=figure_size)
    sns.set_style('darkgrid')
    sns.set_palette('tab10')
    sns.set_context("talk", rc={"lines.linewidth": 8}, font_scale=1.6)

    sns.lineplot(x=df.index, y=indicator, data=df, hue='Region', alpha=0.7)
    plt.title(f"{title}\n from {df.index.min()} to {df.index.max()}", size=40)
    plt.xlabel('Year')
    plt.ylabel(title)
    plt.legend()
    plt.ylim(ylim)
    if save:
        plt.savefig(f"{title}_line.png")
    plt.show()


def plot_bar_chart(indicator, year, country='all', title='Graph', margin=1.1, figure_size=(18,10), barcolour='darkslategrey',
                  decimals=1, save=False):
    """
    Plots a Bar Chart of a specific year of data.
    Must have a dataframe in the correct format. This format is where the year is the index

    Parameters:
    * indicator: the world bank code available on the World Bank Page.
    * year: The year of data that you want to plot. By default will plot the latest year of data available.
    * country: a string if single or a list if multiple of the ISO3 codes of the locations.
    * title: The title that you want for your graph
    * margin: change the size of the right limit to allow for space for the text.
    * figure_size: The size of the figure that you want as output.
    * barcolor: Change the colours of the bars
    * decimals: how many decimal places shold the labels contain.
    * save: Saves the graph to your current working directory.
    """
    df = get_wb_data(indicator, year, year, country, save_csv=False)
    if year == None:
        year = df.index.max()
    df = df[df.index == str(year)].sort_values(by='Region')

    plt.figure(figsize=figure_size)
    sns.set_style('darkgrid')
    sns.set_palette('tab10')
    sns.set_context("talk", rc={"lines.linewidth": 8}, font_scale = 1.6)

    sns.barplot(x=indicator, y='Region', data=df.sort_values(by=indicator, ascending=False), color=barcolour)

    if decimals > 0:
        temp_df = df[indicator].sort_values(ascending=False).values.round(decimals).astype(float)
    else:
        temp_df = df[indicator].sort_values(ascending=False).values.round(decimals).astype(int)

    for i, v in enumerate(temp_df):
        plt.text(v, i, f' {v:,}', color='black', fontweight='bold', verticalalignment='center')
    plt.title(f"{title}\nin {df.index.max()}", size=40)
    plt.xlabel(f'{title}')
    plt.ylabel('')
    plt.xlim(right = df[indicator].max() * margin)

    if save:
        plt.savefig(f"{title}_bar.png")

    plt.show()
