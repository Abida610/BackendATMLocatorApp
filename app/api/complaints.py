from fastapi import  HTTPException, Depends,APIRouter
from sqlalchemy.orm import Session
from typing import List
from services.complaint_service import add_complaint, get_complaints
from config.database import get_db
from pydantic import BaseModel,EmailStr
from  services.complaint_service import ComplaintResponse
router = APIRouter()
class ComplaintCreate(BaseModel):
    
    email: EmailStr
    description: str
    pid: int
    class Config:
        from_attributes = True

@router.post("/complaints")
async def create_complaint_endpoint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    try:
        new_complaint=add_complaint(complaint.pid,db,complaint.email,complaint.description )
        
        return {"message": "Merci pour votre réclamation. Elle est bien enregistrée"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get complaints endpoint
@router.get("/complaints", response_model=List[ComplaintResponse])
async def get_complaints_endpoint(atm_id: int | None = None, limit: int = 100, db: Session = Depends(get_db)):
    try:
        return get_complaints(db, atm_id, limit)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))