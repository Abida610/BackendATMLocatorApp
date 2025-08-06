import pandas as pd
#fonction pour classifier les descriptions des événements
def classify_criticality(group):
    group['DATETIME'] = pd.to_datetime(group['DATETIME'])
    latest_event=group.iloc[-1]
    event_id = latest_event['EVENT_ID']
    latest_event_time = latest_event['DATETIME']
    time_window=latest_event_time - pd.Timedelta(minutes=1)
    recent_events = group[group['DATETIME'] >= time_window]
    recent_events_ids=recent_events['EVENT_ID'].tolist()
    if event_id in [ 200101,200710,200714,200724]: #dispenser failure ,ATM card reader down, ATM card reader jam,ATM card capture failure
        return ('DAB en panne','critical')
    elif event_id==200000:
        return ('Probleme de réseau','critical')
    elif event_id==200003:
        return ('DAB hors service','critical')

    elif event_id in [200423,200064]:
        return ('Distribution bloquée','warning')
    #probleme de cassette vide
    elif event_id  == 200113:
        if (200143 in recent_events_ids or 200140 in recent_events_ids) and (200150 in recent_events_ids or 200153 in recent_events_ids) and (200163 in recent_events_ids or 200160 in recent_events_ids) and (200170 in recent_events_ids or 200173 in recent_events_ids):
            return ("DAB à court d'argent",'critical')
        if (200143 in recent_events_ids or 200140 in recent_events_ids) :
            return ("DAB à court de billets de 10 dinars",'warning')
        if (200150 in recent_events_ids or 200153 in recent_events_ids):
            return ("DAB à court de billets de 20 dinars",'warning')
        if (200163 in recent_events_ids or 200160 in recent_events_ids):
            return ("DAB à court de billets de 50 dinars",'warning')
        if (200170 in recent_events_ids or 200173 in recent_events_ids):
            return ("DAB à court de billets de 20 dinars",'warning')
        if sum(1 for e in recent_events_ids if e in [200142,200152,200162]) >= 2:
            return ("DAB bientot à court de billets",'warning')
        if ('200722' in recent_events_ids or 200718 in recent_events_ids) :
            return ("Problème relié à la carte de l'utilisateur",'low')
    elif event_id in [200233,200230,200232]:
        return ('Imprimante hors service','low')
    else:
        return ('DAB disponible','low')
#calculer le downtime
def calculate_downtime(group,failure_id, success_id ):
    all_downtimes = []
    for pid in group['PID'].unique():
        atm_group = group[group['PID'] == pid]
    
        i = 0
        while i < len(atm_group):
            row = atm_group.iloc[i]

            if row['EVENT_ID'] == failure_id:  
                failed_time = row['DATETIME']
                
                # Chercher le prochain succès
                j = i + 1
                while j < len(atm_group):
                    next_row =atm_group.iloc[j]
                    if next_row['EVENT_ID'] == success_id:  # succès de communication
                        success_time = next_row['DATETIME']
                        downtime_minutes = (success_time - failed_time).total_seconds() / 60  # minutes
                        all_downtimes.append({
                            'PID': pid,
                            'downtime_minutes': downtime_minutes
                        })
                        i = j  
                        break
                    j += 1
            i += 1
    if all_downtimes:
                downtime_df = pd.DataFrame(all_downtimes)
                result_df=downtime_df.groupby('PID', as_index=False)['downtime_minutes']. mean()
                result_df.columns = ['PID', 'avg_downtime_minutes']
                return result_df
    else:
        return pd.DataFrame(columns=['PID', 'avg_downtime_minutes'])
