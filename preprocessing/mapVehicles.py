def correct_vehicle_names(df):

    import pandas as pd
    import numpy as np

    # generate list of columns on which to operate
    col_id = df.columns.str.match("vehicle type")
    cols = df.columns[col_id].tolist()

    # Convert to lowercase and remove whitespaces both leading and trailing
    for col in cols:
        df[col] = df[col].str.lower()
        df[col] = df[col].str.strip()

    # Perform vehicle name correction
    vehiclename_dict = vehiclename_corrector()

    for col in cols:
        for old, new in vehiclename_dict.items():
            df[col] = df[col].replace(old, new, regex=False)

    # Replace all instances with less than 5 incidents in column "vehicle type code 1" and
    # all instances with less than 3 incidents in column "vehicle type code 2" with "other".
    target_idgroup1 = df["vehicle type code 1"].value_counts()
    target_idgroup1 = target_idgroup1[target_idgroup1 < 5]

    target_idgroup2 = df["vehicle type code 2"].value_counts()
    target_idgroup2 = target_idgroup2[target_idgroup2 < 3]

    target_ids = pd.concat([target_idgroup1, target_idgroup2]).index

    for col in cols:
        mask = df[col].isin(target_ids)
        df.loc[mask, col] = "other"

    return df


def vehiclename_corrector():
    vehiclename_lookup = {

        "bicycle": "bike",

        "sedan": "passenger vehicle",
        "station wagon/sport utility vehicle": "passenger vehicle",
        "sport utility / station wagon": "passenger vehicle",
        "4 dr sedan": "passenger vehicle",
        "2 dr sedan": "passenger vehicle",
        "convertible": "passenger vehicle",

        "truck": "pick-up truck",
        "pick up tr": "pick-up truck",

        "livery vehicle": "limousine",
        "limo": "limousine",
        "limou": "limousine",

        "posta": "mail truck",
        "usps": "mail truck",
        "usps mail": "mail truck",

        "ambu": "ambulance",
        "ambul": "ambulance",

        "garbage tr": "garbage truck",
        "garbage or refuse": "garbage truck",
        "sanit": "garbage truck",

        "cement tru": "cement truck",
        "concrete mixer": "cement truck",

        "dump": "dump truck",

        "fire": "fire truck",
        "fdny": "fire truck",
        "firet": "fire truck",
        "fire engin": "fire truck",

        "small com veh(4 tires)": "small com veh",
        "ford sprin": "small com veh",
        "sprin": "small com veh",
        "refrigerated van": "small com veh",
        "deliv": "small com veh",

        "large com veh(6 or more tires)": "large com veh",
        "box t": "large com veh",
        "box truck": "large com veh",
        "tow truck / wrecker": "large com veh",
        "chassis cab": "large com veh",
        "beverage truck": "large com veh",
        "flat bed": "large com veh",
        "comme": "large com veh",
        "pallet": "large com veh",
        "armored truck": "large com veh",

        "tanker": "tractor truck",
        "tractor truck gasoline": "tractor truck",
        "tractor truck diesel": "tractor truck",

        "schoo": "school bus",
        "mta b": "bus",
        "postal bus": "bus",

        "motorbike": "motorcycle",
        "dirt bike": "motorcycle",
        "dirtbike": "motorcycle",

        "moped scoo": "moped",
        "moped elec": "moped",

        "e-bik": "e-bike",
        "e bike": "e-bike",
        "ebike": "e-bike",
        "scoot": "scooter",
        "e sco": "e-scooter",
        "e-sco": "e-scooter",
        "unkno": "unknown"
    }
    return vehiclename_lookup
