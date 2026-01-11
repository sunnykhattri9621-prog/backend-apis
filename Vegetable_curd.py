from fastapi import APIRouter, HTTPException
from models import VegetableCreate, VegetableResponse
from database import vegetables
from typing import List, Optional
import uuid

router = APIRouter(prefix="/vegetables", tags=["vegetables"])

# CREATE - Array input, AUTO UUID generation
@router.post("/", response_model=List[VegetableResponse])
async def create_vegetables(veggies: List[VegetableCreate]):
    """Add multiple vegetables - veg_id generated automatically"""
    created_docs = []
    
    for veg in veggies:
        veg_id = str(uuid.uuid4())  # Generate UUID
        doc = veg.dict()
        doc["veg_id"] = veg_id
        
        result = vegetables.insert_one(doc)
        created_doc = vegetables.find_one({"_id": result.inserted_id})
        created_doc["_id"] = str(created_doc["_id"])
        created_doc["id"] = created_doc["_id"]
        created_docs.append(VegetableResponse(**created_doc))
    
    return created_docs

# READ - Get all OR filter by name
@router.get("/", response_model=List[VegetableResponse])
async def get_vegetables(name: Optional[str] = None):
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    
    data = list(vegetables.find(query))
    for veg in data:
        veg["_id"] = str(veg["_id"])
        veg["id"] = veg["_id"]
    return data

# UPDATE - Single vegetable by veg_id
@router.put("/{veg_id}", response_model=VegetableResponse)
async def update_vegetable(veg_id: str, veg: VegetableCreate):
    """Update single vegetable - preserve existing veg_id"""
    veg_dict = veg.dict()
    veg_dict["veg_id"] = veg_id  # Keep original UUID
    
    updated = vegetables.find_one_and_update(
        {"veg_id": veg_id},
        {"$set": veg_dict},
        return_document=True
    )
    
    if not updated:
        raise HTTPException(404, f"Vegetable {veg_id} not found")
    
    updated["_id"] = str(updated["_id"])
    updated["id"] = updated["_id"]
    return VegetableRequest(**updated)

# DELETE - Single vegetable by veg_id
@router.delete("/{veg_id}")
async def delete_vegetable(veg_id: str):
    result = vegetables.delete_one({"veg_id": veg_id})
    if result.deleted_count == 0:
        raise HTTPException(404, f"Vegetable {veg_id} not found")
    return {"message": f"Vegetable {veg_id} deleted"}

# Get vegetable by UUID
@router.get("/{veg_id}", response_model=VegetableResponse)
async def get_single_vegetable(veg_id: str):
    veg = vegetables.find_one({"veg_id": veg_id})
    if not veg:
        raise HTTPException(404, f"Vegetable {veg_id} not found")
    veg["_id"] = str(veg["_id"])
    veg["id"] = veg["_id"]
    return VegetableResponse(**veg)
