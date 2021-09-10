# Consumption analyzer

Simple Jupyter notebook that gets the data from a CSV file, prepared the data approproately and draw the plots.

## Setup

Rename `config.ini.example` into `config.ini` and fill in all the fields there.

### Get the data

Before use the parser from this repo, one must collect the proper data first. This can be done like explained here:

* TBD

In case you want to get the data from Google Spreadsheets, use [this guide](https://www.labnol.org/internet/direct-links-for-google-drive/28356/#google-sheets---export-links).

## Usage

There are 3 main files in this repository:

* `Consumption_with_explanations.ipynb` - explains everything that happens step by step
* `Consumption.ipynb` - gets the data for 3 main type of resources at home (water, gas, electricity) and draws the plots
* `consumption_parser.py` - shorter version of what one may find in `Consumption_with_explanations.ipynb` and which is used in `Consumption.ipynb`. 

### Usage of `consumption_parser.py`

See `Consumption.ipynb`. Otherwise:

```python
import consumption_parser

gas = consumption_parser.parseConsumption("Gas")

print(gas)
```

## Licence

See [LICENSE](LICENSE).