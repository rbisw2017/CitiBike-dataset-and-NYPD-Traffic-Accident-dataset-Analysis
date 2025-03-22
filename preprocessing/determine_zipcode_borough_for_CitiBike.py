def get_zipcode_borough_info(df):

    """Function for filling in zipcode and borough information for citibike trips. It takes in the starting station
    latitude and longitude for a bike trip, computes distance from recorded NY locations using
    their latitude, longitude information and selects the zipcode and borough that has the least distance.
    """
    import pandas as pd
    import numpy as np

    # Loading zipcode and location (latitude, longitude) information of NY
    ny = pd.read_csv("NY-zip-code-latitude-and-longitude.csv", delimiter=";", usecols=[0, 1, 3, 4])

    # Selecting subset of NY locations pertaining to bike accident dataset.
    minlat, maxlat = np.min(df["start_lat"]), np.max(df["start_lat"])
    minlon, maxlon = np.min(df["start_lng"]), np.max(df["start_lng"])

    latlonmask = (ny["Longitude"] >= minlon) & (ny["Longitude"] <= maxlon)
    latlonmask = latlonmask & (ny["Latitude"] >= minlat) & (ny["Latitude"] <= maxlat)
    ny = ny[latlonmask]

    # Initialize the columns borough and zipcode
    df["borough"] = np.nan
    df["zipcode"] = np.nan

    # get indices of trips missing a zipcode
    missing_mask = df["zipcode"].isnull().to_numpy()
    missing_ind = np.nonzero(missing_mask)[0]

    borough_col = np.argwhere(df.columns == "borough")[0]
    zip_col = np.argwhere(df.columns == "zipcode")[0]

    print("\nStarted determining zipcode and borough information for all locations.")
    for k in missing_ind:
        dist = (df.iloc[k]["start_lng"] - ny["Longitude"])**2 + (df.iloc[k]["start_lat"] - ny["Latitude"])**2
        dist = dist.to_numpy()

        nearest_ind = np.argmin(dist)
        nearest_zip = ny.iloc[nearest_ind]["Zip"]
        nearest_borough = ny.iloc[nearest_ind]["City"]

        dist = dist[nearest_ind]

        if np.isfinite(dist):
            df.iloc[k, zip_col] = nearest_zip
            df.iloc[k, borough_col] = nearest_borough

        if not (k % 100000):
            print("Determined zipcode and borough for {:} locations.".format(k))
    print("Finished determining zipcode and borough information for all locations.")

    mask = df["borough"].isna()
    df = df[~mask]

    df["zipcode"] = df["zipcode"].astype(str)

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
