import pandas as pd

path_to_csv = "../data/mapped_output.csv"

df_mapped_out = pd.read_csv(path_to_csv)

post_codes = {
    1: {"name": "Bronshoj",         "zip_from": "2700", "zip_to": "2700", "setting": "2700"},
    2: {"name": "Kobenhavn K",      "zip_from": "1050", "zip_to": "1473", "setting": "1050"},
    3: {"name": "Kobenhavn N",      "zip_from": "2200", "zip_to": "2200", "setting": "2200"},
    4: {"name": "Kobenhavn Nv",     "zip_from": "2400", "zip_to": "2400", "setting": "2400"},
    5: {"name": "Kobenhavn O",      "zip_from": "2100", "zip_to": "2100", "setting": "2100"},
    6: {"name": "Kobenhavn S",      "zip_from": "2300", "zip_to": "2300", "setting": "2300"},
    7: {"name": "Kobenhavn Sv",     "zip_from": "2450", "zip_to": "2450", "setting": "2450"},
    8: {"name": "Kobenhavn V",      "zip_from": "1550", "zip_to": "1799", "setting": "1550"},
    9: {"name": "Nordhavn",         "zip_from": "2150", "zip_to": "2150", "setting": "2150"},
    10: {"name": "Valby",           "zip_from": "2500", "zip_to": "2500", "setting": "2500"},
    11: {"name": "Vanlose",         "zip_from": "2720", "zip_to": "2720", "setting": "2720"},
    12: {"name": "Frederiksberg C", "zip_from": "1800", "zip_to": "2000", "setting": "2000"},
}
# ensure numeric types for comparison
df_codes = pd.DataFrame(post_codes).T
df_codes['zip_from'] = df_codes['zip_from'].astype(int)
df_codes['zip_to']   = df_codes['zip_to'].astype(int)
# Fill NA with -1 so its also numeric
df_mapped_out['zipCode'] = df_mapped_out['zipCode'].fillna(-1)
df_mapped_out['zipCode'] = df_mapped_out['zipCode'].astype(int)
# Build intervals including both from and to
iv = pd.IntervalIndex.from_arrays(df_codes['zip_from'], df_codes['zip_to'], closed='both')
zips = df_mapped_out['zipCode'].to_numpy()
# has length of dataset, values are interval position
pos  = iv.get_indexer(zips)  # -1 where no interval matches
mask = pos != -1
zip_fixed = zips.copy()
# assign same zips for same kommune
zip_fixed[mask] = df_codes['setting'].to_numpy()[pos[mask]]
df_mapped_out['zipCodeFixed'] = zip_fixed

# Save
# print(df_mapped_out[["zipCode","zipCodeFixed"]])
# save_path = "../data/fixedZip_output.csv"
# df_mapped_out.to_csv(save_path)