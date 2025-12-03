import pandas as pd
import argparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("--input", type=str, required=True, help="Path to the input data file (CSV)")

    args = parser.parse_args()

    df = pd.read_csv(args.input)

    logger.info(f"Loaded data with {len(df)} rows from {args.input}")

    # Unique number plates
    unique_plates = df['licencePlate'].nunique()
    logger.info(f"Number of unique licence plates: {unique_plates}")

    per_vehicle = df.groupby("licencePlate", sort=False)["car_type"].first()

    counts = per_vehicle.value_counts()

    car_count = int(counts.get("car", 0))
    van_count = int(counts.get("van", 0))
    total_count = car_count + van_count

    logger.info(f"Total number of cars: {car_count} out of {total_count} vehicles, which is {car_count / total_count:.2%}")
    logger.info(f"Total number of vans: {van_count} out of {total_count} vehicles, which is {van_count / total_count:.2%}")


    


    

if __name__ == "__main__":
    main()