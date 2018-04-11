# epa-explore-data
Exploring outdoor air quality data from the US EPA
# requirements
Requires python 2.7 with:
1. numpy
2. pandas
3. d3js v4
# functionality
**get_process_data.py**

Reads in raw daily ozone data. Current script uses data from California during 2012-2017. Other raw daily data sets for ozone and other pollutants may be found here: https://www.epa.gov/outdoor-air-quality-data/download-daily-data. Script returns a processed data file calculating the number of days during each year (2012-2017) there was an ozone exceedance (max 8 hr ozone > 0.070 ppm) for each county in California (CA_oz_data.json).

**CA_choro.html**

Creates an interactive choropeth map for a visual display of the ozone data. HTML file takes the CA_oz_data.json file as input.      
