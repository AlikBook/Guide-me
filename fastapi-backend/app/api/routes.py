from fastapi import APIRouter, Request,HTTPException

from pydantic import BaseModel
from app.services.metro_service import get_trip, get_all_station_ids

router = APIRouter()


class TripRequest(BaseModel):
    start: int
    end: int

@router.post("/calculate_trip")
async def calculate_trip_endpoint(request_body: TripRequest, request: Request):
    data = request.app.state.metro_data
    return get_trip(
        request_body.start,
        request_body.end,
        data["graph"],
        data["metro_info"],
        data["filtered_metro_ids"]
    )

@router.get("/station_ids")
async def station_ids_endpoint(request: Request):
    try:
        data = request.app.state.metro_data
        return get_all_station_ids(data["metro_info"], data["filtered_metro_ids"])
    except Exception as e:
        print("Error in /station_ids:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


from app.services.metro_service import analyze_network_and_mst

"""@router.get("/analyze_network")
async def analyze_network_endpoint(request: Request):
    data = request.app.state.metro_data
    graph = data["graph"]
    metro_info = data["metro_info"]
    return analyze_network_and_mst(graph, metro_info)"""

@router.get("/analyze_network")
async def analyze_network_endpoint():
    return analyze_network_and_mst()


"""@router.get("/stations/{line_number}")
async def stations_for_line_endpoint(line_number: int):
    return get_stations_for_line(line_number)"""