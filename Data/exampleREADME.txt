Here are the csv files containing all ACEP Fuel Meter data collected during the 2019 season.

Created by Doug Keller on July 3rd 2019

Creation Process:

ftp-data => puma_unified_data.nc => puma_product_data.nc => FBK###_final.csv

First, the data was collated from the fuel meter data in the ftp-data directory (the fuel meters send their data to this directory) to a single unified netcdf file (puma_unified_data.nc) using the puma2unified.py script.
Then, (second step) the puma_product_data.nc netcdf file was extracted from the unified netcdf file (puma_unified_data.nc) using the uni_nc2prod_nc.py script.
Lastly, the product netcdf file (puma_product_data.nc) data was copied and restructured into a csv file per fuel meter stove combo (FBK###_final.csv) using the prod_nc2csv.py script.

Metadata:

Each csv file contains the metadata for the stove and the data columns in the first two rows, such as the stove name and location (in degrees), and the data units and descriptions.
Each file contains the time of the measurement, burning state of the stove, cumulative clicks counted by the fuel meter, clicks per interval, US gallons per interval, US gallons per hour per interval, indoor temperature measured by the fuel meter, difference in indoor and outdoor temperature, and the outdoor temperature provided by the SnoTel data collected by the Alaska Ocean Observing System (https://portal.aoos.org/#map).
The files should be easy to open in Microsoft Excel and contain the data in the correct columns.

Notes:

The first data line registering clicks in each file will be 0 as it is the beginning of the reference click count to determine the clicks per interval.
-1 is placed when the stove is off during the time interval.
Different stoves have different time measurement intervals, depending on the model of the fuel meter used (just beware when doing large data analysis scripts).
There may be operational gaps in the data due to adjustments made to the fuel meters.
