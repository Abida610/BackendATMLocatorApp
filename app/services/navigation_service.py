import requests
from pydantic import BaseModel
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from models.atminfo import ATMInfo
from dotenv import load_dotenv
import os

load_dotenv()


AZURE_API_KEY =os.getenv("AZURE_SUBSCRIPTION_KEY")


class Coordinates(BaseModel):
    latitude: float
    longitude: float


#Fetch ATM details from database
def get_atm_info(atm_id: int,db:Session) :
   
    try:
        query=text("""
        SELECT 
            ST_Y(location::geometry) AS latitude, 
            ST_X(location::geometry) AS longitude 
        FROM atm_info 
        WHERE pid = :pid
    """)
        result = db.execute(query, {"pid": atm_id}).fetchone()
        atm = db.query(
            ATMInfo
            
        ).filter(ATMInfo.pid == atm_id).first()
        
        
        if not atm:
            raise HTTPException(status_code=404, detail="Le DAB est inexistant")
        latitude = float(result.latitude) if result.latitude is not None else None
        longitude = float(result.longitude) if result.longitude is not None else None
        
        if latitude is None or longitude is None:
            raise HTTPException(status_code=500, detail="Les coordonnées sont invalides!")
        return {"status":atm.latest_status,"latitude": latitude, "longitude": longitude}
        
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"Erreur fetching les informations de DAB: {str(e)}")


def get_directions(origin: Coordinates, destination: Coordinates):
    query = f"{origin.latitude},{origin.longitude}:{destination.latitude},{destination.longitude}"
    url = "https://atlas.microsoft.com/route/directions/json"
    params = {
        "api-version":"1.0",
        "query":query,
        "travelMode": "car"
        
    }
    headers = {
        "Subscription-Key": AZURE_API_KEY  
    }
    response = requests.get(url, params=params,headers=headers)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch directions")
    return response.json()


def navigate_to_atm(user_location: Coordinates, atm_id: int,db:Session):

    atm_info = get_atm_info(atm_id,db)
    
    destination= Coordinates(latitude=atm_info["latitude"], longitude=atm_info["longitude"])
    print(destination)
    directions = get_directions(user_location, destination)
    return {
        "route": directions,
        "atm_status": atm_info["status"]
    }
