import argparse
import pandas as pd
import numpy as np
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Data Transformation Script")
    parser.add_argument("--input", type=str, required=True, help="Path to the input data file (CSV)")
    parser.add_argument("--output", type=str, required=True, help="Path to the output data file")
    args = parser.parse_args()

    df = pd.read_csv(args.input)

    logger.info(f"Loaded data with {len(df)} rows from {args.input}")

    # Strip whitespace from column names
    df.rename(columns=lambda x: x.strip(), inplace=True)

    logger.info("Stripped whitespace from column names")

    # Ensure 'licencePlate' column is string type and normalize its values
    df["licencePlate"] = (
        df["licencePlate"]
        .astype(str)
        .str.lower()
        .str.replace(" ", "", regex=False)
        .str.strip()
    )
    logger.info("Normalized 'licencePlate' values")

    # Convert 'file_datetime' to datetime and sort the DataFrame
    df["file_datetime"] = pd.to_datetime(df["file_datetime"], errors="coerce")
    df = df.sort_values(['licencePlate', 'file_datetime']).reset_index(drop=True)

    logger.info("Converted 'file_datetime' to datetime and sorted the DataFrame")

    # Extract numeric part of 'zipCode', convert to float, handle missing values, and convert to int
    df["zipCode"] = (df["zipCode"].astype(str).str.extract(r'(\d{4})').astype(float).fillna(-1).astype(int))

    thr = 1e-3

    lat  = df['lat'].to_numpy()
    lon  = df['lon'].to_numpy()
    plate= df['licencePlate'].to_numpy()

    # Plate change
    plate_change = np.r_[True, plate[1:] != plate[:-1]]

    # Location change
    move_change = np.r_[False,
        (np.abs(lat[1:] - lat[:-1]) > thr) |
        (np.abs(lon[1:] - lon[:-1]) > thr)
    ]

    # Any boundary event
    boundary = plate_change | move_change
    b_idx = np.flatnonzero(boundary)

    # Closing segments
    end_idx   = np.r_[b_idx[1:] - 1, len(df) - 1]
    start_idx = b_idx[:len(end_idx)]

    # Build output
    grouped = pd.DataFrame({
        "licencePlate": df.loc[start_idx, "licencePlate"].to_numpy(),
        "start_time":   df.loc[start_idx, "file_datetime"].to_numpy(),
        "end_time":     df.loc[end_idx,   "file_datetime"].to_numpy(),
        "start_lat":    df.loc[start_idx, "lat"].to_numpy(),
        "start_lon":    df.loc[start_idx, "lon"].to_numpy(),
        "parking_time": np.round(
            (df.loc[end_idx, "file_datetime"].to_numpy() -
             df.loc[start_idx, "file_datetime"].to_numpy()) /
             np.timedelta64(1, "m")
        ).astype(int),
        "vehicleTypeId": df.loc[start_idx, "vehicleTypeId"].astype(str).to_numpy(),
        "zipCode": df.loc[start_idx, "zipCode"].to_numpy()
    })

    logger.info("Built grouped DataFrame")

    grouped['car_type'] = grouped['vehicleTypeId'].apply(id_to_car_type)

    logger.info("Mapped vehicleTypeId to car_model and car_type")

    grouped['area_name'] = grouped['zipCode'].apply(postcode_mapping)


    logger.info("Mapped zipCode to area codes")
    grouped["day_of_week_start"] = pd.to_datetime(grouped["start_time"]).dt.day_name()
    grouped["hour_of_day_start"] = pd.to_datetime(grouped["start_time"]).dt.hour

    grouped["day_of_week_end"] = pd.to_datetime(grouped["end_time"]).dt.day_name()
    grouped["hour_of_day_end"] = pd.to_datetime(grouped["end_time"]).dt.hour



    logger.info("Extracted day_of_week and hour_of_day from start_time")

    grouped.to_csv(args.output, index=False)

    logger.info(f"Saved transformed data to {args.output}")



