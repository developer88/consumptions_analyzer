# Consumption parser
# by Andrey Eremin
# 2021. Licence: GPL3

# Usage:

# import consumption_parser
# gas = consumption_parser.parseConsumption("Gas")
# print(gas) # Do smth with it

# Config
import configparser

# Data manipulation
import pandas as pd
import requests
import io

# Dates manipulation
from datetime import date
from datetime import datetime as dtObj
import datetime

# Main entrypoint
# Get parsed information about consumption data
def parseConsumption(consumptionType):
    settings = loadSettings()
    df = downloadAndPrepareCsv(settings, consumptionType)
    if not df.empty:
        return {
            "df": df,
            "settings": settings,
            "ticks": list(range(0, len(df[settings["timeColumn"]]))),
            "tickLabels": df[settings["timeColumn"]], 
            "consumptionType": consumptionType
        }
    else:
        print("Cannot download CSV file")
        return None

def downloadAndPrepareCsv(settings, consumptionType):
    df = downloadCsv(settings)
    if not df.empty:
        return prepareDf(df, settings, consumptionType)
    else:
        None   

def prepareDf(df, settings, consumptionType):
    # NB: Feel free to comment these lines out. This was necessary for me because I had that in my CSV file
    del df['Дата']
    del df['Пометка']

    # format the dates
    df[settings["timeColumn"]] = pd.to_datetime(df[settings["timeColumn"]], dayfirst=True)
    # filter by consumptionType
    dataByType = df[df[settings["typeColumn"]] == consumptionType]
    # filter for daysAgoRange days ago
    daysAgo = date.today() - datetime.timedelta(days=int(settings["daysAgoRange"]))
    today = date.today()
    dt = dtObj(daysAgo.year, daysAgo.month, daysAgo.day)
    dtToday = dtObj(today.year, today.month, today.day)
    # Filter out for the dates
    dateFilterdDf = dataByType[(dataByType[settings["timeColumn"]] >= dt) & (dataByType[settings["timeColumn"]] <= dtToday)]
    # format the dates that look good   
    dateFilterdDf[settings["timeColumn"]] = dateFilterdDf[settings["timeColumn"]].apply(format_date)
    # Drop unneeded column with type
    del dateFilterdDf[settings["typeColumn"]]
    # Group by month and select min of each group to get 1 record per month to work with
    # We take min to make sure we take the closest record to the beginning of the month 
    idx = dateFilterdDf.groupby([settings["timeColumn"]], sort=False)[settings["valueColumn"]].transform(min) == dateFilterdDf[settings["valueColumn"]]
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
    #dfWithoutFirstAndLastRows = diffDfWithoutIndex.drop(diffDfWithoutIndex.tail(1).index) # drop last n rows
    dfWithoutFirstRow = diffDfWithoutIndex.drop(diffDfWithoutIndex.head(1).index) # drop first n rows
    
    return dfWithoutFirstRow

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
