from sqlalchemy.orm import Session
from geoalchemy2.functions import ST_DWithin, ST_SetSRID, ST_Point, ST_Distance
from models.atminfo import ATMInfo
from services.navigation_service import Coordinates
from fastapi import HTTPException
from typing import List
from pydantic import BaseModel

from datetime import datetime
from sqlalchemy.sql import func
class ATMRecommendation(BaseModel):
    pid: int
    name: str
    city: str
    latest_status: str
    critical_level: str
    last_updated: datetime
    distance: float
    class Config:
        from_attributes = True

def get_recommended_atms(db:Session,user_location: Coordinates,radius: float=5000, limit: int = 15) ->List[ATMRecommendation]:
    critical_level_weights = {
        "low": 1.0,      
        "warning": 0.5   
    }
    try:
        user_point=ST_SetSRID(ST_Point(user_location.longitude, user_location.latitude), 4326)
        
        atms  = (
            db.query(ATMInfo, ST_Distance(ATMInfo.location, user_point).label("distance"))
            .filter(
                
                ATMInfo.critical_level.in_(["low", "warning"]),
                ST_DWithin(ATMInfo.location, user_point, radius)
            )
            
            .limit(limit)
            .all()
        )
        
       
        
        if not atms:
                raise HTTPException(status_code=404, detail="Aucun DAB trouvé dans la zone spécifiée")

        scored_atms=[]
        for atm,distance  in atms:
            
            distance_km=distance/1000
            score = critical_level_weights.get(atm.critical_level, 0.5) /( distance + 1)
            atm_dict = ATMRecommendation(
                pid=atm.pid,name=atm.name,city=atm.city,latest_status=atm.latest_status,critical_level=atm.critical_level,last_updated=atm.last_updated,
                distance=round(distance_km,4)
            )
            scored_atms.append(
            {
                "atm":atm_dict,"score":score
            
            })
        scored_atms = sorted(scored_atms, key=lambda x: x["score"], reverse=True)
        recommended_atms = [item["atm"] for item in scored_atms]     
        return recommended_atms

    except Exception as e:
        raise HTTPException (status_code=500, detail=f"Erreur fetching recommendations: {str(e)}")
