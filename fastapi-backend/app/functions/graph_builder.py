"""Graph building and connection functions."""

from app.core.database import db_cursor
from app.services.transport_service import get_transfers


def get_edges_and_graph_v2(all_station_ids, id_to_index):
    """
    Builds the graph edges directly from the transfer and stop_times tables.
    This provides the 'Adjacency List' for Dijkstra and Yen.
    """
    edges = []
    
    with db_cursor() as cursor:
        # 1. Fetch Transfers (Walking between platforms)
        cursor.execute("SELECT from_stop_id, to_stop_id, min_transfer_time FROM transfers")
        for row in cursor.fetchall():
            u_id, v_id, weight = row[0], row[1], row[2]
            if u_id in id_to_index and v_id in id_to_index:
                weight_int = int(weight) if weight is not None else 0
                edges.append((id_to_index[u_id], id_to_index[v_id], max(60, weight_int)))

        # 2. Fetch Metro/RER segments (Consecutive stations)
        # This SQL trick finds stations that are next to each other in a trip
        cursor.execute("""
            SELECT a.stop_id, b.stop_id, 
            (strftime('%s', b.arrival_time) - strftime('%s', a.departure_time)) as travel_time
            FROM stop_times a
            JOIN stop_times b ON a.trip_id = b.trip_id 
            WHERE b.stop_sequence = a.stop_sequence + 1
        """)
        for row in cursor.fetchall():
            u_id, v_id, weight = row[0], row[1], row[2]
            if u_id in id_to_index and v_id in id_to_index:
                # Ensure a minimum weight of 60s to avoid 0-second edges
                edges.append((id_to_index[u_id], id_to_index[v_id], max(60, int(weight))))
    
    return edges


def get_edges_and_graph(all_station_ids, complete_data, id_to_index, rer_connections=None):
    """Build both edge list and adjacency matrix (legacy-compatible contract)."""
    n = len(all_station_ids)
    graph = [[0 for _ in range(n)] for _ in range(n)]
    edges = []

    rer_station_ids = set()
    if rer_connections:
        for id1, id2, _ in rer_connections:
            rer_station_ids.add(id1)
            rer_station_ids.add(id2)

    edges_not_symetric = set()
    metro_asymmetric_pairs = [
        ("462958", "21971"),
        ("21982", "462958"),
        ("21988", "463239"),
        ("21974", "21988"),
        ("24686", "24682"),
        ("24687", "24686"),
    ]

    for id1, id2 in metro_asymmetric_pairs:
        if id1 in id_to_index and id2 in id_to_index:
            edges_not_symetric.add((id_to_index[id1], id_to_index[id2]))

    for id1, id2, time in complete_data:
        if id1 in id_to_index and id2 in id_to_index:
            i = id_to_index[id1]
            j = id_to_index[id2]
            time_int = int(time) if time is not None else 0
            if time_int <= 0:
                time_int = 60

            graph[i][j] = time_int
            edges.append((i, j, time_int))

            is_transfer = id1 in rer_station_ids or id2 in rer_station_ids
            if (i, j) not in edges_not_symetric or is_transfer:
                graph[j][i] = time_int
                edges.append((j, i, time_int))

    if rer_connections:
        for id1, id2, time in rer_connections:
            if id1 in id_to_index and id2 in id_to_index:
                i = id_to_index[id1]
                j = id_to_index[id2]
                time_int = int(time) if time is not None else 0
                if time_int <= 0:
                    time_int = 60

                if graph[i][j] == 0:
                    graph[i][j] = time_int
                    edges.append((i, j, time_int))

                if graph[j][i] == 0:
                    graph[j][i] = time_int
                    edges.append((j, i, time_int))

    return edges, graph


