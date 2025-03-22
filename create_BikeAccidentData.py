def collect_bike_accidents_nypd(token=None, query=None, output_file=None):

    """
    Collect all instances of accidents involving bikes from the NYPD public
    dataset available at the site:
    https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95/about_data

    Note: Create a user specific token by registering at the following site:
    https://data.cityofnewyork.us/signup
    and use the token with Socrata for downloading the dataset without throttling.
    """
    import os
    import pandas as pd
    from sodapy import Socrata

    # Configure Socrata client
    client = Socrata("data.cityofnewyork.us", token)

    # Set up SoSQL query for collecting all instances involving bike accidents.
    if query is None:
        print("Collecting all instances of bike accidents using default query.")
        query = """
                select *
                where
                VEHICLE_TYPE_CODE1 = 'Bike' OR VEHICLE_TYPE_CODE1 = 'BICYCLE'
                OR
                VEHICLE_TYPE_CODE2 = 'Bike' OR VEHICLE_TYPE_CODE2 = 'BICYCLE'
                OR
                VEHICLE_TYPE_CODE_3 = 'Bike' OR VEHICLE_TYPE_CODE_3 = 'BICYCLE'
                OR
                VEHICLE_TYPE_CODE_4 = 'Bike' OR VEHICLE_TYPE_CODE_4 = 'BICYCLE'
                OR
                VEHICLE_TYPE_CODE_5 = 'Bike' OR VEHICLE_TYPE_CODE_5 = 'BICYCLE'
                OR
                NUMBER_OF_CYCLIST_INJURED > 0 OR NUMBER_OF_CYCLIST_KILLED > 0
                limit 5000000
                """

    results = client.get("h9gi-nx95", query=query)

    # Converting results, a list of dictionaries, where each dictionary is an accident into a pandas dataframe.
    df = pd.DataFrame.from_records(results)
    print("\nCollected {:} bike accidents from NYPD public dataset.".format(df.shape[0]))

    # Correcting few column names
    df.rename(columns={"vehicle_type_code1": "vehicle_type_code_1",
                       "vehicle_type_code2": "vehicle_type_code_2"}, inplace=True)

    # Regularizing column names by removing underscores.
    df.columns = df.columns.str.replace('_', ' ')

    if output_file is not None:
        df.to_csv(path_or_buf=output_file, index=False)
        print("\nOutput file {:} written.".format(output_file))

    return df


if __name__ == "__main__":

    import argparse

    my_parser = argparse.ArgumentParser(description="Collecting all instances of bike accidents from public NPYD data")

    my_parser.add_argument("--token", type=str, help="Your token for downloading data")
    my_parser.add_argument("--output", type=str, help="Output filename for storing data")
    my_parser.add_argument("--query", type=str, help="SoSQL query string")

    args = my_parser.parse_args()

    input_token = args.token
    input_query = args.query
    output_filename = args.output

    collect_bike_accidents_nypd(token=input_token, query=input_query, output_file=output_filename)

