"""
Python Script for analyzing CitiBike dataset and NYPD's publicly available dataset on traffic accidents for finding
opportunities for cooperation on Insurance.
"""
import os
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

from preprocessing.dataCleaning import clean_data
from preprocessing.mapVehicles import correct_vehicle_names
from preprocessing.determine_zipcode_borough_for_CitiBike import get_zipcode_borough_info
from preprocessing.determine_zipcode_borough_for_NYPDbikeAccidents import get_zipcode_borough_using_NYmapinfo

# Filepaths for Bike Accidents dataset and CitiBike dataset
# Note: NYPD publicly available dataset "Motor Vehicle Collisions - Crashes" is processed using the python script
# create_BikeAccidentData.py for selecting only the accidents that involved bikes and result is stored in a csv file.
# Note: CitiBike data for January 2023 is considered due to hardware limitation as each month contains around 2 Million
# rows. However, the code can handle more files on suitable hardware.
nyBikeAccidents_filepath = "bikeAccidentsNY.csv"
citibike_filepath = "citibike-tripdata"

print("\nStarted Processing NY Bike Accidents dataset.")
# Reading in NY Bike Accidents data into a Pandas Dataframe
bikeAccidents = pd.read_csv(nyBikeAccidents_filepath)
print("\nShape of Bike Accident data: {:}".format(bikeAccidents.shape))
print("\nPrinting the Columns in the Bike Accidents dataset: ")
print(bikeAccidents.columns)

# Some entries bikeAccidents Dataframe are missing location information. This information is filled in with the
# help of the function get_zipcode_borough_bikeAccidents from the preprocessing script zipcode_borough_determination.py
print("\nNumber of entries missing (Latitude, Longitude) for accidents: {:}".format(bikeAccidents["latitude"].isna().sum()))

# Filling in the missing Location information
bikeAccidents = get_zipcode_borough_using_NYmapinfo(bikeAccidents)

# Correct the names in the VEHICLE TYPE CODE columns
bikeAccidents = correct_vehicle_names(bikeAccidents)

# Clean the bikeAccidents Dataframe with the help of the function clean_data from the preprocessing script
# dataCleaning.py
bikeAccidents = clean_data(bikeAccidents)

# We now encode bike accidents in terms of the seriousness of Injury in the variable accident_outcome
# accident_outcome: 0 = unharmed, 1 = injured, 2 = death
# Append new column and initialize with NaNs
bikeAccidents["accident_outcome"] = np.nan
# unharmed
mask = (bikeAccidents["number of cyclist injured"] == 0)
bikeAccidents.loc[mask, "accident_outcome"] = 0
# injured
mask = bikeAccidents["number of cyclist injured"] > 0
bikeAccidents.loc[mask, "accident_outcome"] = 1
# deaths
mask = bikeAccidents["number of cyclist killed"] > 0
bikeAccidents.loc[mask, "accident_outcome"] = 2

print("\nPrinting the Column-names in the DataFrames: ")
print(bikeAccidents.columns)

print("\nPrinting the Time Interval for all Bike Accidents: ")
print(bikeAccidents["datetime"].min())
print(bikeAccidents["datetime"].max())

print("\nBreakdown Bike Accidents by Number of Cyclists UnHarmed, Injured and Deaths:")
print(bikeAccidents["accident_outcome"].value_counts().sort_index())

# Generating breakdown of accidents by District (Borough)
bikeAccidents_borough = bikeAccidents.groupby(["borough"])[["number of cyclist killed", "number of cyclist injured"]].sum().sort_index()

# Get population of the different districts (boroughs) in NY from https://www.citypopulation.de/en/usa/newyorkcity/
# Compute cyclist injuries and deaths per 100k in these districts.
# BRONX: 1356476, BROOKLYN: 2561225, MANHATTAN: 1597451, QUEENS: 2252196, STATEN ISLAND: 490687
bikeAccidents_borough["Population"] = [1356476, 2561225, 1597451, 2252196, 490687]
bikeAccidents_borough["injuries_per_100k"] = 1e5*bikeAccidents_borough["number of cyclist injured"] / bikeAccidents_borough["Population"]
bikeAccidents_borough["deaths_per_100k"] = 1e5*bikeAccidents_borough["number of cyclist killed"] / bikeAccidents_borough["Population"]
bikeAccidents_borough.round(decimals={"Population": -3, "injuries_per_100k": 0, "deaths_per_100k": 2})

