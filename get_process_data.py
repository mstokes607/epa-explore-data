import pandas as pd
import numpy as np

# Location of my data
air_quality_folder = "my folder"  

# Read in the data 
aq_data_2017 = pd.read_csv(air_quality_folder + "CA_2017_OZONE.csv")
aq_data_2016 = pd.read_csv(air_quality_folder + "CA_2016_OZONE.csv")  
aq_data_2015 = pd.read_csv(air_quality_folder + "CA_2015_OZONE.csv")
aq_data_2014 = pd.read_csv(air_quality_folder + "CA_2014_OZONE.csv")
aq_data_2013 = pd.read_csv(air_quality_folder + "CA_2013_OZONE.csv")
aq_data_2012 = pd.read_csv(air_quality_folder + "CA_2012_OZONE.csv")

'''
Function to prep the air quality data for analysis
Validated against data from ozone exceedances @ https://www.epa.gov/outdoor-air-quality-data/air-data-ozone-exceedances
'''

def clean_yearly_data(data):
    # Rename columns
    data = data.rename(columns={'Daily Max 8-hour Ozone Concentration': 'Max_8_hr_ozone'})
    # Convert date to date time
    data['Date_dt'] = pd.to_datetime(data['Date'])
    # Drop original date
    data = data.drop(['Date'],axis=1)
    # Records above max 8-hr ozone threshold (0.07 ppm)
    data['Above'] = np.where(data['Max_8_hr_ozone'] > 0.07, 1, 0)
    # Add an indicator for month
    data['Month'] = data['Date_dt'].map(lambda x: x.month)
    data['Year'] = data['Date_dt'].map(lambda x: x.year)
    # Sort the dataframe, and drop duplicates based on COUNTY and Date_dt
    # Subset to NOT double count instances where two stations report value above threshold on the same date
    subset = data.sort_values('Above', ascending=False).drop_duplicates(['COUNTY','Date_dt'])
    return subset

CA_2017 = clean_yearly_data(aq_data_2017)
CA_2016 = clean_yearly_data(aq_data_2016)
CA_2015 = clean_yearly_data(aq_data_2015)
CA_2014 = clean_yearly_data(aq_data_2014)
CA_2013 = clean_yearly_data(aq_data_2013)
CA_2012 = clean_yearly_data(aq_data_2012)

# Calculate number of days there was an ozone exceedance in given month & year: returns dframe
def calculate(data, year):
    calc = data.groupby(['COUNTY', 'STATE_CODE', 'COUNTY_CODE', 'Year'])['Above'].sum()
    calc_df = pd.DataFrame(calc)
    calc_df = calc_df.reset_index(level=['COUNTY', 'STATE_CODE', 'COUNTY_CODE','Year'])
    # create id for GEOJSON data
    calc_df['STATE_CODE'] = calc_df['STATE_CODE'].apply(lambda x: '0' + str(x) if (len(str(x)) <2) else str(x))
    calc_df['COUNTY_CODE'] = calc_df['COUNTY_CODE'].apply(lambda x: '00' + str(x) if len(str(x)) == 1 
                                                          else ('0' + str(x) if len(str(x)) == 2 else str(x)))
    calc_df['id'] = calc_df['STATE_CODE']+calc_df['COUNTY_CODE']
    calc_df = calc_df.rename(columns={'Above':'value'}) 
    # express number of days OZ above threshold as % days in year
    calc_df['value_' + year] = calc_df['value'] / 365 * 100                                                   
        
    return calc_df[['id','value_' + year]]
            
CA_2017_data = calculate(CA_2017,'2017')
CA_2016_data = calculate(CA_2016,'2016')
CA_2015_data = calculate(CA_2015,'2015')
CA_2014_data = calculate(CA_2014,'2014')
CA_2013_data = calculate(CA_2013,'2013')
CA_2012_data = calculate(CA_2012,'2012')

# combine the data frames
dfs = [CA_2017_data, CA_2016_data, CA_2015_data, CA_2014_data, CA_2013_data, CA_2012_data]
CA_oz_combine = reduce(lambda left,right: pd.merge(left,right,on='id'), dfs)

out_folder = 'my folder'
filename = 'CA_oz_combine.csv'
CA_oz_combine.to_csv(out_folder + filename, index=False)

filename = 'CA_oz_data.json'
json_prep = CA_oz_combine.set_index('id')
json_prep.to_json(out_folder + filename, orient='index')
