import os
import pickle
from app.functions.reads_and_pickles import load_ratp_data, read_and_save_stops, read_transfers, get_detailed_trips_for_RER, read_RER_lines
from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
import heapq
# Ensure the pickle directory exists
PICKLE_DIR = os.path.join(os.path.dirname(__file__), "container_pkl_files")
os.makedirs(PICKLE_DIR, exist_ok=True)

def get_pickle_path(filename):
    return os.path.join(PICKLE_DIR, filename)

def create_metro_ids():
    metro_lines = []
    for i in range(1,18):
        if i != 15:
            metro_lines.append("C0"+str(1370+i))
    return metro_lines

def get_trajets_for_metro():
    pkl_file = get_pickle_path("trajects_per_metro.pkl")
    if os.path.exists(pkl_file) and os.path.getsize(pkl_file) > 0:
        with open(pkl_file, "rb") as f:
            trajects_per_metro = pickle.load(f)
        return trajects_per_metro

    ratp_data = load_ratp_data()
    trajects_per_metro = {}
    metro_lines = create_metro_ids()
    for i, line in enumerate(metro_lines, 1):
        key = f"Metro :{i}"
        trajects_per_metro[key] = {}
        previous_trajet = ""
        n_trajet = 1
        for trajet in ratp_data:
            if trajet[3] == line:
                trajet_key = f"Trajet {n_trajet}"
                if trajet_key not in trajects_per_metro[key]:
                    trajects_per_metro[key][trajet_key] = []
                if previous_trajet == "":
                    previous_trajet = trajet[4]
                elif previous_trajet != trajet[4]:
                    n_trajet += 1
                    trajet_key = f"Trajet {n_trajet}"
                    trajects_per_metro[key][trajet_key] = []
                    previous_trajet = trajet[4]
                trajects_per_metro[key][trajet_key].append(trajet[:8])
    with open(pkl_file, "wb") as f:
        pickle.dump(trajects_per_metro, f)
    return trajects_per_metro

def is_subsequence(sub, seq):
    n, m = len(sub), len(seq)
    for i in range(m - n + 1):
        if seq[i:i+n] == sub:
            return True
    return False

def get_max_len(trajects_per_metro):
    pickle_file = get_pickle_path("max_len_results.pkl")

    if os.path.exists(pickle_file):
        with open(pickle_file, "rb") as f:
            return pickle.load(f)

    list_of_trajet = []
    for i in range(1, 17):
        key = f"Metro :{i}"
        trajet_keys = list(trajects_per_metro[key].keys())
        max_len = 0
        max_index_traject = 0
        for j, trajet in enumerate(trajet_keys, 1):
            l = len(trajects_per_metro[key][trajet])
            if l > max_len:
                max_len = l
                max_index_traject = j
        seen_sequences = []
        idx_to_add = []
        for j, trajet in enumerate(trajet_keys, 1):
            stops = tuple(stop[7] for stop in trajects_per_metro[key][trajet])
            if not any(is_subsequence(stops, saved_stops) for saved_stops in seen_sequences):
                seen_sequences.append(stops)
                idx_to_add.append(j)
        list_of_trajet.append(idx_to_add)
    
    list_of_trajet = filter_subsequences(list_of_trajet, trajects_per_metro)

    with open(pickle_file, "wb") as f:
        pickle.dump(list_of_trajet, f)

    return list_of_trajet
  
def filter_subsequences(list_of_trajet, trajects_per_metro):
    for i in range(1, 17):
        key = f"Metro :{i}"
        
        idx_to_remove = []
        for idx in list_of_trajet[i-1]:
            stops = tuple(stop[7] for stop in trajects_per_metro[key][f"Trajet {idx}"])
            for other_idx in list_of_trajet[i-1]:
                other_stops = tuple(stop[7] for stop in trajects_per_metro[key][f"Trajet {other_idx}"])
                if is_subsequence(stops, other_stops) and idx != other_idx:
                    idx_to_remove.append(idx)
        for idx in set(idx_to_remove):
            if idx in list_of_trajet[i-1]:
                list_of_trajet[i-1].remove(idx)
        #Exceptional case for line 10
        if key == "Metro :10" and len(list_of_trajet[i-1]) > 1:
            list_of_trajet[i-1] = list_of_trajet[i-1][1:] 
        
    return list_of_trajet