def id_to_car_type(vehicle_type_id):
    car_types = {
        "1": {"model":"Renault Zoe","type":"car"},
        "2": {"model":"Renault Zoe","type":"car"},
        "6": {"model":"unknown","type":"van"},
        "9":  {"model":"Renault Zoe","type":"car"},
        "10": {"model":"Renault Zoe","type":"car"},
        "14": {"model":"Renault Zoe","type":"car"},
        "25": {"model":"unknown","type":"van"},
        "26": {"model":"Renault Zoe","type":"car"},
        "31": {"model":"unknown","type":"van"},
        "32": {"model":"SAIC Motor MAXUS E-Deliver 3","type":"van"},
        "34": {"model":"Renault Zoe","type":"car"},
        "35": {"model":"Renault Zoe","type":"car"},
        "57": {"model":"Renault Zoe","type":"car"},
        "64": {"model":"Renault Zoe","type":"car"},
        "74": {"model":"unknown","type":"van"},
        "76": {"model":"Mercedes eVito","type":"van"},
        "77": {"model":"Renault Zoe","type":"car"},
        "79": {"model":"Peugeot e-Partner","type":"van"},
        "86": {"model":"Renault Zoe","type":"car"},
        "91": {"model":"Renault Zoe","type":"car"},
        "94": {"model":"Renault Zoe","type":"car"},
        "95": {"model":"Renault Kangoo","type":"van"},
        "96": {"model":"Renault Zoe","type":"car"},
        "97": {"model":"Renault Zoe","type":"car"},
        "99": {"model":"Renault Zoe","type":"car"},
        "102": {"model":"Renault Megane","type":"car"},
        "103": {"model":"Opel Vivaro Electric","type":"van"},
        "105": {"model":"Renault Zoe","type":"car"},
        "106": {"model":"Renault Zoe","type":"car"},
        "107": {"model":"Renault Zoe","type":"car"},
        "109": {"model":"Renault Trafic E-Tech","type":"van"},
        "111": {"model":"Ford E-Transit","type":"van"}
    }
    return car_types.get(vehicle_type_id)["type"] if vehicle_type_id in car_types else "unknown"

    


def postcode_mapping(zip_code):
    post_codes = {
        1: {"name": "Bronshoj",         "zip_from": 2700, "zip_to": 2700, "setting": 2700},
        2: {"name": "Kobenhavn K",      "zip_from": 1050, "zip_to": 1473, "setting": 1050},
        3: {"name": "Kobenhavn N",      "zip_from": 2200, "zip_to": 2200, "setting": 2200},
        4: {"name": "Kobenhavn NV",     "zip_from": 2400, "zip_to": 2400, "setting": 2400},
        5: {"name": "Kobenhavn O",      "zip_from": 2100, "zip_to": 2100, "setting": 2100},
        6: {"name": "Kobenhavn S",      "zip_from": 2300, "zip_to": 2300, "setting": 2300},
        7: {"name": "Kobenhavn SV",     "zip_from": 2450, "zip_to": 2450, "setting": 2450},
        8: {"name": "Kobenhavn V",      "zip_from": 1550, "zip_to": 1799, "setting": 1550},
        9: {"name": "Nordhavn",         "zip_from": 2150, "zip_to": 2150, "setting": 2150},
        10: {"name": "Valby",           "zip_from": 2500, "zip_to": 2500, "setting": 2500},
        11: {"name": "Vanlose",         "zip_from": 2720, "zip_to": 2720, "setting": 2720},
        12: {"name": "Frederiksberg C", "zip_from": 1800, "zip_to": 2000, "setting": 2000},
        13: {"name": "Hellerup",        "zip_from": 2900, "zip_to": 2900, "setting": 2900},
        14: {"name": "Soborg",        "zip_from": 2860, "zip_to": 2860, "setting": 2860},
        15: {"name": "Herlev",          "zip_from": 2730, "zip_to": 2730, "setting": 2730},
        16: {"name": "Skovlunde",       "zip_from": 2740, "zip_to": 2740, "setting": 2740},
        17: {"name": "Ballerup",        "zip_from": 2750, "zip_to": 2750, "setting": 2750},
        18: {"name": "Glostrup",        "zip_from": 2600, "zip_to": 2600, "setting": 2600},
        19: {"name": "Hvidovre",        "zip_from": 2650, "zip_to": 2650, "setting": 2650},
        20: {"name": "Albertslund",     "zip_from": 2620, "zip_to": 2620, "setting": 2620},
        21: {"name": "Taastrup",        "zip_from": 2630, "zip_to": 2630, "setting": 2630},
        22: {"name": "Brondby Strand","zip_from": 2660, "zip_to": 2660, "setting": 2660},
        23: {"name": "Kgs. Lyngby",     "zip_from": 2800, "zip_to": 2800, "setting": 2800},
        24: {"name": "Virum",           "zip_from": 2830, "zip_to": 2830, "setting": 2830},
        25: {"name": "Dyssegoord",     "zip_from": 2870, "zip_to": 2870, "setting": 2870},
        26: {"name": "Gentofte",        "zip_from": 2820, "zip_to": 2820, "setting": 2820}
    }   
    
    for code, info in post_codes.items():
        if info["zip_from"] <= zip_code <= info["zip_to"]:
            return info["name"]
    return "NOT_ANNOTATED"




if __name__ == "__main__":
    main()
