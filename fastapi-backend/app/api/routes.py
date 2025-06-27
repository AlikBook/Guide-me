from fastapi import APIRouter
from pydantic import BaseModel
from app.services.metro_service import get_trip, get_all_station_ids, get_stations_for_line, get_stations_position

router = APIRouter()

class TripRequest(BaseModel):
    start: int
    end: int



@router.post("/calculate_trip")
async def calculate_trip_endpoint(request: TripRequest):
    """
    Route API qui retourne ... 
    ------------------
    ...
    """
    print(request)
    return get_trip(request.start, request.end)

@router.get("/station_ids")
async def station_ids_endpoint():
    """
    Route API qui retourne ... 
    ------------------
    ...
    """
    return get_all_station_ids()

@router.get("/stations/{line_number}")
async def stations_for_line_endpoint(line_number: int):
    """
    Route API qui retourne les stations du numéro de la ligne donnée en paramètre
    ------------------
    return: Json
        {
            "metro_line": <line_number>,
            "stations": 
            {
                ...
                {"id": <id>, "station": <nom de la station>, "line": <line_number>}
                ...
            }
        }
    """
    return get_stations_for_line(line_number)

@router.get("/stations_position")
async def stations_position_endpoint():
    """
    Route API qui retourne la position des stations
    ------------------
    return format:
    { 
        <metro line number (int)> : 
        {
            <Nom de la station (str)> : 
            [
                <pos_x (int)>, 
                <pos_y (int)>
            ]
        }
    }
    """
    return get_stations_position()