def get_stations_id_and_name_per_metro(trajects_per_metro, list_of_trajet, stop_data):
    pickle_file = get_pickle_path("station_info_cache.pkl")
    pickle_file2 = get_pickle_path("all_metro_ids.pkl")

    # Return cached result if available
    if os.path.exists(pickle_file) and os.path.exists(pickle_file2):
        with open(pickle_file, "rb") as f1, open(pickle_file2, "rb") as f2:
            data1 = pickle.load(f1)
            data2 = pickle.load(f2)
            return data1, data2

    # Compute and cache result
    
    metro_stop_info = []
    all_metro_stop_info = []
    for stop in stop_data:
        stop_id = stop[0]
        wheelchair = stop[2] if len(stop) > 2 else 0 
        for i, metro_trajet in enumerate(list_of_trajet, 1):
            for idx in metro_trajet:
                key = f"Metro :{i}"
                for trajet in trajects_per_metro[key][f"Trajet {idx}"]:
                    if stop_id == trajet[7].split(":")[-1]:
                        all_metro_stop_info.append((stop_id, stop[1], i, wheelchair))
                        if all(existing_id != stop_id for existing_id, *_ in metro_stop_info):
                            metro_stop_info.append((stop_id, stop[1], i, wheelchair))

    with open(pickle_file, "wb") as f:
        pickle.dump(metro_stop_info, f)
    with open(pickle_file2, "wb") as f:
        pickle.dump(all_metro_stop_info, f)

    return metro_stop_info, all_metro_stop_info


def filter_idx_trajects(trajects_per_metro, metro_stop_info, list_of_trajet):
    new_list_of_trajet = []
    temp_list = []
    for i, trajet in enumerate(list_of_trajet, 1):
        key = f"Metro :{i}"
        if i == 10:
            new_list_of_trajet.append(trajet[:])
            continue  
        if i == 16:
            new_list_of_trajet.append(trajet[:])
            continue
        new_trajet = []
        for idx in trajet:
            stops = trajects_per_metro[key][f"Trajet {idx}"]
            init_stop = stops[0][7].split(":")[-1]
            final_stop = stops[-1][7].split(":")[-1]
            init_stop_name = next((stop[1] for stop in metro_stop_info if stop[0] == init_stop), None)
            final_stop_name = next((stop[1] for stop in metro_stop_info if stop[0] == final_stop), None)
            if len(temp_list) > 0:
                if (init_stop_name, final_stop_name) not in temp_list and (final_stop_name, init_stop_name) not in temp_list:
                    temp_list.append((init_stop_name, final_stop_name))
                    new_trajet.append(idx)
            else:
                temp_list.append((init_stop_name, final_stop_name))
                new_trajet.append(idx)
        new_list_of_trajet.append(new_trajet)
    return new_list_of_trajet

def time_difference_seconds(time1, time2):
    def to_seconds(t):
        h, m, s = map(int, t.split(":"))
        return h * 3600 + m * 60 + s

    return to_seconds(time1) - to_seconds(time2)

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

def get_connections_per_metro(trajects_per_metro, new_list_of_trajet, metro_info):
    metro_stations = get_unique_stops_per_line(metro_info)
    
    unique_connections = set()
    filtered_connections = []
    for i, key in enumerate(trajects_per_metro,0):
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
                conn_key = frozenset([canon_id1, canon_id2])
                if conn_key not in unique_connections:
                    unique_connections.add(conn_key)
                    filtered_connections.append([canon_id1, canon_id2, time_diff])
    return filtered_connections

def get_filtered_metro_ids(connections):
 
    ids = set()
    for con in connections:
        ids.add(con[0])
        ids.add(con[1])
    return sorted(ids)



def join_all_connections(trajects_per_metro, new_list_trajet, metro_info,rer_stop_data):
    
    metro_connections = get_connections_per_metro(trajects_per_metro, new_list_trajet, metro_info)
    filtered_metro_ids = get_filtered_metro_ids(metro_connections)
    
    
    rer_connections = get_rer_connections(rer_stop_data)
    rer_station_ids = [stop[0] for stop in rer_stop_data]
    
    
    all_station_ids = sorted(set(filtered_metro_ids + rer_station_ids))
    
    
    transfer_data = read_transfers(filtered_metro_ids, rer_stop_data)
    
    
    complete_metro_data = metro_connections + transfer_data
    
    return complete_metro_data, all_station_ids, rer_connections

