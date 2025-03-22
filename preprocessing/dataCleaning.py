def clean_data(df):
    """
    Function for cleaning the bike accident dataset.
    """

    import pandas as pd
    import numpy as np

    # Arrange columns in alphabetical order.
    df.sort_index(axis=1, inplace=True)

    # Remove the redundant column "Location" as latitude and longitude information is already available.
    df.drop(columns="location", inplace=True)

    # Format date and time into datetime64 format.
    crash_dt = df["crash date"] + " " + df["crash time"]
    crash_dt = pd.to_datetime(crash_dt)
    df.insert(0, "datetime", crash_dt)
    df.drop(columns=["crash date", "crash time"], inplace=True)

    # Arrange the accidents by timestamp.
    df.sort_values(by="datetime", inplace=True, ignore_index=True)

    # Remove missing positions.
    mask = (df["latitude"] < 35) | (df["longitude"] > -65)
    df.loc[mask, "latitude"] = np.nan
    df.loc[mask, "longitude"] = np.nan

    # Regularize contributing factors.
    mask = df["contributing factor vehicle 1"].str.fullmatch("illnes", case=False)
    mask.fillna(False, inplace=True)
    df.loc[mask, "contributing factor vehicle 1"] = "Illness"

    # Remove the column "off-street name" as most instances are missing value.
    df.drop(columns="off street name", inplace=True)

    # Regularize the street names by Titlizing them.
    df["on street name"] = df["on street name"].str.title()
    df["cross street name"] = df["cross street name"].str.title()

    # Regularize borough names by capitalizing them.
    df["borough"] = df["borough"].str.capitalize()

    # Regularize the columns "number of persons injured" and "number of persons killed"
    # They have some missing values, and we correct them here.
    na_rows = df["number of persons injured"].isna()
    na_rows = df.loc[na_rows, :].index

    df.loc[na_rows[0], "number of persons injured"] = 0
    df.loc[na_rows[0], "number of persons killed"] = 0

    df.loc[na_rows[1], "number of persons injured"] = 1
    df.loc[na_rows[1], "number of persons killed"] = 0

    df["number of persons injured"] = df["number of persons injured"].astype("Int64")
    df["number of persons killed"] = df["number of persons killed"].astype("int")

    # Remove all the accident instances where no cyclist is involved.
    # For this we assume that in the vehicle column "bike" should be present or
    # there should be either an injury or death of a cyclist.

    col_ind = df.columns.str.match("vehicle_type")
    cols = df.columns[col_ind].tolist()

    new_str = df["vehicle type code 1"]
    for col in cols[1:]:
        new_str = new_str.str.cat(df[col], sep=",", na_rep="")

    has_bike = new_str.str.contains("bike")

    cyclist_mask = (df["number of cyclist injured"] > 0) | (df["number of cyclist killed"] > 0)

    # Join masks, that is, combine them.
    the_mask = has_bike | cyclist_mask

    # Filter and retain only the rows needed.
    df = df.loc[the_mask]

    df.drop_duplicates(inplace=True, ignore_index=True)

    return df

