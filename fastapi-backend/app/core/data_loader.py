from app.functions.data_loader import (
    get_trajets_for_metro,
    get_max_len,
    get_stations_id_and_name_per_metro,
    filter_idx_trajects,
    get_rer_stop_data,
    filter_similar_trips,
)
from app.services.transport_service import get_all_stops, get_detailed_rer_trips
from app.functions.graph_builder import (
    join_all_connections,
    get_edges_and_graph
)

def load_all_data():
    """Load all necessary data for the transport network on startup"""
    print("Loading transport network data...")
    
    # Load base data
    print("Loading stops and metro trajectories...")
    stops_data = get_all_stops()
    print(f"Loaded {len(stops_data)} stops")
    trajects_per_metro = get_trajets_for_metro()
    print(f"Loaded trajectories for {len(trajects_per_metro)} metro lines")
    list_of_trajet = get_max_len(trajects_per_metro)
    print(f"Max trajectory length: {len(list_of_trajet)}")
    
    # Load RER trajectory data
    rer_trajects = get_detailed_rer_trips()
    print(f"Loaded detailed RER trajectories for {len(rer_trajects)} lines")
    rer_filtered_trips = filter_similar_trips(rer_trajects)
    print(f"Filtered RER trips, remaining: {sum(len(trips) for trips in rer_filtered_trips.values())}")
    
    # Get metro station information
    metro_info, all_metro_info = get_stations_id_and_name_per_metro(
        trajects_per_metro, list_of_trajet, stops_data
    )
    print(f"Extracted metro station information for {len(metro_info)} stations")
    
    # Filter trajectories
    new_list_trajet = filter_idx_trajects(trajects_per_metro, metro_info, list_of_trajet)
    
    print(f"Filtered trajectories, remaining: {len(new_list_trajet)}")
    # Get RER data
    rer_stop_data, rer_with_line = get_rer_stop_data(stops_data)
    print(f"Extracted RER stop data for {len(rer_stop_data)} stops")
    
    # Join all connections (metro + RER + transfers)
    complete_data, all_station_ids, rer_connections = join_all_connections(
        trajects_per_metro, new_list_trajet, metro_info, rer_stop_data
    )
    print(f"Combined all connections, total stations: {len(all_station_ids)}, total connections: {len(complete_data)}")
    
    # Create ID to index mapping
    id_to_index = {stop_id: idx for idx, stop_id in enumerate(all_station_ids)}
    
    print("Data loading complete.")
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