def get_edges_and_graph(all_station_ids, complete_data, id_to_index, rer_connections=None):
    
    n = len(all_station_ids)
    graph = [[0 for _ in range(n)] for _ in range(n)]
    edges = []

    
    rer_station_ids = set()
    if rer_connections:
        for id1, id2, time in rer_connections:
            rer_station_ids.add(id1)
            rer_station_ids.add(id2)

    
    edges_not_symetric = set()
    metro_asymmetric_pairs = [
        ("462958", "21971"), 
        ("21982", "462958"), 
        ("21988", "463239"), 
        ("21974", "21988"), 
        ("24686", "24682"), 
        ("24687", "24686")
    ]
    
    for id1, id2 in metro_asymmetric_pairs:
        if id1 in id_to_index and id2 in id_to_index:
            edges_not_symetric.add((id_to_index[id1], id_to_index[id2]))

    for id1, id2, time in complete_data:
        if id1 in id_to_index and id2 in id_to_index:
            i = id_to_index[id1]
            j = id_to_index[id2]
            time_int = int(time)

            graph[i][j] = time_int
            edges.append((i, j, time_int))

            # Check if this is a transfer connection (involves RER station)
            is_transfer = id1 in rer_station_ids or id2 in rer_station_ids
            
            # Add reverse connection if:
            # 1. Not asymmetric metro connection, OR
            # 2. It's a transfer connection (always bidirectional)
            if (i, j) not in edges_not_symetric or is_transfer:
                graph[j][i] = time_int
                edges.append((j, i, time_int))

    # Process RER connections if provided
    if rer_connections:
        for id1, id2, time in rer_connections:
            if id1 in id_to_index and id2 in id_to_index:
                i = id_to_index[id1]
                j = id_to_index[id2]
                time_int = int(time)

                # For RER, connections are typically bidirectional
                # Only add if not already set (to avoid overwriting existing connections)
                if graph[i][j] == 0:
                    graph[i][j] = time_int
                    edges.append((i, j, time_int))
                
                if graph[j][i] == 0:
                    graph[j][i] = time_int
                    edges.append((j, i, time_int))

    return edges, graph

def check_connection(path, index_to_id, metro_info, rer_stop_data=None):
    path_names = []
    path_station_ids = []
    
    # Create a combined info dictionary
    all_station_info = {}
    
    # Add metro info
    for metro_id in metro_info:
        all_station_info[metro_id[0]] = metro_id[1]  # id -> name
    
    # Add RER info if available
    if rer_stop_data:
        for rer_stop in rer_stop_data:
            all_station_info[rer_stop[0]] = rer_stop[1]  # id -> name
    
    # Process ALL stations in path, not just those we have info for
    for station in path:
        station_id = index_to_id[station]
        path_station_ids.append(station_id)
        
        if station_id in all_station_info:
            path_names.append(all_station_info[station_id])
        else:
            # For unknown stations, use the station_id as name
            path_names.append(f"Unknown_{station_id}")
    
    # Now we should have complete lists
    if len(path_station_ids) != len(path):
        # This should not happen now, but keep as safety check
        return False
    
    # Check for repeated STATION IDs (not names) - this catches true backtracking
    seen_station_ids = set()
    for station_id in path_station_ids:
        if station_id in seen_station_ids:
            return True  # Found a repeated station ID - invalid path
        seen_station_ids.add(station_id)
    
    # Additional check: if path has fewer than 2 unique stations, it's invalid
    if len(set(path_names)) < 2:
        return True
    
    # Check for inefficient patterns using station IDs (A->B->A type patterns)
    for i in range(len(path_station_ids) - 2):
        if path_station_ids[i] == path_station_ids[i + 2]:
            return True  # Found A->X->A pattern - likely inefficient
    
    # NEW: Check for redundant transfers at the same station
    # Group consecutive stations with the same name
    station_groups = []
    current_group = []
    prev_name = None
    
    for i, name in enumerate(path_names):
        if name != prev_name:
            if current_group:
                station_groups.append(current_group)
            current_group = [i]
        else:
            current_group.append(i)
        prev_name = name
    
    if current_group:
        station_groups.append(current_group)
    
    # Check for groups with more than 2 consecutive stations at the same location
    # This indicates unnecessary back-and-forth transfers
    for group in station_groups:
        if len(group) > 2:
            return True  # Too many consecutive visits to the same station
    
    # NEW: Check for redundant single-station segments
    # If we have A -> B -> A pattern where B is a single station, it's likely redundant
    consecutive_same_station_count = 0
    for i in range(len(path_names)):
        if i > 0 and path_names[i] == path_names[i-1]:
            consecutive_same_station_count += 1
            if consecutive_same_station_count > 1:  # More than 2 consecutive same stations
                return True
        else:
            consecutive_same_station_count = 0
    
    # NEW: Advanced redundancy check - detect unnecessary intermediate transfers
    # Look for patterns where we visit the same station multiple times with only single stations in between
    for i in range(len(path_names)):
        for j in range(i + 2, len(path_names)):
            if path_names[i] == path_names[j]:
                # Check if there's only one unique station between i and j
                intermediate_stations = set(path_names[i+1:j])
                if len(intermediate_stations) == 1:
                    # This suggests an unnecessary transfer: A -> B -> A
                    return True
    
    return False

