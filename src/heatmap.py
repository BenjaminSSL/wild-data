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

    # Drop rows with missing coordinates or time
    df = df.dropna(subset=["lat", "lon", "start_time"])
    print(f"{len(df)} rows after dropping rows with missing lat/lon/start_time")

    df["start_time"] = pd.to_datetime(df["start_time"])

    m_static = folium.Map(
        location=[df["lat"].mean(), df["lon"].mean()],
        zoom_start=12,
    )

    heat_data_static = df[["lat", "lon"]].values.tolist()
    HeatMap(heat_data_static).add_to(m_static)

    m_static.save("data/heatmap_static.html")
    print("Static heatmap saved to data/heatmap_static.html")

    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()

    df["day"] = df["start_time"].dt.date  # calendar day

    heat_data_days = []
    time_index_days = []

    for day, group in df.groupby("day"):
        day_points = group[["lat", "lon"]].values.tolist()
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

    m_days.save("data/vehicle_heatmap_per_day.html")
    print("Per-day heatmap saved to data/vehicle_heatmap_per_day.html")

    df["hour"] = df["start_time"].dt.floor("H")

    heat_data_hours = []
    time_index_hours = []

    for hour, group in df.sort_values("hour").groupby("hour"):
        hour_points = group[["lat", "lon"]].values.tolist()
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

    m_hours.save("data/vehicle_heatmap_per_hour.html")
    print("Per-hour heatmap saved to data/vehicle_heatmap_per_hour.html")


if __name__ == "__main__":
    main()
