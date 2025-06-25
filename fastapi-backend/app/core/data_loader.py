from app.functions.functionsV2 import (
    get_trajets_for_metro, get_max_len, get_stations_id_and_name_per_metro,
    filter_idx_trajects, join_all_metro_connections, create_metro_empty_graph
)

def load_all_data():
    trajects_per_metro = get_trajets_for_metro()
    list_of_trajet = get_max_len(trajects_per_metro)
    metro_info = get_stations_id_and_name_per_metro(trajects_per_metro, list_of_trajet)
    new_list_trajet = filter_idx_trajects(trajects_per_metro, metro_info, list_of_trajet)
    complete_data, filtered_metro_ids = join_all_metro_connections(
        trajects_per_metro, new_list_trajet, metro_info
    )
    graph = create_metro_empty_graph(filtered_metro_ids, complete_data)

    return {
        "graph": graph,
        "metro_info": metro_info,
        "filtered_metro_ids": filtered_metro_ids
    }
