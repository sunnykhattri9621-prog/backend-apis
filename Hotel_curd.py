from fastapi import APIRouter, HTTPException
from models import HotelCreate, HotelResponse
from database import hotels
from typing import List, Optional
from datetime import datetime
import uuid


router = APIRouter(prefix="/hotels", tags=["hotels"])

# CREATE - Bulk array input, auto-add static fields
@router.post("/", response_model=List[HotelResponse])
async def create_hotels(hotels_data: List[HotelCreate]):
    """Create multiple hotels - auto adds static fields"""
    created_hotels = []
    
    for hotel_data in hotels_data:
        # Check if email already exists
        if hotels.find_one({"email": hotel_data.email}):
            raise HTTPException(400, f"Hotel with email {hotel_data.email} already exists")
        
        # Prepare document with static fields
        hotel_doc = hotel_data.dict()
        hotel_doc.update({
            "hotelId": str(uuid.uuid4()),
            "status": "active",
            "type": "hotel", 
            "entity_type": "hotel",
            "createdAt": datetime.utcnow(),
            "last_checked": datetime.utcnow()
        })
        
        # Insert and get result
        result = hotels.insert_one(hotel_doc)
        created_hotel = hotels.find_one({"_id": result.inserted_id})
        created_hotel["_id"] = str(created_hotel["_id"])
        
        created_hotels.append(HotelResponse(**created_hotel))
    
    return created_hotels

# READ - Get all hotels, optional email/name filter
@router.get("/", response_model=List[HotelResponse])
async def get_hotels(email: Optional[str] = None, name: Optional[str] = None):
    """Get all hotels or filter by email/name"""
    query = {}
    if email:
        query["email"] = email
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    
    data = list(hotels.find(query))
    for hotel in data:
        hotel["_id"] = str(hotel["_id"])
    
    return data

# READ - Single hotel by _id
@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: str):
    hotel = hotels.find_one({"_id": hotel_id})
    if not hotel:
        raise HTTPException(404, f"Hotel {hotel_id} not found")
    hotel["_id"] = str(hotel["_id"])
    return HotelResponse(**hotel)

# UPDATE - Single hotel by _id (mandatory fields only)
@router.put("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(hotel_id: str, hotel_data: HotelCreate):
    """Update single hotel - preserves static fields"""
    # Check if hotel exists
    existing = hotels.find_one({"_id": hotel_id})
    if not existing:
        raise HTTPException(404, f"Hotel {hotel_id} not found")
    
    # Update only provided fields
    update_data = {"$set": {
        "name": hotel_data.name,
        "email": hotel_data.email,
        "password": hotel_data.password,
        "address": hotel_data.address,
        "contact": hotel_data.contact,
        "last_checked": datetime.utcnow()
    }}
    
    updated = hotels.find_one_and_update(
        {"_id": hotel_id},
        update_data,
        return_document=True
    )
    
    updated["_id"] = str(updated["_id"])
    return HotelResponse(**updated)

# DELETE - Single hotel by _id
@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: str):
    """Delete single hotel"""
    result = hotels.delete_one({"_id": hotel_id})
    if result.deleted_count == 0:
        raise HTTPException(404, f"Hotel {hotel_id} not found")
    return {"message": f"Hotel {hotel_id} deleted successfully"}
