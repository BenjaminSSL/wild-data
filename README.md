# Data In the Wild Exam Project
This repository contains the code and documentation for the "Data in the Wild" exam project for the course at IT University of Copenhagen. The project involves scraping, processing, analyzing, and visualizing data collected from GreenMobility car-sharing service.

This project was created by:
- Abel Jozsef Szemler (absz@itu.dk)
- Benjamin Storm Larsen (bsla@itu.dk)
- Florentina Fabregas Alippi (flfa@itu.dk)
- Miina Johanna Mäkinen (miin@itu.dk)

## Scraping
The scraper is built with GoLang and is found in the `scraper/` directory. To run it you need to have Go installed on your machine and the `awscli` configured with your AWS credentials, and update the S3 bucket name and region in the `main.go` file. To run it simply use the command:
```bash
go run main.go
```
or build it with (MacOS/Linux):
```bash
go build -o scraper main.go
chmod +x scraper
./scraper
```


## Pre-requisites
The data processing and analysis scripts are written in Python 3.11.14. It is recommended to use a virtual environment. You can create and activate a virtual environment using the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
```

Then, install the required packages using pip, we made sure to add all the required packages in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Data Processing
The data processing scripts are found in the `src/` directory. The main scripts are:
- `build_csv.py`: This script processes the raw data files and builds a consolidated CSV file
- `data_transformation.py`: This script performs data transformation and groups the data to single trips. This script also contains our data annotation logic.

Given the size of the full dataset it was not possible to include it in the repository. However, a sample of the data is included in the `data/example.json` directory for testing and development purposes. The full dataset requires to run the full data pipeline.

Instead we included the output from the data processing step in the `data/transformed.csv` file, which can be used for analysis and visualization without needing to run the data processing step. The data processing step is also computationally intensive and may require a machine with higher specifications and good patience to run it.


## Data Analysis and Visualization
The data analysis and visualization scripts are also found in the `src/` directory and inside notebooks in the `notebooks/` directory. Running all the notebooks in the `notebooks/` and the non data processing scripts in the `src/` directory will generate the visualizations and analysis results.

## Artifacts
The `artifacts/` directory contains generated files such as maps and visualizations created during the analysis and visualization process.


