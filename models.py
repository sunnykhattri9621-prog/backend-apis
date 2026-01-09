# models.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class HotelLogin(BaseModel):
    email: EmailStr
    password: str

class HotelResponse(BaseModel):
    _id: str
    name: str
    email: str
    address: str
    contact: str
    status: str
    
    class Config:
        from_attributes = True
