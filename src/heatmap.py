import argparse
import pandas as pd
import folium
from folium.plugins import HeatMap, HeatMapWithTime


def main():
    parser = argparse.ArgumentParser(
        description="Generate heatmaps (static, per-day, and per-hour) from grouped car positions."
    )
    parser.add_argument(
        "--input",
        type=str,
        required=False,
        default="data/group.csv",
        help="Input CSV file path.",
    )

    args = parser.parse_args()

    df = pd.read_csv(args.input)
    print(f"Read {len(df)} rows from {args.input}")

    # drop if parking_time is 0
    df = df[df["parking_time"] > 0].reset_index(drop=True)

    # Drop rows with missing coordinates or time
    df = df.dropna(subset=["start_lat", "start_lon", "end_time"])
    print(f"{len(df)} rows after dropping rows with missing lat/lon/end_time")

    df["end_time"] = pd.to_datetime(df["end_time"])

    m_static = folium.Map(
        location=[df["start_lat"].mean(), df["start_lon"].mean()],
        zoom_start=12,
    )

    heat_data_static = df[["start_lat", "start_lon"]].values.tolist()
    HeatMap(heat_data_static).add_to(m_static)

    m_static.save("artifacts/heatmap_static.html")
    print("Static heatmap saved to artifacts/heatmap_static.html")

    center_lat = df["start_lat"].mean()
    center_lon = df["start_lon"].mean()

    df["day"] = df["end_time"].dt.date  # calendar day

    heat_data_days = []
    time_index_days = []

    for day, group in df.groupby("day"):
        day_points = group[["start_lat", "start_lon"]].values.tolist()
        day_points = [[lat, lon, 0.3] for lat, lon in day_points]
        heat_data_days.append(day_points)
        time_index_days.append(day.strftime("%Y-%m-%d"))

    m_days = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    HeatMapWithTime(
        heat_data_days,
        index=time_index_days,  
        auto_play=False,
        max_opacity=0.8,
        radius=7,
    ).add_to(m_days)

    m_days.save("artifacts/vehicle_heatmap_per_day.html")
    print("Per-day heatmap saved to artifacts/vehicle_heatmap_per_day.html")

    df["hour"] = df["end_time"].dt.floor("H")

    heat_data_hours = []
    time_index_hours = []

    for hour, group in df.sort_values("hour").groupby("hour"):
        hour_points = group[["start_lat", "start_lon"]].values.tolist()
        hour_points = [[lat, lon, 0.3] for lat, lon in hour_points]
        heat_data_hours.append(hour_points)
        time_index_hours.append(hour.strftime("%Y-%m-%d %H:%M"))

    m_hours = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    HeatMapWithTime(
        heat_data_hours,
        index=time_index_hours, 
        auto_play=False,
        max_opacity=0.8,
        radius=7,
    ).add_to(m_hours)

    m_hours.save("artifacts/vehicle_heatmap_per_hour.html")
    print("Per-hour heatmap saved to artifacts/vehicle_heatmap_per_hour.html")

    # Heatmap with parking time
    heat_data_parking = []
    for _, row in df.iterrows():
        heat_data_parking.append([
            row["start_lat"],
            row["start_lon"],
            max(1, min(row["parking_time"] / 60, 10))  
        ])
    m_parking = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
    )

    HeatMap(heat_data_parking).add_to(m_parking)

    m_parking.save("artifacts/vehicle_heatmap_parking_time.html")
    print("Heatmap with parking time saved to artifacts/vehicle_heatmap_parking_time.html")


if __name__ == "__main__":
    main()
