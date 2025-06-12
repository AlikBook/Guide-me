from fastapi import APIRouter
from pydantic import BaseModel
from app.services.metro_service import get_trip, get_all_station_ids, get_stations_for_line

router = APIRouter()

class TripRequest(BaseModel):
    start: int
    end: int



@router.post("/calculate_trip")
async def calculate_trip_endpoint(request: TripRequest):
    print(request)
    return get_trip(request.start, request.end)

@router.get("/station_ids")
async def station_ids_endpoint():
    return get_all_station_ids()

@router.get("/stations/{line_number}")
async def stations_for_line_endpoint(line_number: int):
    return get_stations_for_line(line_number)