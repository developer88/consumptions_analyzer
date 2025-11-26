# Home Utilities Consumption Analyzer - Project Overview

## Purpose

This project tracks and analyzes home utility consumption (gas, electricity, and water) over time. It helps identify consumption patterns, compare usage year-over-year, and visualize trends to better understand and manage household resource usage.

## Core Concept

The system follows a simple workflow:

1. **Data Collection**: Users manually record their utility meter readings throughout the year
2. **Data Storage**: Readings are stored in a spreadsheet (currently Google Sheets)
3. **Data Processing**: The system downloads, parses, and calculates monthly consumption
4. **Visualization**: Interactive charts and tables show consumption patterns and trends

## Data Model

### Input Data Structure

The source data is a CSV/spreadsheet with the following columns:

- **Time**: Timestamp when the meter reading was recorded (format: DD.MM.YYYY HH:MM:SS)
- **Type**: Category of utility ("Газ" for gas, "Электричество" for electricity, "Вода" for water)
- **Value** (Показание): The actual meter reading value at that moment
- **Additional columns**: "Дата" and "Пометка" (currently ignored/dropped)

### Data Entry Pattern

Users typically enter meter readings **at the beginning of each month**, but may:
- Forget and enter late in the month
- Enter multiple times per month (system uses the first entry only)
- Skip entire months (system handles gaps)

### Processed Data Structure

After processing, each consumption record contains:

- **months**: Month name (Jan, Feb, Mar, etc.)
- **month_num**: Numeric month (1-12) for accurate plotting
- **years**: Two-digit year (24, 25, etc.)
- **consumption**: Calculated monthly consumption (difference between consecutive readings)
- **cumulative_consumption**: Running total of consumption

## Key Processing Logic

### 1. Data Download
- Fetches CSV data from a remote URL (Google Sheets export link)
- Configured via `config.ini` file

### 2. Data Filtering and Grouping
- Filters data by consumption type (gas, electricity, or water)
- Sorts chronologically by timestamp
- Groups by month-year, selecting the **first (earliest)** entry per month

### 3. Consumption Calculation
The system calculates monthly consumption by:

1. Taking the difference between consecutive meter readings
2. Detecting month gaps (when months are skipped)
3. **Averaging consumption** over gaps: if 2 months are skipped, the total consumption is divided by the number of elapsed months

**Example:**
- January reading: 1000 units
- February: **MISSING**
- March reading: 1150 units
- System detects 2-month gap
- Calculates: (1150 - 1000) / 2 = 75 units per month
- Both February and March show ~75 units (averaged)

This prevents artificial spikes in graphs when months are missed.

### 4. Edge Cases Handled
- **Missing months**: Consumption averaged across the gap
- **Multiple entries per month**: Only the first (earliest) entry is used
- **First entry ever**: Consumption set to 0 (no previous reading to compare)
- **Mixed date formats**: Handles both date-only and datetime formats

## Visualization Features

### Monthly Comparison Charts
Shows monthly consumption overlaid for multiple years:
- X-axis: Months (Jan through Dec)
- Y-axis: Consumption value
- Multiple lines, one per year
- Missing months appear as gaps in the line

### Monthly Comparison Tables
Displays side-by-side monthly data for selected years:
- Rows: 12 months
- Columns: Month name and consumption for each year
- Missing data shows as NaN

### Yearly Trend Analysis
Provides year-over-year total consumption:
- **Table format**: Lists each year with total annual consumption
- **Bar chart**: Visual comparison of yearly totals
- Helps identify long-term trends (increasing/decreasing usage)

## Configuration

The system requires a `config.ini` file with:

```
[MAIN]
FileUrl = [URL to CSV export]
TimeColumnName = Time
ValueColumnName = Value
TypeColumnName = Type
```

## Current Technology Stack

- **Data Processing**: Python with pandas
- **Visualization**: matplotlib
- **Environment**: Jupyter Notebook
- **Data Source**: Google Sheets (exported as CSV)

## API Functions Available

### Core Functions
- `parseConsumption(consumptionType)`: Main entry point, returns processed data structure
- `downloadAndPrepareCsv(settings, consumptionType)`: Fetches and processes raw data

### Visualization Functions
- `compareYears(consumption, years)`: Draw multi-year monthly comparison chart
- `compareYearsAsTable(consumption, years)`: Display multi-year monthly comparison table
- `compareYearlyTrends(consumption, years)`: Draw yearly total consumption bar chart
- `yearlyTotalsAsTable(consumption, years)`: Display yearly totals table

### Utility Functions
- `filterByYear(consumption, year)`: Extract data for a specific year
- `listOfYearsFor(yearFrom, yearTo)`: Generate year range
- `lastDigitOfCurrentYear()`: Get current year (2-digit format)

## Data Flow

```
Google Sheets → CSV Export → Download → Parse → Filter by Type → 
Sort by Time → Group by Month → Calculate Consumption → 
Handle Gaps → Generate Visualizations
```

## Use Cases

1. **Monthly budget planning**: Understand typical monthly usage
2. **Seasonal pattern detection**: See which months have higher/lower consumption
3. **Year-over-year comparison**: Track if usage is increasing or decreasing
4. **Anomaly detection**: Identify unusual spikes or drops in consumption
5. **Cost estimation**: Predict future utility bills based on historical patterns

## Future Mobile App Considerations

When building a mobile frontend/backend:

### Essential Features
1. **Data entry**: Easy meter reading input with date/time
2. **Multi-utility support**: Handle gas, electricity, water separately
3. **Visualization**: Charts showing monthly and yearly trends
4. **Data sync**: Store readings in cloud/database
5. **Reminders**: Notify users to record readings monthly

### Technical Considerations
1. **Replace CSV with database**: Store readings in proper DB (SQLite, PostgreSQL, Firebase, etc.)
2. **API design**: RESTful endpoints for CRUD operations on readings
3. **Authentication**: Multi-user support if needed
4. **Offline support**: Cache data locally, sync when online
5. **Date handling**: Ensure timezone awareness
6. **Gap detection**: Implement the averaging logic for missing months
7. **Configurable categories**: Allow custom utility types beyond gas/water/electricity

### Data Schema (Suggested)
```
Readings table:
- id (primary key)
- user_id (if multi-user)
- timestamp (when reading was recorded)
- utility_type (gas/electricity/water/custom)
- meter_value (the actual reading)
- notes (optional)
- created_at
- updated_at
```

### Key Algorithms to Port
1. **Chronological sorting** before processing
2. **First-entry-per-month selection** logic
3. **Month gap detection** and consumption averaging
4. **Consumption calculation** (diff between consecutive readings)
5. **Month-to-position mapping** (1-12) for accurate chart rendering

## Current Limitations

1. **Manual data entry**: Requires user to consistently record readings
2. **No automation**: Cannot auto-import from smart meters
3. **Single data source**: Tied to one Google Sheets file
4. **No multi-user support**: Designed for single household
5. **Limited historical analysis**: No forecasting or advanced analytics
6. **Desktop-only**: Jupyter notebook not mobile-friendly

## Success Metrics

The system successfully:
- Handles missing months without data corruption
- Displays accurate month-to-month comparisons even with gaps
- Shows correct yearly trends
- Visualizes data clearly with proper month alignment
- Averages consumption over gaps to avoid misleading spikes
