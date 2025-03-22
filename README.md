# CitiBike-dataset-and-NYPD-Traffic-Accident-dataset-Analysis
## Instructions for running the code are as follows:
1. Create a python virtual env, install pandas, numpy, matplotlib, sodapy, glob inside it.
2. Create an api token by registering at the site https://data.cityofnewyork.us/signup
3. Activate the virtual env and run:
 python create_BikeAccidentData.py --token Your_Token --output Your_OuputFilename 
This will create the bike accident data.
4. Download and place CitiBike trip datasets and place .csv files, inside the folder citibike-tripdata. For reproducing the results, unzip 202301-citibike-tripdata.zip and place the contents (i.e., 202301-citibike-tripdata_1.csv and 202301-citibike-tripdata_2.csv) inside the folder mentioned.
5. Run python analyze_CitiBike_and_NYPDbikeAccidents_data.py 