def get_connections_per_metro(trajects_per_metro, new_list_of_trajet, metro_info):
    """Extract metro connections from trajectory data."""
    def time_difference_seconds(time1, time2):
        def to_seconds(t):
            h, m, s = map(int, t.split(":"))
            return h * 3600 + m * 60 + s
        diff = to_seconds(time1) - to_seconds(time2)
        # Handle schedules that wrap past midnight (GTFS can use extended-hour timestamps).
        if diff < 0:
            diff += 24 * 3600
        return diff

    def get_unique_stops_per_line(metro_info):
        metro_stations = {}
        for stop_id, stop_name, line_n, wheelchair in metro_info:
            metro_key = f"Metro :{line_n}"
            if metro_key not in metro_stations:
                metro_stations[metro_key] = {}
            if stop_name not in metro_stations[metro_key]:
                metro_stations[metro_key][stop_name] = stop_id

        sorted_metro = dict(
            sorted(metro_stations.items(), key=lambda item: int(item[0].split(":")[1]))
        )
        return sorted_metro

    metro_stations = get_unique_stops_per_line(metro_info)
    
    connection_times = {}
    for i, key in enumerate(trajects_per_metro, 0):
        use_canonical = len(new_list_of_trajet[i]) > 1
        for idx in new_list_of_trajet[i]:
            trajet = trajects_per_metro[key][f"Trajet {idx}"]
            for j in range(1, len(trajet)):
                stop_id1 = trajet[j-1][7].split(":")[-1]
                stop_id2 = trajet[j][7].split(":")[-1]
                if use_canonical:
                    stop_id1_name = next((stop[1] for stop in metro_info if stop[0] == stop_id1), None)
                    stop_id2_name = next((stop[1] for stop in metro_info if stop[0] == stop_id2), None)
                    canon_id1 = metro_stations[key].get(stop_id1_name, stop_id1)
                    canon_id2 = metro_stations[key].get(stop_id2_name, stop_id2)
                else:
                    canon_id1 = stop_id1
                    canon_id2 = stop_id2
                time_diff = time_difference_seconds(trajet[j][5], trajet[j-1][5])
                # Keep weights strictly positive so graph matrix (0=no edge) remains valid.
                if time_diff <= 0:
                    time_diff = 60
                conn_key = frozenset([canon_id1, canon_id2])
                previous = connection_times.get(conn_key)
                if previous is None or time_diff < previous[2]:
                    connection_times[conn_key] = [canon_id1, canon_id2, time_diff]

    filtered_connections = list(connection_times.values())
    return filtered_connections


def get_connections_per_rer(rer_traject_per_line, rer_filtered_trips):
    """Get RER connections similar to the rer_read.py implementation."""
    def time_difference_seconds(time1, time2):
        def to_seconds(t):
            h, m, s = map(int, t.split(":"))
            return h * 3600 + m * 60 + s
        return to_seconds(time1) - to_seconds(time2)

    connections = []
    pair_of_connections = []
    
    for rer_id, indexes in rer_filtered_trips.items():
        for idx in indexes:
            trip_key = idx if idx in rer_traject_per_line[rer_id] else f"Trip: {idx}"
            if trip_key not in rer_traject_per_line[rer_id]:
                continue
            trajet = rer_traject_per_line[rer_id][trip_key]
            
            for j in range(1, len(trajet)):
                stop_id1 = trajet[j-1][3]
                stop_id2 = trajet[j][3]
                
                if [stop_id1, stop_id2] not in pair_of_connections:
                    pair_of_connections.append([stop_id1, stop_id2])
                    time_diff = abs(time_difference_seconds(trajet[j][2], trajet[j-1][2]))
                    if time_diff <= 0:
                        time_diff = 60
                    connections.append([stop_id1, stop_id2, time_diff])
                else:
                    # If the connection already exists, update the time if it's shorter
                    time_diff = abs(time_difference_seconds(trajet[j][2], trajet[j-1][2]))
                    if time_diff <= 0:
                        time_diff = 60
                    for conn in connections:
                        if conn[0] == stop_id1 and conn[1] == stop_id2:
                            if time_diff < conn[2]:
                                conn[2] = time_diff
                            break
                
    return connections


def get_filtered_metro_ids(connections):
    """Extract unique metro station IDs from connections."""
    ids = set()
    for con in connections:
        ids.add(con[0])
        ids.add(con[1])
    return sorted(ids)


def join_all_connections(trajects_per_metro, new_list_trajet, metro_info, rer_stop_data):
    """Combine metro and RER connections with transfer data."""
    metro_connections = get_connections_per_metro(trajects_per_metro, new_list_trajet, metro_info)
    filtered_metro_ids = get_filtered_metro_ids(metro_connections)
    
    # Get RER connections
    from app.functions.data_loader import get_rer_connections
    rer_connections = get_rer_connections(rer_stop_data)
    rer_station_ids = [stop[0] for stop in rer_stop_data]
    
    # Combine all station IDs
    all_station_ids = sorted(set(filtered_metro_ids + rer_station_ids))
    
    # Read transfers directly from DB-backed service
    transfer_data = get_transfers(filtered_metro_ids, rer_stop_data)
    
    # Combine metro data with transfers
    complete_metro_data = metro_connections + transfer_data
    
    return complete_metro_data, all_station_ids, rer_connections


def convert_graph_list_to_dict(matrix, all_station_ids):
    """Convert adjacency matrix to dictionary representation."""
    graph = {node_id: {} for node_id in all_station_ids}
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                graph[all_station_ids[i]][all_station_ids[j]] = matrix[i][j]
    return graph
