from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.services.metro_service import get_trip, get_all_station_ids, analyze_network_and_mst

router = APIRouter()

class TripRequest(BaseModel):
    start: int
    end: int
    actual_time: str = "8:30:00"  # Default time if not provided

@router.post("/calculate_trip")
async def calculate_trip_endpoint(request_body: TripRequest, request: Request):
    try:
        data = request.app.state.metro_data
        return get_trip(request_body.start, request_body.end, data, request_body.actual_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/station_ids")
async def station_ids_endpoint(request: Request):
    try:
        data = request.app.state.metro_data
        return get_all_station_ids(data)
    except Exception as e:
        print("Error in /station_ids:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analyze_network")
async def analyze_network_endpoint(request: Request):
    try:
        data = request.app.state.metro_data
        return analyze_network_and_mst(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))