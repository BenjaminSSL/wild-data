#!/usr/bin/env bash

echo "Building CSV from raw data..."
python3 src/build_csv.py --input data/raw/ --output data/output.csv

echo "Transforming data..."
python3 src/data_transformation.py --input data/output.csv --output data/data_transformed.csv

echo "Data transformation complete. Transformed data saved to data/data_transformed.csv"