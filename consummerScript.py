from kafka import KafkaConsumer
import json
import psycopg2
from ETLfunctions import classify_criticality
import pandas as pd
from dotenv import load_dotenv
import os


load_dotenv()
topic = 'atmevents.public.atm_events'
db_config = os.getenv("db_config")

def update_backend(pid,status, criticality,last_updated):
    """Met à jour la base de données backend avec l'événement et sa criticité."""
    try:
        pid=int(pid)
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE public.atm_info SET latest_status = %s, critical_level = %s, last_updated= %s WHERE pid = %s",
            (status, criticality, last_updated, pid)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la base de données : {e}")

def main():
    print(f"Consuming topic {topic}")
    
    consumer = KafkaConsumer(
        topic,
        bootstrap_servers='localhost:29092',
        group_id='kafka_group',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    try:
    #events_accumulated = pd.DataFrame(columns=['pid', 'datetime', 'event_id', 'dsc'])
        for message in consumer:
            try:
                data = message.value
                print(data)
                #vérifier si c'est un événement de création
                if data.get('op') in ['c']:  #c=create
                    event = data.get('after')

                    if event:
                        
                        event_data = {
                            'PID': [event.get('pid')],
                            'DATETIME': [event.get('datetime')],
                            'EVENT_ID': [event.get('event_id')],
                            'DSC': [event.get('dsc')]
                        }
                        '''events_accumulated = pd.concat([events_accumulated, pd.DataFrame([event_data])], ignore_index=True)
                        grouped = events_accumulated.groupby('pid')
                        for pid_key, group_df in grouped:
                            status, criticality = classify_criticality(group_df)
                            print(f"Criticality calculated for PID {pid_key}: status={status}, criticality={criticality}")
                            update_backend(pid_key, status, criticality)
        '''             
                        if all(event_data.values()):
                            df_event = pd.DataFrame(event_data)
                            df_event['DATETIME'] = pd.to_datetime(df_event['DATETIME'])

                            status, criticality = classify_criticality(df_event)
                            update_backend(df_event['PID'][0], status, criticality, df_event['DATETIME'][0])
                    else:
                        print("données manquantes.")
            except Exception as e:
                print(f"Erreur lors du traitement du message : {e}")
    except KeyboardInterrupt:
        print("Arrêt du consommateur.")
    finally:
        consumer.close()

if __name__ == "__main__":
    main()
