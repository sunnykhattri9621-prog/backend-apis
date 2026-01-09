# main.py - CORRECTED VERSION
from fastapi import FastAPI, HTTPException  # Import HTTPException from fastapi directly
from fastapi.middleware.cors import CORSMiddleware
from models import HotelLogin, HotelResponse
from database import hotels

app = FastAPI(title="Hotel Login API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login", response_model=HotelResponse)
async def hotel_login(credentials: HotelLogin):
    """Verify hotel login credentials"""
    hotel = hotels.find_one({"email": credentials.email, "status": "active"})
    
    if not hotel:
        raise HTTPException(status_code=401, detail="Invalid email or inactive account")
    
    # Verify password (plain text for demo - use bcrypt in production)
    if hotel["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Convert ObjectId and prepare response
    hotel["_id"] = str(hotel.get("_id", ""))
    return hotel

@app.get("/health")
async def health_check():
    return {"status": "Hotel API running", "hotels_count": hotels.count_documents({})}
