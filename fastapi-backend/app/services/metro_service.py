from fastapi import HTTPException
from app.functions.pathfinding import (
    calculate_path_and_time_with_realistic_timing,
    display_ids,
    analyze_graph
)

def get_trip(start: int, end: int, data: dict, actual_time: str = "8:30:00"):
    """
    Calculate trip between two stations using preloaded data with realistic timing
    """
    try:
        # Extract all necessary data from the preloaded data dictionary
        edges = data["edges"]
        metro_info = data["metro_info"]
        all_station_ids = data["all_station_ids"]
        id_to_index = data["id_to_index"]
        rer_stop_data = data["rer_stop_data"]
        rer_with_line = data["rer_with_line"]
        complete_data = data.get("complete_data")
        trajects_per_metro = data.get("trajects_per_metro")
        rer_trajects = data.get("rer_trajects")
        rer_filtered_trips = data.get("rer_filtered_trips")
        list_of_trajet = data.get("list_of_trajet")
        
        # Calculate path using the new realistic timing function
        trips = calculate_path_and_time_with_realistic_timing(
            start, end, edges, metro_info, all_station_ids, 
            id_to_index, rer_stop_data, rer_with_line, 
            actual_time, complete_data, trajects_per_metro, 
            rer_trajects, rer_filtered_trips, list_of_trajet
        )
        
        # Return all trips with additional metadata
        if trips:
            return {
                "trips": trips,
                "total_options": len(trips)
            }
        else:
            return {"error": "No path found", "trips": [], "total_options": 0}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_all_station_ids(data: dict):
    try:
        metro_info = data["metro_info"]
        all_station_ids = data["all_station_ids"]
        rer_stop_data = data["rer_stop_data"]
        rer_with_line = data["rer_with_line"]
        
        return display_ids(metro_info, all_station_ids, rer_stop_data, rer_with_line)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def analyze_network_and_mst(data: dict):
    
    try:
        graph = data["graph"]
        all_station_ids = data["all_station_ids"]
        metro_info = data["metro_info"]
        
        return analyze_graph(graph, all_station_ids, metro_info)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))