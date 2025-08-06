from fastapi import  HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
from config.database import get_db
from models.atminfo import ATMInfo
from pydantic import BaseModel
from datetime import datetime
from typing import List,Optional
from sqlalchemy import text
from geoalchemy2.functions import ST_Point,ST_SetSRID
router = APIRouter()
class ATMDetails(BaseModel):
    pid: int
    name: str
    city: str
    latest_status: str
    critical_level: str
    last_updated: datetime
    avg_communication_downtime: Optional[str] = None  # Allow None
    avg_service_downtime: Optional[float] = None      # Allow None
    stat_last_updated: Optional[datetime] = None 
    longitude:float
    latitude:float
    class Config:
        from_attributes = True

class ATMUpdate(BaseModel):
    pid: int|None =None
    name: str|None =None
    city: str|None =None
    latest_status: str|None =None
    critical_level: str|None =None
    last_updated: datetime|None =None
    avg_communication_downtime: Optional[str] = None  # Allow None
    avg_service_downtime: Optional[float] = None      # Allow None
    stat_last_updated: Optional[datetime] = None 
    longitude:float
    latitude:float
    class Config:
        from_attributes = True



#GET: Retrieve all ATMs
@router.get("/atms", response_model=List[ATMDetails])
def get_all_atms(db: Session = Depends(get_db)):
    all_atms=[]
    query=text("""
            SELECT 
                ST_Y(location::geometry) AS latitude, 
                ST_X(location::geometry) AS longitude 
            FROM atm_info 
            WHERE pid = :pid
            """)
    try:
        atms = db.query(ATMInfo)
        if not atms:
            raise HTTPException(status_code=404, detail="Aucun DAB trouvé")
        for atm in atms:
            result=db.execute(query,{"pid": atm.pid}).fetchone()
            latitude = float(result.latitude) if result.latitude is not None else None
            longitude = float(result.longitude) if result.longitude is not None else None
        
            if latitude is None or longitude is None:
                raise HTTPException(status_code=500, detail="Les coordonnées sont invalides!")
            all_atms.append(ATMDetails(pid=atm.pid,name=atm.name,city=atm.city,latest_status=atm.latest_status,critical_level=atm.critical_level,last_updated=atm.last_updated,avg_communication_downtime=atm.avg_communication_downtime,avg_service_downtime=atm.avg_service_downtime,stat_last_updated=atm.stat_last_updated,latitude=latitude,longitude=longitude))
        return all_atms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur fetching DABs: {str(e)}")

# POST:Add a new ATM
@router.post("/atm")
def create_atm(atm: ATMDetails, db: Session = Depends(get_db)):
    try:
        location=ST_SetSRID(ST_Point(atm.longitude, atm.latitude), 4326)
        
        new_atm=ATMInfo(pid=atm.pid,name=atm.name,city=atm.city,latest_status=atm.latest_status,critical_level=atm.critical_level,last_updated=atm.last_updated,avg_communication_downtime=atm.avg_communication_downtime,avg_service_downtime=atm.avg_service_downtime,stat_last_updated=atm.stat_last_updated,location=location)
        
        db.add(new_atm)
        db.commit()
        db.refresh(new_atm)
        
        
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Une erreur s'est produite lors de la création de DAB: {str(e)}")

#PUT: Update an existing ATM
@router.put("/atm/{atm_id}", response_model=ATMUpdate)
def update_atm(atm_id: int, atm: ATMUpdate, db: Session = Depends(get_db)):
    try:
        #Check if ATM exists
        existing_atm = db.query(ATMInfo).filter(ATMInfo.pid == atm_id).first()
        if not existing_atm:
            raise HTTPException(status_code=404, detail="DAB introuvable")
        location = ST_SetSRID(ST_Point(atm.longitude, atm.latitude), 4326)
        existing_atm.name = atm.name
        existing_atm.city = atm.city
        existing_atm.latest_status = atm.latest_status
        existing_atm.critical_level = atm.critical_level
        existing_atm.last_updated = atm.last_updated
        existing_atm.avg_communication_downtime = atm.avg_communication_downtime
        existing_atm.avg_service_downtime = atm.avg_service_downtime
        existing_atm.stat_last_updated = atm.stat_last_updated
        existing_atm.location = location

        db.commit()
        db.refresh(existing_atm)

        return atm
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Une erreur s'est produite lors de la mise à jour de DAB: {str(e)}")
        

#DELETE: Delete an ATM
@router.delete("/atms/{atm_id}")
def delete_atm(atm_id: int, db: Session = Depends(get_db)):
    try:
        #check if ATM exists
        atm = db.query(ATMInfo).filter(ATMInfo.pid == atm_id).first()
        if not atm:
            raise HTTPException(status_code=404, detail="DAB introuvable")
        
        #Delete ATM
        query = text("DELETE FROM atm_info WHERE pid = :pid")
        db.execute(query, {"pid": atm_id})
        db.commit()
        return {"message": f"ATM {atm_id} supprimé de la base de données"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur à la suppresion de  DAB: {str(e)}")