def is_station_transfer_consistent(stations_by_line):
        prev_last_station = None
        for line_dict in stations_by_line:
            line_name, stations = next(iter(line_dict.items()))
            if prev_last_station:
                current_first_station = stations[0]["station"]
                if current_first_station != prev_last_station:
                    return False
            prev_last_station = stations[-1]["station"]
        return True

def calculate_path_and_time(start_id, end_id, edges, metro_info, all_station_ids, id_to_index, rer_stop_data, rer_with_line, complete_data=None):
    k = 10
    paths = get_k_shortest_paths(edges, start_id, end_id, k)
    index_to_id = {idx: stop_id for idx, stop_id in enumerate(all_station_ids)}

    list_of_paths = []
    list_of_trips = []

    # Create transfer time lookup dictionary from complete_data
    transfer_times = {}
    if complete_data:
        for id1, id2, time in complete_data:
            transfer_times[(id1, id2)] = int(time)
            transfer_times[(id2, id1)] = int(time)  # Make it bidirectional

    # Create info mappings for both metro and RER
    metro_id_to_info = {id: (name, line, wheelchair) for id, name, line, wheelchair in metro_info}
    
    # Create a mapping that handles multiple lines per RER station
    rer_id_to_all_info = {}
    for id, name, line_name, wheelchair in rer_with_line:
        if id not in rer_id_to_all_info:
            rer_id_to_all_info[id] = []
        rer_id_to_all_info[id].append((name, line_name, wheelchair))

    for cost, path in paths:
        
        if path in list_of_paths:
            continue  
            
        if check_connection(path, index_to_id, metro_info, rer_stop_data):
                continue  
        
        if len(path) > 50:  
            continue

        list_of_paths.append(path)

        rer_line_assignments = {}
        for path_idx, idx in enumerate(path):
            stop_id = index_to_id[idx]
            if stop_id in rer_id_to_all_info:
                correct_line = determine_rer_line_from_context(stop_id, path_idx, path, index_to_id, rer_with_line)
                rer_line_assignments[stop_id] = correct_line

        # Use a list to handle multiple segments of the same line
        stations_segments = []
        current_segment = None
        prev_line = None
        prev_line_type = None

        for path_idx, idx in enumerate(path):
            stop_id = index_to_id[idx]
            
            # Check if it's a metro station first
            if stop_id in metro_id_to_info:
                name, line, wheelchair = metro_id_to_info[stop_id]
                line_type = 'metro'
                
                # Map bis lines for metro
                display_line = line
                if line == 15:
                    display_line = '3bis'
                elif line == 16:
                    display_line = '7bis'
                
                key = f"Metro {display_line}"
                
            # Check if it's a RER station
            elif stop_id in rer_id_to_all_info:
                # Use pre-determined line assignment
                correct_line = rer_line_assignments[stop_id]
                
                # Get the info for the determined line
                station_info = next((name, line_name, wheelchair) for name, line_name, wheelchair in rer_id_to_all_info[stop_id] if line_name == correct_line)
                name, line_name, wheelchair = station_info
                
                line = line_name
                line_type = 'rer'
                key = f"RER {line_name}"
            else:
                # Handle unknown stations
                continue

            # Create station info
            station_info = {
                "id": str(id_to_index.get(stop_id, idx)),
                "station": name,
                "wheelchair_accessible": wheelchair
            }

            # Check if we need to start a new segment
            if line != prev_line or line_type != prev_line_type or current_segment is None:
                # Start a new segment
                current_segment = {
                    "line_key": key,
                    "stations": [station_info]
                }
                stations_segments.append(current_segment)
            else:
                # Continue current segment
                current_segment["stations"].append(station_info)
            
            prev_line = line
            prev_line_type = line_type

        # Convert segments to the expected format and add transfer times
        stations_list = []
        for i, segment in enumerate(stations_segments):
            segment_dict = {segment["line_key"]: segment["stations"]}
            
            # Add transfer time if this is not the first segment
            if i > 0:
                # Get the last station of previous segment and first station of current segment
                prev_segment = stations_segments[i-1]
                prev_last_station_id = prev_segment["stations"][-1]["id"]
                current_first_station_id = segment["stations"][0]["id"]
                
                # Convert index-based IDs back to actual station IDs
                prev_station_actual_id = index_to_id[int(prev_last_station_id)]
                current_station_actual_id = index_to_id[int(current_first_station_id)]
                
                # Look up transfer time
                transfer_time = transfer_times.get((prev_station_actual_id, current_station_actual_id))
                if transfer_time:
                    segment_dict["transfer_time"] = f"{transfer_time // 60} min {transfer_time % 60} sec"
            
            stations_list.append(segment_dict)

        var_return = {
            "total_time": f"{int(cost // 60)} minutes and {int(cost % 60)} seconds",
            "stations": stations_list
        }
        list_of_trips.append(var_return)

    return list_of_trips



