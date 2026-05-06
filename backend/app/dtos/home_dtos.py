# app/dtos/home_dtos.py

from app.dtos.base.base_data import BaseRecordData

class HomeStatsOut(BaseRecordData):
    total_professionals: int = 0
    total_cases: int = 0