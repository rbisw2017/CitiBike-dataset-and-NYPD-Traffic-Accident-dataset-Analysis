def get_zipcode_borough_using_NYmapinfo(df):

    """
    Function for filling in missing zipcodes and boroughs in bike accident instances. It takes in the
    latitude and longitude of an accident location, computes distance from recorded NY locations using
    their latitude, longitude information.
    """
    import pandas as pd
    import numpy as np

    # Loading zipcode and location (latitude, longitude) information of NY
    ny = pd.read_csv("NY-zip-code-latitude-and-longitude.csv",delimiter=";", usecols=[0, 1, 3, 4])

    # Removing missing positions
    mask = (df["latitude"] < 35) | (df["longitude"] > -65)
    df.loc[mask, "latitude"] = np.nan
    df.loc[mask, "longitude"] = np.nan

    # Selecting subset of NY locations pertaining to bike accident dataset.
    minlat, maxlat = np.min(df["latitude"]), np.max(df["latitude"])
    minlon, maxlon = np.min(df["longitude"]), np.max(df["longitude"])

    latlonmask = (ny["Longitude"] >= minlon) & (ny["Longitude"] <= maxlon)
    latlonmask = latlonmask & (ny["Latitude"] >= minlat) & (ny["Latitude"] <= maxlat)
    ny = ny[latlonmask]

    # Collect accident instances that have missing zipcodes
    missing_mask = df["zip code"].isnull().to_numpy()
    missing_ind = np.nonzero(missing_mask)[0]

    borough_col = np.argwhere(df.columns == "borough")[0]
    zip_col = np.argwhere(df.columns == "zip code")[0]

    for k in missing_ind:
        dist = (df.iloc[k]["longitude"] - ny["Longitude"])**2 + (df.iloc[k]["latitude"] - ny["Latitude"])**2
        dist = dist.to_numpy()

        nearest_ind = np.argmin(dist)
        nearest_zip = ny.iloc[nearest_ind]["Zip"]
        nearest_borough = ny.iloc[nearest_ind]["City"]

        dist = dist[nearest_ind]

        if np.isfinite(dist):
            df.iloc[k, zip_col] = nearest_zip
            df.iloc[k, borough_col] = nearest_borough

    # Removing all rows from the dataframe that does not have a borough and hence a zipcode
    mask = df["borough"].isna()
    df = df[~mask]

    df["zip code"] = df["zip code"].astype(str)

    # Regularizing the names of the five boroughs
    # "New York" is recorded as Manhattan in the zip code file
    df["borough"] = df["borough"].str.replace("New York", "MANHATTAN")

    df["borough"] = df["borough"].str.replace("Bronx", "BRONX")
    df["borough"] = df["borough"].str.replace("Brooklyn", "BROOKLYN")
    df["borough"] = df["borough"].str.replace("Staten Island", "STATEN ISLAND")

    # Everything else appear to be in Queens
    # Find them by checking for strings that are not in all caps.
    mask = df["borough"].str.isupper()
    mask = ~mask

    df.loc[mask, "borough"] = "QUEENS"

    return df
