#Import libraires 
import pandas as pd
from datetime import datetime
from ETLfunctions import calculate_downtime, classify_criticality
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()
#Extraction 
event_dataset=pd.read_excel("C:/Users/marie/OneDrive/Desktop/ProjetMonétique/DATA.xlsx")
event_dataset.to_csv("C:/Users/marie/OneDrive/Desktop/ProjetMonétique/DATA.csv", index=False)
localisations_dataset=pd.read_csv("C:/Users/marie/OneDrive/Desktop/ProjetMonétique/tunisia_atm_locations.csv")

#Transform
#Cleaning the dataset
#extract only the necessary columns
event_dataset = event_dataset[['PID','DATETIME','EVENT_ID','DSC']]
#delete duplicated rows
if event_dataset.duplicated().sum():
    print("Found",event_dataset.duplicated().sum(),"duplicated rows" )
    event_dataset.drop_duplicates(keep='last', inplace=True)

#delete rows having null values
if event_dataset.isnull().values.any():
    print("found null values in the dataset")
    event_dataset = event_dataset.dropna(subset=['DATETIME', 'DSC', 'EVENT_ID', 'PID'])
#sort the dataset by datetime
event_dataset = event_dataset.reset_index().sort_values(by=['DATETIME', 'index']).set_index('index')
#creer status_df
status_data = []
for pid, group in event_dataset.groupby('PID'):
    status, level = classify_criticality(group)
    status_data.append({
        'PID': pid,
        'latest_status': status,
        'critical_level': level,
        'last_updated': group['DATETIME'].max()
    })
    
status_df = pd.DataFrame(status_data)
#communication downtime stats
communication_events=event_dataset[event_dataset['EVENT_ID'].isin([200000, 200001])]
comm_downtime_df = calculate_downtime(communication_events, 200000, 200001)
comm_downtime_df.rename(columns={'avg_downtime_minutes': 'avg_communication_downtime'}, inplace=True)
#service downtime stats
service_events=event_dataset[event_dataset['EVENT_ID'].isin([200003, 200002])]
service_downtime_df = calculate_downtime(service_events, 200003, 200002)
service_downtime_df.rename(columns={'avg_downtime_minutes': 'avg_service_downtime'}, inplace=True)
#merge stats dataset
atm_stats_df = pd.merge(service_downtime_df, comm_downtime_df, on='PID', how='left').fillna('unknown')
atm_stats_df['stat_last_updated'] = datetime.now()
#join datasets (location-stats-status)
#join the datasets 
atm_loc_status_df= pd.merge(localisations_dataset, status_df, on='PID', how='outer')
atm_loc_status_stat_df = pd.merge(atm_loc_status_df, atm_stats_df, on='PID', how='outer')
atm_loc_status_stat_df=atm_loc_status_stat_df[['PID']+[col for col in atm_loc_status_stat_df.columns if col != 'PID']]
atm_loc_status_stat_df.head()
#Load
#connect to postgresql
load_dotenv()
db_url = os.getenv("DATABASE_URL")
engine = create_engine(db_url)

#creer colonne pour PostGIS geo
atm_loc_status_stat_df['geom'] = atm_loc_status_stat_df.apply(lambda row: f"POINT({row['longitude']} {row['latitude']})" if pd.notnull(row['latitude']) else None, axis=1)
print(atm_loc_status_stat_df.dtypes)
for col in atm_loc_status_stat_df.select_dtypes(include=['object']).columns:
    for idx, val in enumerate(atm_loc_status_stat_df[col]):
        if isinstance(val, str):
            try:
                val.encode('utf-8')
            except UnicodeEncodeError:
                print(f"Encoding error in column {col} at index {idx}: {val}")

with engine.connect() as connection:
    print("Connected to the database successfully.")
    atm_loc_status_stat_df.columns = atm_loc_status_stat_df.columns.str.lower()

    atm_loc_status_stat_df[['pid','name','city','geom','latest_status','critical_level','last_updated','avg_service_downtime','avg_communication_downtime','stat_last_updated']].to_sql('atm_info', engine, if_exists='replace', index=False)
''' i ran this in sql
    connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
    connection.execute(text("ALTER TABLE atm_info ALTER COLUMN location TYPE geography(POINT, 4326) USING ST_GeomFromText(location)::geography;"))
    connection.execute(text("CREATE INDEX atm_info_location_idx ON atm_info USING GIST (location);"))
    connection.execute(text("CREATE INDEX atm_info_atm_id_idx ON atm_info (pid);"))
    connection.execute(text("ALTER TABLE atm_info ADD PRIMARY KEY (pid);"))
 '''