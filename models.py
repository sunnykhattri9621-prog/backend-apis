# models.py
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from bson import ObjectId
from datetime import datetime
import uuid

class HotelLogin(BaseModel):
    email: EmailStr
    password: str

class HotelLoginResponse(BaseModel):
    _id: str
    hotelId: str
    name: str
    email: str
    address: str
    contact: str
    status: str
    
    class Config:
        from_attributes = True

class DealerLogin(BaseModel):
    email: EmailStr
    password: str

class DealerResponse(BaseModel):
    _id: str
    name: str
    email: str
    contact: str
    status: str
    
    class Config:
        from_attributes = True

class VegetableCreate(BaseModel):  # For CREATE - no veg_id needed
    name: str
    price: float

class Vegetable(VegetableCreate):   # Full model with auto-generated ID
    veg_id: str

class VegetableResponse(Vegetable):
    id: str  # MongoDB _id
    
    class Config:
        from_attributes = True

# Input model - only mandatory fields
class HotelCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    address: str
    contact: str

# Full response model
class HotelResponse(HotelCreate):
    _id: str
    status: str = "active"
    type: str = "hotel"
    entity_type: str = "hotel"
    
    class Config:
        from_attributes = True           


class OrderItem(BaseModel):
    itemName: str
    quantity: float
    unit: str = "kg"

class OrderCreate(BaseModel):
    hotelId: str
    hotelName: str
    items: List[OrderItem]

class OrderResponse(OrderCreate):
    id: str
    status: str = "pending"
    dealerNote: str = ""
    date: str
    timestamp: datetime
    
    class Config:
        from_attributes = True