print("\nCompleted Processing of NY Bike Accidents Dataset.")

print("\nStarted Processing CitiBike Dataset.")
# Our goal is to find the breakdown of Bikes rented by the Boroughs in which the bke accidents occurred.
# For this we use the starting (latitude, longitude) information to determine in which districts the bikes were rented.
files = sorted(glob.glob(os.path.join(citibike_filepath, '*.csv')))
print("\nThe CitiBike files being processed are:  {:}".format(files))
citibikeData = pd.DataFrame()
for i, file in enumerate(files):
    df = pd.read_csv(file)
    citibikeData = pd.concat([citibikeData, df])

print("\nShape of Citibike Data: {:}".format(citibikeData.shape))
print("\nThe Columns of CitiBike Data are: ")
print(citibikeData.columns)

# Augment CitiBike Data with borough and zipcode information from which the bikes were rented
# using starting station latitude (start_lat) and starting station longitude (start_lng) from the CitiBike Dataset
# For this step we use the Borough and Zipcode information of New York (NY-zip-code-latitude-and-longitude.csv)
citibikeData_Borough_Zipcode = get_zipcode_borough_info(citibikeData)

print("\nBreakdown of Bikes Rented by Districts (Boroughs): ")
citibikeRented_borough = citibikeData_Borough_Zipcode["borough"].value_counts().sort_index()
print(citibikeRented_borough)
bikeRentalCounts = citibikeRented_borough.tolist()

print("\nCompleted Processing CitiBike Dataset.")

# Concatenating Citibike rentals by borough with accident information
bikeAccidents_borough.insert(2, "CitiBikesRented", [bikeRentalCounts[0], bikeRentalCounts[1], bikeRentalCounts[2], bikeRentalCounts[3], 0])
bikeAccidents_borough["CitiBikesRented_per_100k"] = 1e5*bikeAccidents_borough["CitiBikesRented"] / bikeAccidents_borough["Population"]
bikeAccidents_borough.round(decimals={"CitiBikesRented_per_100k": 2})
print("\nBreakdown of Bike Accidents and CitiBike Rentals by Borough")
print(bikeAccidents_borough)

barWidth = 0.25
fig = plt.subplots(figsize=(12, 8))
#num_killed = 1e2*bikeAccidents_borough["number of cyclist killed"]
num_killed = 1e2*bikeAccidents_borough["deaths_per_100k"]
num_killed = num_killed.tolist()
#num_injured = bikeAccidents_borough["number of cyclist injured"].tolist()
num_injured = bikeAccidents_borough["injuries_per_100k"].tolist()
num_rentedbikes = bikeAccidents_borough["CitiBikesRented_per_100k"].tolist()

br1 = np.arange(len(num_killed))
br2 = [x + barWidth for x in br1]
br3 = [x + barWidth for x in br2]

plt.bar(br1, num_killed, color='r', width=barWidth, edgecolor='grey', label='Deaths per 100k of the population times 100')
plt.bar(br2, num_injured, color='g', width=barWidth, edgecolor='grey', label='Injuries per 100k of the population')
plt.bar(br3, num_rentedbikes, color='b', width=barWidth, edgecolor='grey', label='Bikes Rented per 100k of the population')
plt.title('Visualization of cyclists killed (per 10Mil), injured (per 100k) and CitiBikes rented (per 100k)')
plt.xlabel('Borough', fontweight='bold', fontsize=15)
plt.ylabel('Frequency', fontweight='bold', fontsize=15)
plt.xticks([r + barWidth for r in range(len(num_killed))], ["Bronx", "Brooklyn", "Manhattan", "Queens", "Staten Island"])
plt.legend()
plt.savefig('Bar-diagram visualization')
plt.show()
print("\nSaved Bar-diagram.")

