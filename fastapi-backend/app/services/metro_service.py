from fastapi import HTTPException
from app.functions.functionsV1 import calculate_path_and_time, display_ids, display_specific_metro_stations

def get_trip(start: int, end: int):
    try:
        trip = calculate_path_and_time(start, end)
        return trip
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_all_station_ids():
    try:
        return display_ids()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_stations_for_line(metro_line: int):
    if not (1 <= metro_line <= 14):
        raise HTTPException(status_code=400, detail="Invalid metro line number. Must be between 1 and 14.")
    try:
        return display_specific_metro_stations(metro_line)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))