from fastapi import HTTPException
from app.functions.functionsV2 import calculate_path_and_time, display_ids, stops_position, lines_info
from app.functions.functionsV1 import stations_position

def get_trip(start: int, end: int, graph: list, metro_info: list, filtered_metro_ids:list):
    try:
        trip = calculate_path_and_time(start, end, graph, metro_info, filtered_metro_ids)
        
        return trip
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_all_station_ids(metro_info: list, filtered_metro_ids:list):
    try:
        return display_ids(metro_info, filtered_metro_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""def get_stations_for_line(metro_line: int):
    if not (1 <= metro_line <= 14):
        raise HTTPException(status_code=400, detail="Invalid metro line number. Must be between 1 and 14.")
    try:
        return display_specific_metro_stations(metro_line)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""
    

    
"""
Services de la map

"""

def get_stations_position():
    try:
        return stations_position()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def get_stops_position():
    try:
        return stops_position()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
def get_lines_info():
    try:
        return lines_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))