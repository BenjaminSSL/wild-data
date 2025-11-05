import logging
import pandas as pd
import argparse
from pathlib import Path


logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    args = argparse.ArgumentParser(description="Group static car positions into a single row per car.")
    args.add_argument('--input', type=str, required=True,  help="Input CSV file path.")
    args.add_argument('--output', type=str, required=False, default="data/output.csv", help="Output CSV file path.")
    args = args.parse_args()
 
    input_path = Path(args.input)
    output_path = Path(args.output)
    df = pd.read_csv(input_path)
    logger.debug(f"Read {len(df)} rows from {input_path}")


    # Sort by carId and file_datetime to ensure correct grouping
    df = df.sort_values(by=['carId', 'file_datetime'])






if __name__ == "__main__":
    main()  