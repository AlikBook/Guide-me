from app.functions.functionsV3 import (
    get_trajets_for_metro, 
    get_max_len, 
    get_stations_id_and_name_per_metro, 
    filter_idx_trajects, 
    join_all_connections,
    get_edges_and_graph, 
    get_rer_stop_data
)
from app.functions.reads_and_pickles import read_and_save_stops, get_detailed_trips_for_RER, get_RER_trips

def load_all_data():
    """Load all necessary data for the transport network on startup"""
    print("Loading transport network data...")
    
    # Load base data
    stops_data = read_and_save_stops()
    trajects_per_metro = get_trajets_for_metro()
    list_of_trajet = get_max_len(trajects_per_metro)
    
    # Load RER trajectory data
    rer_trajects = get_detailed_trips_for_RER()
    rer_filtered_trips = get_RER_trips()
    
    # Get metro station information
    metro_info, all_metro_info = get_stations_id_and_name_per_metro(
        trajects_per_metro, list_of_trajet, stops_data
    )
    
    # Filter trajectories
    new_list_trajet = filter_idx_trajects(trajects_per_metro, metro_info, list_of_trajet)
    
    # Get RER data
    rer_stop_data, rer_with_line = get_rer_stop_data(stops_data)
    
    # Join all connections (metro + RER + transfers)
    complete_data, all_station_ids, rer_connections = join_all_connections(
        trajects_per_metro, new_list_trajet, metro_info, rer_stop_data
    )
    
    # Create ID to index mapping
    id_to_index = {stop_id: idx for idx, stop_id in enumerate(all_station_ids)}
    
    # Create edges and graph
    edges, graph = get_edges_and_graph(all_station_ids, complete_data, id_to_index, rer_connections)
    
    print(f"Loaded {len(all_station_ids)} stations and {len(edges)} connections")
    
    return {
        "edges": edges,
        "graph": graph,
        "metro_info": metro_info,
        "all_station_ids": all_station_ids,
        "id_to_index": id_to_index,
        "rer_stop_data": rer_stop_data,
        "rer_with_line": rer_with_line,
        "complete_data": complete_data,
        "rer_connections": rer_connections,
        "trajects_per_metro": trajects_per_metro,
        "rer_trajects": rer_trajects,
        "rer_filtered_trips": rer_filtered_trips,
        "list_of_trajet": list_of_trajet
    }