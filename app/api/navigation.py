from fastapi import APIRouter, HTTPException, Depends 
from pydantic import BaseModel
from services.navigation_service import navigate_to_atm,  Coordinates

from sqlalchemy.orm import Session
from config.database import get_db
#pydantic model for navigation request
class NavigationRequest(BaseModel):
    user_location: Coordinates
    atm_id: int

#pydantic model for navigation response
class NavigationResponse(BaseModel):
    route: dict
    atm_status: str
router=APIRouter()
#the endpoint
@router.get("/navigation", response_model=NavigationResponse)
async def navigation_endpoint(latitude:float,longitude:float,atm_id:int,db:Session=Depends(get_db)):
    user_location = Coordinates(latitude=latitude, longitude=longitude)
    try:
        result = navigate_to_atm(user_location, atm_id,db)
        return NavigationResponse(**result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
