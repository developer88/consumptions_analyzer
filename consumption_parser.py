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

        # Plot using numeric month positions (1-12) so missing months don't shift the data
        ax.plot(
            df_year['month_num'],
            df_year['consumption'],
            marker='o',
            label=f'20{year}'
        )

    # Set the title
    ax.set_title(consumption["consumptionType"])

    # Set the x-axis label
    ax.set_xlabel("Date")

    # Set the y-axis label
    ax.set_ylabel("Value")

    # Set x-axis to show all 12 months with proper labels
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months, rotation=45)
    ax.grid(True)

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


def yearlyTotalsAsTable(consumption, years = []):
    """
    Display yearly consumption totals in a table format.
    Shows total consumption per year without monthly breakdown.
    """
    years = [str(year) for year in years]
    df = consumption["df"]
    
    # Calculate total consumption per year
    yearly_data = []
    for year in years:
        df_year = df[df['years'] == year]
        total = df_year['consumption'].sum()
        yearly_data.append({'Year': f'20{year}', 'Total Consumption': total})
    
    # Create dataframe and display
    df_yearly = pd.DataFrame(yearly_data)
    print(f"\n{consumption['consumptionType']} - Yearly Totals")
    print(df_yearly.to_string(index=False))
    print()
    
    return df_yearly


def compareYearlyTrends(consumption, years = []):
    """
    Plot yearly consumption trends as a bar chart.
    Shows how total annual consumption changes year over year.
    """
    years = [str(year) for year in years]
    df = consumption["df"]
    
    # Calculate total consumption per year
    yearly_totals = []
    year_labels = []
    
    for year in years:
        df_year = df[df['years'] == year]
        total = df_year['consumption'].sum()
        yearly_totals.append(total)
        year_labels.append(f'20{year}')
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = ax.bar(year_labels, yearly_totals, color='steelblue', alpha=0.7)
    
    # Add value labels on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom', fontsize=10)
    
    # Set labels and title
    ax.set_title(f'{consumption["consumptionType"]} - Yearly Consumption Trends', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Total Consumption', fontsize=12)
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.show()


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

    # Sort by time to ensure chronological order
    df = df.sort_values(by=[settings["timeColumn"]])

    # Store the original timestamp for month gap calculation
    df['timestamp'] = df[settings["timeColumn"]]
    
    # Extract the month and year as new columns (for the actual month when data was entered)
    df['months'] = df[settings["timeColumn"]].dt.strftime('%b')
    df['month_num'] = df[settings["timeColumn"]].dt.month  # Numeric month for plotting
    df['years'] = df[settings["timeColumn"]].dt.strftime('%y')
    df['month_year'] = df[settings["timeColumn"]].dt.strftime("%b %y")

    # Select the first (earliest) record of each month
    df = df.groupby(['month_year'], sort=False).first().reset_index()

    # Calculate how many months elapsed between consecutive readings
    df['prev_timestamp'] = df['timestamp'].shift(1)
    df['months_elapsed'] = ((df['timestamp'].dt.year - df['prev_timestamp'].dt.year) * 12 + 
                            (df['timestamp'].dt.month - df['prev_timestamp'].dt.month))
    
    # Calculate the monthly consumption (difference from the previous month)
    df['consumption'] = df[settings["valueColumn"]].diff()
    
    # If months were skipped, divide consumption by number of months to get average monthly consumption
    # This gives a more accurate representation than showing all consumption in one month
    df.loc[df['months_elapsed'] > 1, 'consumption'] = df['consumption'] / df['months_elapsed']

    # If the first entry of 'consumption' is NaN (because there's no previous month to subtract from), replace it with 0
    df['consumption'] = df['consumption'].fillna(0)

    # Calculate cumulative consumption
    df['cumulative_consumption'] = df['consumption'].cumsum()

    # Drop unnecessary columns
    df = df.drop([settings["timeColumn"], settings["valueColumn"], settings["typeColumn"], 
                  'month_year', 'timestamp', 'prev_timestamp', 'months_elapsed'], axis=1)

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
