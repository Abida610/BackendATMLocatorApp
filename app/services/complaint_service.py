from sqlalchemy.orm import Session
from models.complaint import Complaint
from models.atminfo import ATMInfo
from fastapi import HTTPException
from typing import List,Optional
from pydantic import BaseModel,EmailStr
from datetime import datetime 

from config.convert_to_pydantic import to_pydantic
class ComplaintResponse(BaseModel):
    complaint_id: int
    email: EmailStr
    description: str
    pid: int
    created_at:Optional[datetime]=None
    class Config:
        from_attributes = True
def add_complaint(atm_id:int,db:Session,email:EmailStr,description:str):
    try:
        
        atm = db.query(ATMInfo).filter(ATMInfo.pid == atm_id).first()
        
        if not atm:
            raise HTTPException(status_code=404, detail="ATM introuvable")

        
        db_complaint = Complaint(email=email,pid=atm_id,
            description=description)
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        return db_complaint
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Une erreur s'est produite lors de la création de réclamation: {str(e)}")

def get_complaints(db: Session, atm_id: int | None = None, limit: int = 100) -> List[Complaint]:
 
    try:
        
        complaints= db.query(Complaint).limit(100)  
            
        if atm_id is not None:
            query = query.filter(Complaint.pid == atm_id)
        
        if atm_id is not None and not complaints:
            raise HTTPException(status_code=404, detail="Aucune réclamation liée à ce DAB")
        list=[to_pydantic(complaint,ComplaintResponse) for complaint in complaints]
        return list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching complaints: {str(e)}")