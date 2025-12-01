import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import argparse
import folium


def main():
    parser = argparse.ArgumentParser("Detect hotspots in car pickup locations using DBSCAN clustering.")
    parser.add_argument(
        "--input",
        type=str,
        required=False,
        default="data/group.csv",
    )

    args = parser.parse_args()

    df = pd.read_csv(args.input)

    # Sample 10% of data for clustering to reduce computation
    df = df.sample(frac=0.1, random_state=42).reset_index(drop=True)

    lat = df["lat"].values
    lon = df["lon"].values

    coords = np.radians(np.column_stack((lat, lon)))

    kms_per_radian = 6371.0088

    eps_km = 0.5 
    db = DBSCAN(
        eps=eps_km / kms_per_radian,
        min_samples=10,       
        metric="haversine",
        algorithm="ball_tree",
        n_jobs=-1,
    ).fit(coords)

    labels = db.labels_
    df["cluster"] = labels

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    print("Clusters found:", n_clusters)

    center_lat = df["lat"].mean()
    center_lon = df["lon"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")
    # ----- Compute cluster centers and sizes -----
    clustered = df[df["cluster"] != -1]

    if clustered.empty:
        print("No clusters found (all noise).")
        m.save("data/hotspot_map.html")
        return

    group = clustered.groupby("cluster")
    centers = group[["lat", "lon"]].mean().reset_index()
    sizes = group.size().reset_index(name="count")

    centers = centers.merge(sizes, on="cluster")

    MIN_CLUSTER_SIZE = 20  # change as you like
    centers = centers[centers["count"] >= MIN_CLUSTER_SIZE]

    print(f"Clusters plotted (size >= {MIN_CLUSTER_SIZE}):", len(centers))

    for _, row in centers.iterrows():
        cluster_id = int(row["cluster"])
        count = int(row["count"])

        radius = min(40, 5 + np.log1p(count) * 5)

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=radius,
            color="red",
            fill=True,
            fill_opacity=0.6,
            popup=f"Cluster {cluster_id} (n={count})",
        ).add_to(m)

    m.save("data/hotspot_map.html")
    print("Saved interactive map to data/hotspot_map.html")


if __name__ == "__main__":
    main()
