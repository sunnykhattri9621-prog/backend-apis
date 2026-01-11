from fastapi import APIRouter, HTTPException, Depends, Header
from models import OrderCreate, OrderResponse
from database import orders, hotels
from typing import List, Optional
from datetime import datetime
import uuid

router = APIRouter(prefix="/orders", tags=["orders"])

def verify_hotel_access(authorization: str = Header(None)):
    """Verify hotel is logged in and order is not dealer-completed"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Hotel authorization required")
    
    # Extract hotel_id from token (simplified - use JWT in production)
    hotel_id = authorization.replace("Bearer ", "")
    
    if not hotels.find_one({"_id": hotel_id, "status": "active"}):
        raise HTTPException(401, "Invalid or inactive hotel")
    
    return hotel_id

# CREATE - Hotel creates order (only if not dealer-completed)
@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, ):
    """Hotel creates order - only if hotel authorized"""
    
    
    # Check order doesn't exist with same timestamp/date
    existing = orders.find_one({
        "hotelId": order.hotelId,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": {"$gte": datetime.now().replace(hour=0, minute=0, second=0)}
    })
    
    if existing and existing["status"] == "completed":
        raise HTTPException(400, "Daily order already completed by dealer")
    
    order_doc = order.dict()
    order_doc.update({
        "id": f"order_{int(datetime.now().timestamp()*1000)}.{uuid.uuid4().hex[:10]}",
        "status": "pending",
        "dealerNote": "",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.utcnow()
    })
    
    result = orders.insert_one(order_doc)
    order_doc["_id"] = str(result.inserted_id)
    order_doc["id"] = order_doc["id"]
    
    return OrderResponse(**order_doc)

# READ - All orders for logged-in hotel (only pending/non-completed)
@router.get("/", response_model=List[OrderResponse])
async def get_hotel_orders(hotel_id: str = Depends(verify_hotel_access)):
    """Get all pending/non-completed orders for this hotel"""
    orders_data = list(orders.find({
        "hotelId": hotel_id,
        "status": {"$ne": "completed"}  # Only non-dealer-completed
    }).sort("timestamp", -1))
    
    for order in orders_data:
        order["_id"] = str(order["_id"])
        order["id"] = order["id"]
    
    return orders_data

# READ - Single order by ID
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, hotel_id: str = Depends(verify_hotel_access)):
    order = orders.find_one({"id": order_id, "hotelId": hotel_id})
    if not order:
        raise HTTPException(404, "Order not found")
    order["_id"] = str(order["_id"])
    return OrderResponse(**order)

# UPDATE - Hotel can update pending order
@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: str, order_update: OrderCreate):
    """Hotel updates pending order"""
    existing = orders.find_one({"id": order_id, "hotelId": order_update.hotelId})
    if not existing:
        raise HTTPException(404, "Order not found")
    
    if existing["status"] == "completed":
        raise HTTPException(403, "Cannot update dealer-completed order")
    
    update_data = {"$set": {
        "hotelName": order_update.hotelName,
        "items": [item.dict() for item in order_update.items],
        "date":  datetime.now().strftime("%Y-%m-%d")
    }}
    
    updated = orders.find_one_and_update(
        {"id": order_id},
        update_data,
        return_document=True
    )
    
    updated["_id"] = str(updated["_id"])
    return OrderResponse(**updated)

# DELETE - Hotel deletes pending order
@router.delete("/{order_id}")
async def delete_order(order_id: str, hotel_id: str = Depends(verify_hotel_access)):
    """Hotel deletes pending order"""
    result = orders.delete_one({"id": order_id, "hotelId": hotel_id})
    if result.deleted_count == 0:
        raise HTTPException(404, "Order not found")
    return {"message": "Order deleted"}