def display_ids(metro_info, all_station_ids, rer_stop_data=None, rer_with_line=None):
  
    index_to_id = {idx: stop_id for idx, stop_id in enumerate(all_station_ids)}
    metro_dict = {stop_id: (name, line, wheelchair) for stop_id, name, line, wheelchair in metro_info}
    
    # Create RER dictionary if RER is enabled
    rer_dict = {}
    if rer_with_line:
        for stop_id, name, line_name, wheelchair in rer_with_line:
            if stop_id not in rer_dict:
                rer_dict[stop_id] = []
            rer_dict[stop_id].append((name, line_name, wheelchair))
    
    json_list_return = {"stations": []}
    
    for idx, stop_id in index_to_id.items():
        # Check if it's a metro station
        if stop_id in metro_dict:
            name, line, wheelchair = metro_dict[stop_id]
            
            if line == 15:
                line = '3bis'
            elif line == 16:
                line = '7bis'
            
            json_list_return["stations"].append({
                "id": str(idx),
                "station": str(name),
                "line": f"Metro {line}",
                "wheelchair_accessible": wheelchair
            })
        
        # Check if it's a RER station
        elif stop_id in rer_dict:
            # For RER stations with multiple lines, add each line as a separate entry
            for name, line_name, wheelchair in rer_dict[stop_id]:
                json_list_return["stations"].append({
                    "id": str(idx),
                    "station": str(name),
                    "line": f"RER {line_name}",
                    "wheelchair_accessible": wheelchair
                })
    
    return json_list_return

def filter_similar_trips(rer_traject_per_line):
    rer_filtered_trips = {route_id: {} for route_id in rer_traject_per_line}

    for id in rer_traject_per_line:
        list_of_terminus =[]
        index_list = []
        for i, (trajet_n, list_of_trips) in enumerate(rer_traject_per_line[id].items()):
            pair_terminus = [list_of_trips[0][3],list_of_trips[-1][3]]
            if pair_terminus not in list_of_terminus:
                list_of_terminus.append(pair_terminus)
                trip_number = int(trajet_n.split(": ")[1])
                index_list.append(trip_number)
        rer_filtered_trips[id] = index_list
    return rer_filtered_trips

