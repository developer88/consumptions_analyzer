# Consumption analyzer

Simple Jupyter notebook that gets the data from a CSV file, prepared the data approproately and draw the plots.

## Setup

Lima or Docker

## Usage

### 1. Build and configure the script


1. Rename `config.ini.example` into `config.ini` and fill in all the fields there.
3. run `make build`

### 2. Run the script and analyse the data

For that you need to run Jupyter Notebook:

1. run `make run`
2. open in the browser `http://127.0.0.1:8888/notebooks/Consumption.ipynb`


## Get the data

Before use the parser from this repo, one must collect the proper data first. This can be done like explained here:

* TBD

In case you want to get the data from Google Spreadsheets, use [this guide](https://www.labnol.org/internet/direct-links-for-google-drive/28356/#google-sheets---export-links).

❗️ Before start, make sure you remove the following lines

```python
del df['Дата']
del df['Пометка']
```

from `consumption_parser.py` and `Consumption.ipynb`.

## Usage

There are 2 main files in this repository:

* `Consumption.ipynb` - gets the data for 3 main type of resources at home (water, gas, electricity) and draws the plots.
* `consumption_parser.py` - notebook with all the graphs and usage examples.

### Usage of `consumption_parser.py`

See `Consumption.ipynb`. Otherwise:

```python
import consumption_parser

gas = consumption_parser.parseConsumption("Gas")

print(gas)
```

## Licence

See [LICENSE](LICENSE).
