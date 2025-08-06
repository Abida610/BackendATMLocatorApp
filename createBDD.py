from sqlalchemy import create_engine, text
import pandas as pd
engine = create_engine("postgresql://postgres:maryem222@localhost:5432/atm_events")
event_dataset2 = pd.read_csv("C:/Users/marie/OneDrive/Desktop/ProjetMonétique/DATA.csv")
event_dataset2.to_csv("C:/Users/marie/OneDrive/Desktop/ProjetMonétique/DATABASE.csv", index=False)
event_dataset2 = event_dataset2[['PID', 'DATETIME', 'EVENT_ID', 'DSC']]
if event_dataset2.duplicated().sum():
    print("Found",event_dataset2.duplicated().sum(),"duplicated rows" )
    event_dataset2.drop_duplicates(keep='last', inplace=True)
event_dataset2 = event_dataset2.reset_index().sort_values(by=['DATETIME', 'index']).set_index('index')
for col in event_dataset2.select_dtypes(include=['object']).columns:
    for idx, val in enumerate(event_dataset2[col]):
        if isinstance(val, str):
            try:
                val.encode('utf-8')
            except UnicodeEncodeError:
                print(f"Encoding error in column {col} at index {idx}: {val}")
with engine.connect() as connection:
        event_dataset2.columns = event_dataset2.columns.str.lower()
        event_dataset2[['datetime','pid','dsc','event_id']].to_sql('atm_events', engine, if_exists='replace', index=False)
