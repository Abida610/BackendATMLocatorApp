from sqlalchemy import Column,  String, BigInteger,DateTime, Float, Enum
from geoalchemy2 import Geometry,Geography
from config.database import Base
class ATMInfo (Base):
    __tablename__='atm_info'
    pid=Column(BigInteger,primary_key=True)
    name = Column(String)                     
    city = Column(String)                      
    location=Column(Geography('POINT',srid=4326))
    latest_status = Column(String)
    critical_level=Column(Enum('low','warning','critical',name='critical_level_enum'))
    last_updated = Column(DateTime)            
    avg_service_downtime = Column(Float) 
    avg_communication_downtime = Column(String)
    stat_last_updated = Column(DateTime) 