def get_RER_unique_station_ids_and_names(rer_traject_per_line, rer_filtered_trips, stops_data):
    unique_ids = {}
    
    for id, list_of_indexes in rer_filtered_trips.items():
        for index in list_of_indexes:
            for trip in rer_traject_per_line[id][f"Trip: {index}"]:
                if trip[3] not in unique_ids:
                    unique_ids[trip[3]] = set()
                unique_ids[trip[3]].add(id)

    rer_lines = read_RER_lines()
    RER_stop_data = []
    
    for id in unique_ids:
        rer_name = next((stop[1] for stop in stops_data if stop[0] == id), None)
        if rer_name:
            RER_stop_data.append([id, rer_name])
    
    RER_stop_data_with_line = []
    for stop in RER_stop_data:
        stop_id = stop[0]
        stop_name = stop[1]
        # Get wheelchair accessibility from stops_data
        stop_info = next((stop for stop in stops_data if stop[0] == stop_id), None)
        wheelchair = stop_info[2] if stop_info and len(stop_info) > 2 else 0
        
        lines = unique_ids[stop_id]
        for line in rer_lines:
            if line[0] in lines:
                RER_stop_data_with_line.append([stop_id, stop_name, line[2], wheelchair])

    return RER_stop_data, RER_stop_data_with_line

def get_rer_stop_data(stops_data):
    """Get RER station data for transfer connections"""
    stops_data = read_and_save_stops()
    rer_traject_per_line = get_detailed_trips_for_RER()
    rer_filtered_trips = filter_similar_trips(rer_traject_per_line)
    RER_stop_data, RER_stop_data_with_line = get_RER_unique_station_ids_and_names(rer_traject_per_line, rer_filtered_trips, stops_data)
    return RER_stop_data,RER_stop_data_with_line

def get_connections_per_rer(rer_traject_per_line, rer_filtered_trips):
    """Get RER connections similar to the rer_read.py implementation"""
    connections = []
    pair_of_connections = []
    
    for rer_id, indexes in rer_filtered_trips.items():
        for idx in indexes:
            trajet = rer_traject_per_line[rer_id][f"Trip: {idx}"]
            
            for j in range(1, len(trajet)):
                stop_id1 = trajet[j-1][3]
                stop_id2 = trajet[j][3]
                
                if [stop_id1, stop_id2] not in pair_of_connections:
                    pair_of_connections.append([stop_id1, stop_id2])
                    time_diff = abs(time_difference_seconds(trajet[j][2], trajet[j-1][2]))
                    connections.append([stop_id1, stop_id2, time_diff])
                else:
                    # If the connection already exists, update the time if it's shorter
                    time_diff = abs(time_difference_seconds(trajet[j][2], trajet[j-1][2]))
                    for conn in connections:
                        if conn[0] == stop_id1 and conn[1] == stop_id2:
                            if time_diff < conn[2]:
                                conn[2] = time_diff
                            break
                
    return connections

def get_rer_connections(rer_stop_data):
    """Get RER connections with caching"""
    pkl_file = get_pickle_path("rer_connections.pkl")
    
    if os.path.exists(pkl_file):
        with open(pkl_file, "rb") as f:
            return pickle.load(f)
    
    rer_traject_per_line = get_detailed_trips_for_RER()
    rer_filtered_trips = filter_similar_trips(rer_traject_per_line)
    rer_connections = get_connections_per_rer(rer_traject_per_line, rer_filtered_trips)
    
    # Cache the result
    with open(pkl_file, "wb") as f:
        pickle.dump(rer_connections, f)
    
    return rer_connections

