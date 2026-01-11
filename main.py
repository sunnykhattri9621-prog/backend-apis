# main.py - CORRECTED VERSION
from fastapi import FastAPI, HTTPException  # Import HTTPException from fastapi directly
from fastapi.middleware.cors import CORSMiddleware
from models import HotelLogin, HotelLoginResponse
from database import hotels
from datetime import datetime
from Vegetable_curd import router as vegetable_Curd_router
from hotelOrder import router as orders_router
from Hotel_curd import router as hotel_curd_router
from Dealer import router as dealer_router



app = FastAPI(title="Hotel Login API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers in the main application instance
app.include_router(vegetable_Curd_router)
app.include_router(hotel_curd_router)
app.include_router(orders_router)
app.include_router(dealer_router)



@app.post("/login", response_model=HotelLoginResponse)
async def hotel_login(credentials: HotelLogin):
    """Verify hotel login credentials"""
    hotel = hotels.find_one({"email": credentials.email, "status": "active"})

    
    if not hotel:
        raise HTTPException(status_code=401, detail="Invalid email or inactive account")
    
    # Verify password (plain text for demo - use bcrypt in production)
    if hotel["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Convert ObjectId and prepare response
   # hotel["_id"] = str(hotel.get("_id", ""))
    print("Status:", hotel)
    return hotel

@app.get("/health")
async def health_check():
    # Update timestamp to force modification every time
    result = hotels.update_many(
        {}, 
        {
            "$set": {
                "type": "hotel",
                "last_checked": datetime.now()
            }
        }
    )

    print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
    return {
        "status": "Hotel API running", 
        "matched_documents": result.matched_count,
        "modified_documents": result.modified_count
    }
