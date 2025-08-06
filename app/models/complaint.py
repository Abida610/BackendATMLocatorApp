from sqlalchemy import Column, Integer, String,ForeignKey,DateTime,  Sequence
from sqlalchemy.sql import func
from config.database import Base
class Complaint(Base):
    __tablename__ = "complaints"
    complaint_id = Column(Integer, Sequence('complaints_complaint_id_seq'), primary_key=True)
    email=Column(String(255),nullable=False)
    description = Column(String,nullable=False)
    pid = Column(Integer, ForeignKey("atm_info.pid"))
    created_at = Column(DateTime,default=func.now(),nullable=False)

