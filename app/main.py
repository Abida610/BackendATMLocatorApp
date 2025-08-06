from fastapi import FastAPI
from api.navigation import router as nav_api
from api.complaints import router as complaint_api
from api.recommendation  import router as recommendation_api
from api.atms import router as data_api
app=FastAPI(title="ATM Locator API",
    description="API for finding ATMs, managing real-time data, and user complaints.",)
app.include_router(nav_api)
app.include_router(complaint_api)
app.include_router(recommendation_api)
app.include_router(data_api)
@app.get("/")
def read_root():
    return {}



