# Consumption parser
# by Andrey Eremin
# 2022-2023. Licence: GPL3

# Usage:

# import consumption_parser
# gas = consumption_parser.parseConsumption("Gas")
# print(gas) # Do smth with it
# consumption_parser.compareYears(gas, years = [21,22,23])
# consumption_parser.compareYearsAsTable(gas, years = [21,22,23])

# Config
import configparser

# Data manipulation
import pandas as pd
import requests
import io
import matplotlib.pyplot as plt

# Dates manipulation
from datetime import date
from datetime import datetime as dtObj
import datetime

# Main entrypoint
# Get parsed information about consumption data
def parseConsumption(consumptionType):
    settings = loadSettings()

    df = downloadAndPrepareCsv(settings, consumptionType)
    if df.empty:
        print("Cannot download CSV file")
        return None
    else:
        return {
            "df": df,
            "settings": settings,
            "consumptionType": consumptionType
        }

def lastDigitOfCurrentYear():
    # Get the current date
    now = datetime.datetime.now()

    # Get the last two digits of the year
    return now.strftime("%y")

def listOfYearsFor(yearFrom, yearTo):
    return list(range(int(yearFrom), int(yearTo) + 1))


def filterByYear(consumption, year):
    df = consumption["df"]
    return df[df['years'] == str(year)]


def compareYears(consumption, years = []):
    years = [str(year) for year in years]

    # Plot both years on the same axes
    fig, ax = plt.subplots(figsize=(15, 7))

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for year in years:
        df_year = filterByYear(consumption, year)

        df_year.plot(
            x='months',
            y='consumption',
            ax=ax,
            grid=True,
            label=f'20{year}'
        )

    # Set the title
    ax.set_title(consumption["consumptionType"])

    # Set the x-axis label
    ax.set_xlabel("Date")

    # Set the y-axis label
    ax.set_ylabel("Value")

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)
    ax.set_xticks(range(len(months)))
    ax.set_xticklabels(months, rotation=45)

    # Display the legend
    ax.legend()

    plt.show()

def table_for_year(consumption, year):
    df_year = filterByYear(consumption, year)

    # Reset the index
    df_year = df_year.reset_index()

    # Select only few columns
    df_year = df_year[['months', 'consumption']]

    # Rename the columns
    df_year.columns = [f'{col}_{year}' for col in df_year.columns]

    return df_year

def compareYearsAsTable(consumption, years = []):
    years = [str(year) for year in years]

    years_arr = [table_for_year(consumption, year) for year in years]
   
    # Concatenate the dataframes along columns axis
    df_years = pd.concat(years_arr, axis=1)

    # Display the table
    print(consumption["consumptionType"])
    print(df_years.to_string())
    print('')


def downloadAndPrepareCsv(settings, consumptionType):
    df = downloadCsv(settings)
    if not df.empty:
        return prepareDf(df, settings, consumptionType)
    else:
        None


def prepareDf(df, settings, consumptionType):
    # Remove unnecessary columns
    df = df.drop(['Дата', 'Пометка'], axis=1)

    # Filter by consumption type
    df = df[df[settings["typeColumn"]] == consumptionType]

    # Convert the time column to datetime
    df[settings["timeColumn"]] = pd.to_datetime(df[settings["timeColumn"]], format='mixed', dayfirst=True)

    # Extract the month and year as new columns
    df['months'] = (df[settings["timeColumn"]] - pd.DateOffset(months=1)).dt.strftime('%b')
    df['years'] = (df[settings["timeColumn"]] - pd.DateOffset(months=1)).dt.strftime('%y')

    df[settings["timeColumn"]] = (df[settings["timeColumn"]] - pd.DateOffset(months=1)).dt.strftime("%b %y")

    # Select the first record of each month
    is_min_monthly_record = df.groupby([settings["timeColumn"]], sort=False)[settings["valueColumn"]].transform(min) == df[settings["valueColumn"]]
    df = df[is_min_monthly_record]

    # Sort the dataframe by the value column
    df = df.sort_values(by=[settings["valueColumn"]])

    # Calculate the monthly consumption (difference from the previous month)
    df['consumption'] = df[settings["valueColumn"]].diff()

    # If the first entry of 'consumption' is NaN (because there's no previous month to subtract from), replace it with the corresponding value
    df['consumption'] = df['consumption'].fillna(0)

    # Calculate cumulative consumption
    df['cumulative_consumption'] = df['consumption'].cumsum()

    # Reset the index
    df = df.reset_index(drop=True)

    # Drop unnecessary columns
    df = df.drop([settings["timeColumn"], settings["valueColumn"], settings["typeColumn"]], axis=1)

    return df


def downloadCsv(settings):
    r = requests.get(settings["csvUrl"])
    df = None
    if r.ok:
        data = r.content.decode('utf8')
        df = pd.read_csv(io.StringIO(data), dayfirst=True, parse_dates=True)
    return df


def loadSettings():
    config = configparser.ConfigParser()
    config.read('config.ini')
    config.sections()

    return {
        "typeColumn": config['MAIN']['TypeColumnName'],
        "timeColumn": config['MAIN']['TimeColumnName'],
        "valueColumn": config['MAIN']['ValueColumnName'],
        "csvUrl": config['MAIN']['FileUrl']
    }
