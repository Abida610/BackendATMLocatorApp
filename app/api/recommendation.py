from fastapi import Depends, HTTPException,Query, APIRouter
from sqlalchemy.orm import Session
from config.database import get_db
from services.recommendation_service import get_recommended_atms,ATMRecommendation
from services.navigation_service import Coordinates

from typing import List
router=APIRouter()

@router.get("/recommandation", response_model=List[ATMRecommendation])
async def recommend_atms(latitude:float,longitude:float,radius:float=5000,limit:int=15,db:Session=Depends(get_db)):
    user_location = Coordinates(latitude=latitude, longitude=longitude)
    try:
        atms = get_recommended_atms(db, user_location, radius, limit)
        
        return atms
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")