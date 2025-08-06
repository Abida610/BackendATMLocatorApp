ATM Backend (FastAPI)
## Overview
This project is a FastAPI-based backend for an ATM management and navigation application. It integrates with a PostgreSQL database, processes ATM event data via an ETL pipeline, and uses a Kafka/Debezium CDC pipeline to capture real-time changes from a source database (atm_events). The backend provides services for ATM CRUD operations, navigation to ATMs, ATM recommendations based on user location, and a complaint submission system.
## Project Structure

-  Database:
**atm_events**: Source database populated from an Excel file (via createDBB script).
**atm_app**: Backend database with the atm_info table storing ATM details (location as PostGIS geography, status, criticality, etc.) and the complaints table.


- ETL Pipeline:
Extracts data from an Excel file and loads it into the atm_app.atm_info table.
Configures PostGIS for geospatial data, creates indexes, and sets a primary key on pid.


- Kafka/Debezium CDC Pipeline:
Captures changes from atm_events using Debezium, leveraging PostgreSQL's Write-Ahead Log (WAL).
Publishes events to a Kafka topic (atmevents.public.atm_events).
A consumer script processes events, calculates criticality using classify_criticality, and updates atm_app.atm_info.


- Services:
**CRUD**: Manage ATM records (create, read, update, delete) in atm_app.atm_info.
**GET**: get all complaints related to an ATM.
**Navigation**: Provides directions from the user’s location to a selected ATM using geospatial data.
**Recommendation**: Recommends nearby ATMs based on the user’s location.
**Complaint**: Allows users to submit complaints about ATMs (e.g., reported as functional in the app but not in reality).




## Setup Instructions

Clone the Repository:
git clone <repository-url>
Set Up Environment Variables:

--> Create a .env file in the root directory.
--> Add :
**database configuration**:db_config={"dbname": "atm_app", "user": "<user>", "password": "<password>", "host": "localhost", "port": "5432"},
**AZURE_SUBSCRIPTION_KEY**=""
**DATABASE_URL**="postgresql://user:password@host:port/yourdb_name"
**DATABASE_USER**=debezium
**DATABASE_PASSWORD**=password

## Database Setup:

- Create the atm_events database from the Excel file using the createBDD script.
- Create the atm_app database and run the ETL pipeline to populate atm_info:python initialETL.py
- Execute the following SQL in atm_app:
CREATE EXTENSION IF NOT EXISTS postgis;
ALTER TABLE atm_info ALTER COLUMN location TYPE geography(POINT, 4326) USING ST_GeomFromText(location)::geography;
CREATE INDEX atm_info_location_idx ON atm_info USING GIST (location);
CREATE INDEX atm_info_atm_id_idx ON atm_info (pid);
ALTER TABLE atm_info ADD PRIMARY KEY (pid);


## Configure Kafka/Debezium CDC:

-  Configure PostgreSQL for logical replication:
Enable logical replication in postgresql.conf:wal_level = logical
- Create a replication user and grant table access:CREATE USER debezium WITH REPLICATION PASSWORD '<password>';
- GRANT SELECT ON ALL TABLES IN SCHEMA public TO debezium;
- Create a replication slot:SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput');
- Create a publication:CREATE PUBLICATION debezium_publication FOR TABLE public.atm_events;
- Start Kafka,Zookeeper and Debezium using Docker:docker-compose up -d 

- Configure the Debezium connector:

Register the connector:curl -X POST -H "Content-Type: application/json" --data @debezium-connector.json http://localhost:8083/connectors


## Run the Consumer Script:

Start the Kafka consumer to process events and update atm_app.atm_info:python consumerScript.py

## Run the FastAPI Application:
uvicorn app.main:app


## API Endpoints

CRUD Operations:
GET /atms: List all ATMs.
POST /atms: Create a new ATM record.
PUT /atms/{pid}: Update an ATM record.
DELETE /atms/{pid}: Delete an ATM record.


Navigation:
GET /navigate?user_lat={lat}&user_lon={lon}&atm_pid={pid}: Get directions to an ATM from the user’s location.


Recommendation:
GET /recommandation?user_lat={lat}&user_lon={lon}: Get a list of nearby ATMs based on the user’s location.


Complaint:
POST /complaints: Submit a complaint about an ATM (e.g., reported functional but not working).
GET /complaints/id : get the complaints related to an ATM

- Access the API at http://localhost:8000 or use the Swagger UI at http://localhost:8000/docs.
