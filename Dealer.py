from fastapi import APIRouter, HTTPException
from database import orders, dealers
from models import DealerLogin, DealerResponse
from typing import List
from collections import defaultdict
from datetime import datetime


router = APIRouter(prefix="/dealer", tags=["Dealers"])


# DEALER LOGIN
@router.post("/login", response_model=DealerResponse)
async def dealer_login(credentials: DealerLogin):
    """Verify dealer login credentials"""
    dealer = dealers.find_one({"email": credentials.email, "status": "active"})
    
    if not dealer:
        raise HTTPException(status_code=401, detail="Invalid email or inactive account")
    
    if dealer["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid password")
        
    dealer["_id"] = str(dealer["_id"])
    return dealer

# DEALER ENDPOINT - Get aggregated pending orders
@router.get("/dealer/dashboard", response_model=dict)
async def get_dealer_dashboard(date: str = None):
    """
    Club all PENDING orders by HOTEL + ITEM and sum quantities
    Returns: {hotelName: {itemName: total_quantity}}
    """
    
    # Filter pipeline - only pending orders for today (or specific date)
    match_stage = {
        "status": "pending",
        "date": date or datetime.now().strftime("%Y-%m-%d")
    }
    
    # MongoDB Aggregation Pipeline
    pipeline = [
        {"$match": match_stage},
        {"$unwind": "$items"},  # Break items array into separate docs
        {
            "$group": {
                "_id": {
                    "hotelId": "$hotelId",
                    "hotelName": "$hotelName", 
                    "itemName": "$items.itemName"
                },
                "totalQuantity": {"$sum": "$items.quantity"},
                "unit": {"$first": "$items.unit"},
                "hotels": {"$addToSet": "$hotelName"},
                "count": {"$sum": 1}
            }
        },
        {
            "$group": {
                "_id": "$_id.hotelName",
                "items": {
                    "$push": {
                        "itemName": "$_id.itemName",
                        "totalQuantity": "$totalQuantity",
                        "unit": "$unit",
                        "hotelId": "$_id.hotelId"
                    }
                },
                "totalHotels": {"$addToSet": "$_id.hotelId"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    results = list(orders.aggregate(pipeline))
    
    # Format response for easy reading
    dashboard = {}
    for hotel_data in results:
        hotel_name = hotel_data["_id"]
        dashboard[hotel_name] = {
            "totalHotels": len(hotel_data["totalHotels"]),
            "items": hotel_data["items"]
        }
    
    # Summary by item across ALL hotels
    item_summary = defaultdict(float)
    for hotel_data in dashboard.values():
        for item in hotel_data["items"]:
            item_summary[item["itemName"]] += item["totalQuantity"]
    
    return {
        "date": date or datetime.now().strftime("%Y-%m-%d"),
        "summary": {
            "totalHotels": len(dashboard),
            "totalPendingItems": sum(item_summary.values()),
            "byItem": dict(item_summary)
        },
        "byHotel": dashboard
    }
