from fastapi import HTTPException
from app.functions.functionsV2 import calculate_path_and_time, display_ids
from app.functions.functionsV2 import (
    get_trajets_for_metro,
    get_max_len,
    get_stations_id_and_name_per_metro,
    filter_idx_trajects,
    join_all_metro_connections,
    create_metro_empty_graph,
    convert_graph_list_to_dict,
    analyze_graph
)
from app.functions.functionsV2 import analyze_graph

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

def analyze_network_and_mst():
    try:
        trajects_per_metro = get_trajets_for_metro()
        list_of_trajet = get_max_len(trajects_per_metro)
        metro_info = get_stations_id_and_name_per_metro(trajects_per_metro, list_of_trajet)
        new_list = filter_idx_trajects(trajects_per_metro, metro_info, list_of_trajet)
        complete_data, filtered_ids = join_all_metro_connections(trajects_per_metro, new_list, metro_info)

        graph_matrix = create_metro_empty_graph(filtered_ids, complete_data)
        graph_dict = convert_graph_list_to_dict(graph_matrix, filtered_ids)
        
        return analyze_graph(graph_dict)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""def get_stations_for_line(metro_line: int):
    if not (1 <= metro_line <= 14):
        raise HTTPException(status_code=400, detail="Invalid metro line number. Must be between 1 and 14.")
    try:
        return display_specific_metro_stations(metro_line)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))"""