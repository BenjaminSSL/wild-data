import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import argparse
import folium


KMS_PER_RADIAN = 6371.0088
ROUND_DECIMALS = 10
EPS_KM = 0.2
MIN_CLUSTER_SIZE_DEFAULT = 20

CPH_AIRPORT_COORDS = (55.630397, 12.648908)
BILLUND_AIRPORT_COORDS = (55.740020, 9.151920)
AARHUS_AIRPORT_COORDS = (56.303878, 10.619709)
AARHUS_SEAPLANE_COORDS = (56.150649, 10.253114)
def main():
    parser = argparse.ArgumentParser("Detect hotspots in car pickup locations using DBSCAN clustering.")
    parser.add_argument(
        "--input",
        type=str,
        required=False,
        default="data/group.csv",
    )

    args = parser.parse_args()

    df = pd.read_csv(
        args.input,
        usecols=["lat", "lon"],
        dtype={"lat": "float32", "lon": "float32"},
    )

    df = df.dropna(subset=["lat", "lon"])
    df = df[
        (df["lat"].between(-90, 90)) &
        (df["lon"].between(-180, 180))
    ].reset_index(drop=True)

    lat = df["lat"].to_numpy(copy=False)
    lon = df["lon"].to_numpy(copy=False)

    lat_r = np.round(lat, ROUND_DECIMALS)
    lon_r = np.round(lon, ROUND_DECIMALS)

    scale = 10 ** ROUND_DECIMALS

    lat_i = np.asarray((lat_r + 90.0) * scale, dtype=np.int64)
    lon_i = np.asarray((lon_r + 180.0) * scale, dtype=np.int64)
    keys = lat_i * 1_000_000_000 + lon_i

    unique_keys, inverse = np.unique(keys, return_inverse=True)

    first_idx = np.zeros(unique_keys.shape[0], dtype=np.int64)
    first_pos = np.full(unique_keys.shape[0], -1, dtype=np.int64)
    for i, u in enumerate(inverse):
        if first_pos[u] == -1:
            first_pos[u] = i
    first_idx = first_pos

    lat_u = lat_r[first_idx]
    lon_u = lon_r[first_idx]

    coords_u = np.radians(np.column_stack([lat_u, lon_u]).astype(np.float64, copy=False))
    eps = EPS_KM / KMS_PER_RADIAN
    db = DBSCAN(
        eps=eps,
        min_samples=10,
        metric="haversine",
        algorithm="ball_tree",
        leaf_size=40,
        n_jobs=-1,
    ).fit(coords_u)

    labels_u = db.labels_

    labels = labels_u[inverse]
    df["cluster"] = labels

    n_clusters = int(len(set(labels)) - (1 if -1 in labels else 0))
    print("Rows:", len(df))
    print("Clusters found:", n_clusters)

    center_lat = float(df["lat"].mean())
    center_lon = float(df["lon"].mean())
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")

    clustered = df[df["cluster"] != -1]
 

    group = clustered.groupby("cluster", sort=False)
    centers = group[["lat", "lon"]].mean()
    sizes = group.size().rename("count")
    centers = centers.join(sizes).reset_index()

    centers = centers[centers["count"] >= MIN_CLUSTER_SIZE_DEFAULT] 
    print(f"Clusters plotted (size >= {MIN_CLUSTER_SIZE_DEFAULT}):", len(centers))

    for _, row in centers.iterrows():
        cluster_id = int(row["cluster"])
        count = int(row["count"])
        radius = float(min(40, 5 + np.log1p(count) * 5))
        
        # Color blue if close to any airport, else red
        color  = "blue" if any(
            np.sqrt(
                (row["lat"] - airport[0])**2 +
                (row["lon"] - airport[1])**2
            ) < margin
            for airport, margin in [
                (CPH_AIRPORT_COORDS,0.005),
                (BILLUND_AIRPORT_COORDS,0.05),
                (AARHUS_AIRPORT_COORDS,0.05),
                (AARHUS_SEAPLANE_COORDS,0.02),
            ]
        ) else "green"

        
        folium.CircleMarker(
            location=[float(row["lat"]), float(row["lon"])],
            radius=radius,
            color=color,
            fill=True,
            fill_opacity=0.6,
        ).add_to(m)

    m.save("artifacts/cluster_map.html")
    print(f"Saved interactive map to artifacts/cluster_map.html")

if __name__ == "__main__":
    main()
