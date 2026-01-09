# database.py
from pymongo import MongoClient
import os

MONGO_URI = "mongodb+srv://sunnykhattri9621_db_user:Sunny%40991122@cluster0.habx8fg.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client['hotel-retailer']
hotels = db['hotels']

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
