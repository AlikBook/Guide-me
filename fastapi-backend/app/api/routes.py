from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.services.metro_service import get_trip, get_all_station_ids, analyze_network_and_mst
from app.core.station_coordinates import (
    get_all_station_coordinates, 
    get_station_coordinates, 
    get_station_coordinates_with_mapping,
    get_station_coordinates_by_line_type,
    get_metro_station_coordinates,
    get_rer_station_coordinates,
    get_all_lines, 
    get_line_info,
)

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

@router.get("/station_coordinates")
async def get_station_coordinates_endpoint():
    """Get all station coordinates for the map with normalized mapping"""
    try:
        coordinates = get_station_coordinates_with_mapping()
        lines = get_all_lines()
        
        return {
            "stations": coordinates,
            "lines": lines,
            "total_stations": len(coordinates)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/station_coordinates/{station_name}")
async def get_single_station_coordinates(station_name: str):
    """Get coordinates for a specific station"""
    try:
        coords = get_station_coordinates(station_name)
        if coords is None:
            raise HTTPException(status_code=404, detail=f"Station '{station_name}' not found")
        
        return {
            "station": station_name,
            "coordinates": coords
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/station_coordinates_by_line/{station_name}/{line_key}")
async def get_station_coordinates_by_line(station_name: str, line_key: str):
    """Get coordinates for a specific station based on line type"""
    try:
        coords = get_station_coordinates_by_line_type(station_name, line_key)
        if coords is None:
            raise HTTPException(status_code=404, detail=f"Station '{station_name}' not found for line '{line_key}'")
        
        return {
            "station": station_name,
            "line": line_key,
            "coordinates": coords
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metro_stations")
async def get_metro_stations():
    """Get all metro station coordinates"""
    try:
        return {
            "stations": get_metro_station_coordinates(),
            "type": "metro"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rer_stations") 
async def get_rer_stations():
    """Get all RER station coordinates"""
    try:
        return {
            "stations": get_rer_station_coordinates(),
            "type": "rer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/network_data")
async def get_network_data_endpoint(request: Request):
    """Get complete network data including stations with coordinates and connections"""
    try:
        # Get station data from the existing system
        data = request.app.state.metro_data
        station_data = get_all_station_ids(data)
        
        # Get coordinate data
        coordinates = get_all_station_coordinates()
        lines = get_all_lines()
        
        # Enrich station data with coordinates
        enriched_stations = []
        for station in station_data.get("stations", []):
            station_name = station.get("station_name")
            coords = get_station_coordinates(station_name)
            
            enriched_station = {
                **station,
                "coordinates": coords,
                "has_coordinates": coords is not None
            }
            enriched_stations.append(enriched_station)
        
        return {
            "stations": enriched_stations,
            "line_definitions": lines,
            "coordinate_coverage": len([s for s in enriched_stations if s["has_coordinates"]]),
            "total_stations": len(enriched_stations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

