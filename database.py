# database.py
from pymongo import MongoClient
import os

MONGO_URI = "mongodb+srv://sunnykhattri9621_db_user:Sunny%40991122@cluster0.habx8fg.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client['hotel-retailer']
hotels = db['hotels']
orders = db['orders']
dealers = db['dealers']


vegetables = db['vegetable_List']

# Insert sample data if empty
if hotels.count_documents({}) == 0:
    sample_hotel = {
        "_id": "hotel_001",
        "name": "Grand Delhi Palace",
        "email": "grand@hotel.com",
        "password": "hotel123",  # Plain text for demo - hash in production
        "address": "Connaught Place, New Delhi",
        "contact": "+91-9876543210",
        "status": "active"
    }
    hotels.insert_one(sample_hotel)

# Insert sample dealer data if empty
if dealers.count_documents({}) == 0:
    sample_dealer = {
        "_id": "dealer_001",
        "name": "Main Dealer",
        "email": "dealer@shop.com",
        "password": "dealer123",  # Plain text for demo
        "contact": "+91-9876543210",
        "status": "active"
    }
    dealers.insert_one(sample_dealer)
