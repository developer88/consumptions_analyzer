# Consumption parser
# by Andrey Eremin
# 2022-2023. Licence: GPL3

# Usage:

# import consumption_parser
# gas = consumption_parser.parseConsumption("Gas")
# print(gas) # Do smth with it
# consumption_parser.drawGraph(gas)

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

    # TODO: Just a hack to override the range. Remove it later
    settings['daysAgoRange'] = int(9999)

    df = downloadAndPrepareCsv(settings, consumptionType)
    if df.empty:
        print("Cannot download CSV file")
        return None
    else:
        return {
            "df": df,
            "settings": settings,
            "ticks": list(range(0, len(df[settings["timeColumn"]]))),
            "tickLabels": df[settings["timeColumn"]],
            "consumptionType": consumptionType
        }

def lastDigitOfCurrentYear():
    # Get the current date
    now = datetime.datetime.now()

    # Get the last two digits of the year
    return now.strftime("%y")


def filterByYear(consumption, year):
    df = consumption["df"]
    return df[df['years'] == str(year)]


# Draw the graph
# Usage:
#   gas = consumption_parser.parseConsumption("Gas")
#   consumption_parser.drawGraph(gas)
def drawGraph(consumption):
    # Draw the plot
    ax = consumption["df"].plot(
        x=consumption["settings"]["timeColumn"],
        y=consumption["settings"]["valueColumn"],
        figsize=(15, 7),
        grid=True,
        title=consumption["consumptionType"]
    )

    # Make sure we display all the dates in X
    ax.set_xticks(consumption["ticks"])
    ax.set_xticklabels(consumption["tickLabels"], rotation=45)

def compareYears(consumption, year1, year2):
    year1 = str(year1)
    year2 = str(year2)
    df_year1 = filterByYear(consumption, year1)
    df_year2 = filterByYear(consumption, year2)

    # Plot both years on the same axes
    fig, ax = plt.subplots(figsize=(15, 7))

    df_year1.plot(
        x=consumption["settings"]["timeColumn"],
        y=consumption["settings"]["valueColumn"],
        ax=ax,
        grid=True,
        color='blue',
        label=f'{year1} Consumption'
    )

    df_year2.plot(
        x=consumption["settings"]["timeColumn"],
        y=consumption["settings"]["valueColumn"],
        ax=ax,
        grid=True,
        color='red',
        label=f'{year2} Consumption'
    )

    # Set the title
    ax.set_title(consumption["consumptionType"])

    # Set the x-axis label
    ax.set_xlabel("Date")

    # Set the y-axis label
    ax.set_ylabel("Value")

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Display the legend
    ax.legend()

    plt.show()

def compareYearsAsTable(consumption, year1, year2):
    year1 = str(year1)
    year2 = str(year2)

    df_year1 = filterByYear(consumption, year1)
    df_year2 = filterByYear(consumption, year2)

    # Reset the index
    df_year1 = df_year1.reset_index()
    df_year2 = df_year2.reset_index()

    # Rename the columns
    df_year1.columns = [f'{col}_{year1}' for col in df_year1.columns]
    df_year2.columns = [f'{col}_{year2}' for col in df_year2.columns]

    # Concatenate the dataframes along columns axis
    df_years = pd.concat([df_year2, df_year1], axis=1)

    # Display the table
    print(df_years.to_string())



# Display the comparison of last years
#   per months as a table
# Usage:
#  gas = consumption_parser.parseConsumption("Gas")
#  consumption_parser.pivotLastYears(gas, printLabel=true)
def pivotLastYears(consumption, printLabel=False):
    months_in_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                       'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    df = consumption['df'].pivot(index='months', columns='years',
                                 values=consumption["settings"]["valueColumn"])
    df.reindex(months_in_order)

    if printLabel == True:
        print(consumption["consumptionType"])
    return df

# Display the comparison of last years
#   per months as a graph
# Usage:
#  gas = consumption_parser.parseConsumption("Gas")
#  consumption_parser.drawLastYearsGraph(gas)


def drawLastYearsGraph(consumption):
    df = pivotLastYears(consumption)
    df.plot(
        kind='bar',
        figsize=(17, 10),
        color=['red', 'green', 'blue'],
        rot=0,
        title=consumption["consumptionType"])


def downloadAndPrepareCsv(settings, consumptionType):
    df = downloadCsv(settings)
    if not df.empty:
        return prepareDf(df, settings, consumptionType)
    else:
        None


def prepareDf(df, settings, consumptionType):
    # NB: Feel free to comment these lines out. This was necessary for me because I have that in my CSV file :) and 
    #   I am too lazy to remove it manually
    del df['Дата']
    del df['Пометка']

    # format the dates
    df[settings["timeColumn"]] = pd.to_datetime(
        df[settings["timeColumn"]], dayfirst=True)
    # filter by consumptionType
    dataByType = df[df[settings["typeColumn"]] == consumptionType]
    # filter for daysAgoRange days ago
    daysAgo = date.today() - \
        datetime.timedelta(days=int(settings["daysAgoRange"]))
    today = date.today()
    dt = dtObj(daysAgo.year, daysAgo.month, daysAgo.day)
    dtToday = dtObj(today.year, today.month, today.day)
    # Filter out for the dates
    dateFilterdDf = dataByType[(dataByType[settings["timeColumn"]] >= dt) & (
        dataByType[settings["timeColumn"]] <= dtToday)]
    # format the dates that look good
    dateFilterdDf[settings["timeColumn"]] = dateFilterdDf[settings["timeColumn"]].apply(format_date)
    # Drop unneeded column with type
    del dateFilterdDf[settings["typeColumn"]]
    # Group by month and select min of each group to get 1 record per month to work with
    # We take min to make sure we take the closest record to the beginning of the month
    idx = dateFilterdDf.groupby([settings["timeColumn"]], sort=False)[
        settings["valueColumn"]].transform(min) == dateFilterdDf[settings["valueColumn"]]
    grouppedDf = dateFilterdDf[idx]
    # To make sure we have all months sorted correctly, we sort it by valueColumn
    # We do so as we know that counter value is always a cummulative sum, so it always growths.
    sortedDf = grouppedDf.sort_values(by=[settings["valueColumn"]])
    # Because all the values are a cummulative sum, we extract diff between neighbours
    # and set the index to move sure the .diff will not complain about strings in timeColumn
    diffDf = sortedDf.set_index(settings["timeColumn"]).diff()
    # Remove index to make it easier to draw a plot
    diffDfWithoutIndex = diffDf.reset_index(level=0)
    # Drop first row that is NaN anyway and so has no any valuable data for us.
    # dfWithoutFirstAndLastRows = diffDfWithoutIndex.drop(diffDfWithoutIndex.tail(1).index) # drop last n rows
    dfWithoutFirstRow = diffDfWithoutIndex.drop(
        diffDfWithoutIndex.head(1).index)  # drop first n rows
    # add some extra columns for filtering
    dfWithoutFirstRow['months'] = dfWithoutFirstRow[settings["timeColumn"]].apply(
        format_simple_months)
    dfWithoutFirstRow['years'] = dfWithoutFirstRow[settings["timeColumn"]].apply(
        format_simple_years)

    return dfWithoutFirstRow


def format_simple_months(x):
    return x[:len(x)-2]


def format_simple_years(x):
    return x[len(x)-2:]


def format_date(x):
    return x.strftime("%b %y")


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
        "daysAgoRange": config['MAIN']['daysAgoRange'],
        "csvUrl": config['MAIN']['FileUrl']
    }