def determine_rer_line_from_context(stop_id, path_idx, path, index_to_id, rer_with_line):
    """
    Determine the correct RER line for a station based on the entire path context
    """
    # Get all possible lines for this station
    possible_lines = [line_name for id, name, line_name, wheelchair in rer_with_line if id == stop_id]
    
    if len(possible_lines) <= 1:
        return possible_lines[0] if possible_lines else None
    
    # Collect all RER stations and their lines in the entire path
    path_rer_stations = {}
    for i, idx in enumerate(path):
        station_id = index_to_id[idx]
        station_lines = [line_name for id, name, line_name, wheelchair in rer_with_line if id == station_id]
        if station_lines:
            path_rer_stations[i] = (station_id, station_lines)
    
    # Find which line appears most consistently in the path around this station
    line_scores = {}
    for line in possible_lines:
        line_scores[line] = 0
        
        # Check all other RER stations in the path
        for other_idx, (other_station_id, other_lines) in path_rer_stations.items():
            if other_idx != path_idx and line in other_lines:
                # Give higher weight to closer stations
                distance = abs(other_idx - path_idx)
                weight = max(1, 10 - distance)  # Closer stations get higher weight
                line_scores[line] += weight
    
    # Return the line with the highest score
    if line_scores:
        best_line = max(line_scores.keys(), key=lambda x: line_scores[x])
        # Only return if there's a clear preference, otherwise use fallback logic
        if line_scores[best_line] > 0:
            return best_line
    
    # Fallback: check immediate neighbors only
    adjacent_lines = []
    if path_idx > 0:
        prev_stop_id = index_to_id[path[path_idx - 1]]
        prev_lines = [line_name for id, name, line_name, wheelchair in rer_with_line if id == prev_stop_id]
        adjacent_lines.extend(prev_lines)
    
    if path_idx < len(path) - 1:
        next_stop_id = index_to_id[path[path_idx + 1]]
        next_lines = [line_name for id, name, line_name, wheelchair in rer_with_line if id == next_stop_id]
        adjacent_lines.extend(next_lines)
    
    for line in possible_lines:
        if line in adjacent_lines:
            return line
    
    # Final fallback: return the first possible line
    return possible_lines[0]

def convert_graph_list_to_dict(matrix, all_station_ids):
    
    graph = {node_id: {} for node_id in all_station_ids}
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                graph[all_station_ids[i]][all_station_ids[j]] = matrix[i][j]
    return graph

def is_connected(graph: dict[str, dict[str, int]]):
    
    if not graph:
        return False
        
    visited = set()
    start_node = next(iter(graph))

    def dfs(node):
        visited.add(node)
        for neighbor in graph[node]:
            if neighbor not in visited:
                dfs(neighbor)

    dfs(start_node)
    return len(visited) == len(graph)

def prim_mst(graph: dict[str, dict[str, int]]):
    
    if not graph:
        return None, []
        
    start_node = next(iter(graph))
    visited = set([start_node])
    edges = [(weight, start_node, neighbor) for neighbor, weight in graph[start_node].items()]
    heapq.heapify(edges)

    mst_edges = []
    total_cost = 0

    while edges and len(visited) < len(graph):
        weight, u, v = heapq.heappop(edges)
        if v not in visited:
            visited.add(v)
            mst_edges.append((u, v, weight))
            total_cost += weight
            for neighbor, w in graph[v].items():
                if neighbor not in visited:
                    heapq.heappush(edges, (w, v, neighbor))

    if len(visited) == len(graph):
        return total_cost, mst_edges
    else:
        return None, []

def analyze_graph(matrix, all_station_ids, metro_info=None):
    
    # Convert matrix to dictionary format for analysis
    graph_dict = convert_graph_list_to_dict(matrix, all_station_ids)
    
    connected = is_connected(graph_dict)
    cost, mst = prim_mst(graph_dict)

    if not connected:
        return {
            "is_connected": False,
            "message": "Le réseau de transport n'est pas connecté.",
            "mst_total_time": None,
            "mst_cost_seconds": None,
            "total_stations": len(all_station_ids),
            "total_connections": sum(len(neighbors) for neighbors in graph_dict.values()) // 2
        }

    return {
        "is_connected": True,
        "message": "Le réseau de transport est entièrement connecté.",
        "mst_total_time": f"{cost // 3600} heures et {(cost % 3600) // 60} minutes",
        "mst_cost_seconds": cost,
        "total_stations": len(all_station_ids),
        "total_connections": sum(len(neighbors) for neighbors in graph_dict.values()) // 2,
        "mst_edges_count": len(mst)
    }