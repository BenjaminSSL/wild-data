import logging
import pandas as pd
import argparse
from pathlib import Path
import numpy as np


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

    df["licencePlate"] = df["licencePlate"].str.lower().str.replace(" ", "").str.strip()

    df.sort_values(by=["licencePlate","file_datetime"], inplace=True)

    df = df[["licencePlate","file_datetime","lat","lon","zipCode","fuelLevel","vehicleTypeId"]]

    thr = 1e-3

    lat   = df['lat'].to_numpy()
    lon   = df['lon'].to_numpy()
    plate = df['licencePlate'].to_numpy()

    plate_change = np.r_[True, plate[1:] != plate[:-1]]
    move_change  = np.r_[False,
                         (np.abs(lat[1:] - lat[:-1]) > thr) |
                         (np.abs(lon[1:] - lon[:-1]) > thr)]
    boundary = plate_change | move_change

    b_idx = np.flatnonzero(boundary)

    end_idx   = np.r_[b_idx[1:] - 1, len(df) - 1]
    start_idx = b_idx[:len(end_idx)]


    grouped = pd.DataFrame({
        "licencePlate": df.loc[start_idx, "licencePlate"].to_numpy(),
        "start_time":   df.loc[start_idx, "file_datetime"].to_numpy(),
        "end_time":     df.loc[end_idx,   "file_datetime"].to_numpy(),
        "lat":    df.loc[start_idx, "lat"].to_numpy(),
        "lon":    df.loc[start_idx, "lon"].to_numpy(),
        "zipCode": df.loc[start_idx, "zipCode"].to_numpy(),
        "fuelLevel": df.loc[start_idx, "fuelLevel"].to_numpy(),
        "vehicleTypeId": df.loc[start_idx, "vehicleTypeId"].to_numpy(),
    })

    grouped.to_csv(output_path, index=False)
    logger.info(f"Wrote grouped data with {len(grouped)} rows to {output_path}")



if __name__ == "__main__":
    main()  