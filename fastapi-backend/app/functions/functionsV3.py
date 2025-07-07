import os
import pickle
from datetime import datetime, timedelta
from app.functions.reads_and_pickles import load_ratp_data, read_and_save_stops, read_transfers, get_detailed_trips_for_RER, read_RER_lines
try:
    from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
    HAS_YEN_WRAPPER = True
except ImportError:
    HAS_YEN_WRAPPER = False
    print("Warning: yen_wrapper not available, some functionality may be limited")
import heapq
from datetime import datetime, timedelta
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
    if not HAS_YEN_WRAPPER:
        print("Error: yen_wrapper not available. Please use alternative pathfinding methods.")
        return []
    
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
        
        # NEW: Check for unrealistic line patterns (same line used multiple times)
        if has_unrealistic_line_pattern(path, index_to_id, metro_info, rer_with_line):
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

# Realistic Time Calculation Functions (adapted from extractionV2_time_travel.py)

def duration_trajet(metro_name, trajet_name, trajects_per_metro):
    """
    Calculate the total duration of a metro journey in seconds
    Returns: dictionary with minutes and seconds
    """
    total_time = 0
    trajet = trajects_per_metro[metro_name][trajet_name]
    for i in range(1, len(trajet)):
        total_time += time_difference_seconds(trajet[i][5], trajet[i-1][5])
    
    minutes = total_time // 60
    seconds = total_time % 60
    return {
        'total_seconds': total_time,
        'minutes': minutes, 
        'seconds': seconds,
        'formatted': f"{minutes}m {seconds}s"
    }

def search_nearest_time_trajet(actual_time, start_id, target_metro_key, trajects_per_metro, end_id=None):
    """
    Find the nearest trajet that departs after the given time.
    If end_id is provided, only consider trajets that contain both start and end stations.
    If no future trips found, find the earliest trip and assume next day.
    """
    nearest_trajet = []
    min_time_diff = float('inf')
    duration = 0
    earliest_trip = None
    earliest_time = None

    for trajet, stops in trajects_per_metro[target_metro_key].items():
        # Get all station IDs in this trajet
        trajet_station_ids = [stop[7] for stop in stops]
        
        # If end_id is specified, check if both start and end stations are in this trajet
        if end_id is not None:
            if start_id not in trajet_station_ids or end_id not in trajet_station_ids:
                continue  # Skip this trajet if it doesn't contain both stations
        
        for stop in stops:
            if stop[7] == start_id:
                time_diff = time_difference_seconds(stop[5], actual_time)
                
                # Track earliest trip in case no future trips are found
                if earliest_trip is None or stop[5] < earliest_time:
                    earliest_trip = [target_metro_key, trajet, stop]
                    earliest_time = stop[5]
                
                # Look for trips departing after current time (including exact time)
                if 0 <= time_diff < min_time_diff:
                    min_time_diff = time_diff
                    nearest_trajet = [target_metro_key, trajet, stop]
                    duration_info = duration_trajet(target_metro_key, trajet, trajects_per_metro)
                    duration = duration_info['total_seconds']
                elif 0 <= time_diff == min_time_diff:
                    duration_info = duration_trajet(target_metro_key, trajet, trajects_per_metro)
                    if duration_info['total_seconds'] < duration:
                        nearest_trajet = [target_metro_key, trajet, stop]
                        duration = duration_info['total_seconds']
    
    # If no future trips found, use earliest trip from next day
    if not nearest_trajet and earliest_trip:
        print(f"Warning: No future trips found for {target_metro_key} from {start_id} after {actual_time}, using earliest trip from next day")
        nearest_trajet = earliest_trip
    
    return nearest_trajet

def search_nearest_time_rer_trip(actual_time, start_id, target_rer_id, rer_trajects, rer_filtered_trips, end_id=None):
    """
    Find RER trip for realistic wait time calculation.
    Since travel time is now calculated using Yen algorithm, this function only needs to provide departure times.
    """
    nearest_trip = []
    min_time_diff = float('inf')
    earliest_trip = None
    earliest_time = None
    
    # Try to find a real trip for realistic wait time
    if target_rer_id in rer_filtered_trips:
        for trip_idx in rer_filtered_trips[target_rer_id]:
            trip_key = f"Trip: {trip_idx}"
            if trip_key in rer_trajects[target_rer_id]:
                trip_stops = rer_trajects[target_rer_id][trip_key]
                
                # If end_id is specified, check if both stations are in this trip
                if end_id is not None:
                    stop_ids = [stop[3] for stop in trip_stops]
                    if start_id not in stop_ids or end_id not in stop_ids:
                        continue  # Skip this trip if it doesn't contain both stations
                
                # Look for the departure time from start_id
                for stop in trip_stops:
                    if stop[3] == start_id:
                        time_diff = time_difference_seconds(stop[2], actual_time)
                        
                        # Track earliest trip for fallback
                        if earliest_trip is None or stop[2] < earliest_time:
                            earliest_trip = [target_rer_id, trip_key, stop]
                            earliest_time = stop[2]
                        
                        # Look for trips departing after current time
                        if 0 <= time_diff < min_time_diff:
                            min_time_diff = time_diff
                            nearest_trip = [target_rer_id, trip_key, stop]
                        break
    
    # If no future trips found, use earliest trip or create synthetic
    if not nearest_trip:
        if earliest_trip:
            print(f"No future RER trips found, using earliest trip from next day")
            nearest_trip = earliest_trip
        else:
            # Create synthetic trip as fallback
            synthetic_time = add_seconds_to_time_str(actual_time, 600)  # 10 minutes from now
            synthetic_stop = [
                f"SYNTHETIC_{target_rer_id}",
                target_rer_id,
                synthetic_time,
                start_id
            ]
            nearest_trip = [target_rer_id, f"Trip: SYNTHETIC_{target_rer_id}", synthetic_stop]
    
    return nearest_trip

def calculate_partial_duration(trajet_name, start_id, end_id, metro_name, actual_time, trajects_per_metro):
    """
    Calculate partial duration between two stations in a metro journey
    """
    start_time = None
    end_time = None
    
    trajet = trajects_per_metro[metro_name][trajet_name]
    
    # Try different ID formats to find the stations
    def find_station_in_trajet(station_id, trajet):
        """Try different formats to find station in trajectory"""
        possible_formats = [
            station_id,
            station_id.replace("IDFM:", ""),
            f"IDFM:{station_id}" if not station_id.startswith("IDFM:") else station_id.replace("IDFM:", "")
        ]
        
        for stop in trajet:
            stop_id = stop[7]
            for format_id in possible_formats:
                if stop_id == format_id:
                    return stop[5]  # Return the time
        return None
    
    start_time = find_station_in_trajet(start_id, trajet)
    end_time = find_station_in_trajet(end_id, trajet)

    if start_time is None or end_time is None:
        # If we still can't find the stations, use a fallback calculation
        print(f"Warning: Station not found in trajet {trajet_name} ({metro_name}), using fallback duration")
        print(f"Start ID: {start_id} → {start_time}")
        print(f"End ID: {end_id} → {end_time}")
        
        # Fallback: use average time per station (2 minutes per station)
        fallback_duration = 120  # 2 minutes as fallback
        return {
            'total_seconds': fallback_duration,
            'minutes': fallback_duration // 60,
            'seconds': fallback_duration % 60,
            'formatted': f"{fallback_duration // 60}m {fallback_duration % 60}s"
        }
    
    total_seconds = time_difference_seconds(end_time, start_time)
    
    # Handle negative time (indicates wrong direction or data issue)
    if total_seconds < 0:
        total_seconds = abs(total_seconds)
        print(f"Warning: Negative time calculated for {trajet_name}, using absolute value")
    
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    return {
        'total_seconds': total_seconds,
        'minutes': minutes,
        'seconds': seconds,
        'formatted': f"{minutes}m {seconds}s"
    }

def calculate_partial_rer_duration_realistic(segment_stations, edges, all_station_ids, id_to_index):
    """
    Calculate realistic partial duration for RER journey using Yen implementation.
    
    This function replaces the previous theoretical timing calculation for RER.
    Instead of using estimated times based on station count, it uses the actual
    path from calculate_path_and_time and calculates realistic time using the 
    Yen shortest path algorithm on the actual graph with real connection times.
    
    Args:
        segment_stations: List of stations in the RER segment with their IDs from calculate_path_and_time
        edges: Graph edges from the pathfinding system
        all_station_ids: All station IDs in the system
        id_to_index: Mapping from station ID to graph index
    
    Returns:
        Dictionary with timing information (total_seconds, minutes, seconds, formatted)
    """
    if not HAS_YEN_WRAPPER:
        print("Error: yen_wrapper not available for RER duration calculation")
        return {
            'total_seconds': 300,  # 5 minute fallback
            'minutes': 5,
            'seconds': 0,
            'formatted': "5m 0s"
        }
    
    if len(segment_stations) < 2:
        return {
            'total_seconds': 0,
            'minutes': 0,
            'seconds': 0,
            'formatted': "0m 0s"
        }
    
    # Get start and end station indices for Yen algorithm
    start_station_id = segment_stations[0]['id']
    end_station_id = segment_stations[-1]['id']
    
    try:
        start_index = int(start_station_id)
        end_index = int(end_station_id)
        
        # Use Yen algorithm to get the shortest path between these two stations
        k = 1  # We only need the shortest path
        paths = get_k_shortest_paths(edges, start_index, end_index, k)
        
        if paths and len(paths) > 0:
            cost, path = paths[0]
            realistic_time = int(cost)

            
            return {
                'total_seconds': realistic_time,
                'minutes': realistic_time // 60,
                'seconds': realistic_time % 60,
                'formatted': f"{realistic_time // 60}m {realistic_time % 60}s"
            }
        else:
            print(f"Warning: No path found between {start_station_id} and {end_station_id}, using fallback")
            fallback_time = max(180, (len(segment_stations) - 1) * 120)  # 2 minutes per station as fallback
            return {
                'total_seconds': fallback_time,
                'minutes': fallback_time // 60,
                'seconds': fallback_time % 60,
                'formatted': f"{fallback_time // 60}m {fallback_time % 60}s"
            }
    except (ValueError, IndexError) as e:
        print(f"Error calculating RER duration: {e}")
        fallback_time = max(180, (len(segment_stations) - 1) * 120)
        return {
            'total_seconds': fallback_time,
            'minutes': fallback_time // 60,
            'seconds': fallback_time % 60,
            'formatted': f"{fallback_time // 60}m {fallback_time % 60}s"
        }

def get_station_name_from_id(station_id, all_metro_info, rer_stop_data):
    """
    Get station name from ID, checking both metro and RER data
    """
    # Check metro data first
    for triplet in all_metro_info:
        if triplet[0] == station_id:
            return triplet[1]
    
    # Check RER data
    for rer_stop in rer_stop_data:
        if rer_stop[0] == station_id:
            return rer_stop[1]
    
    return None

def get_station_id_from_name(station_name, all_metro_info, rer_stop_data):
    """
    Get station IDs from name, checking both metro and RER data.
    Note: RER station IDs are unique and don't change between lines or directions.
    """
    list_of_ids = []
    
    # Check metro data
    for triplet in all_metro_info:
        if triplet[1] == station_name and f"IDFM:{triplet[0]}" not in list_of_ids:
            list_of_ids.append(f"IDFM:{triplet[0]}")
    
    # Check RER data - each station has only one unique ID regardless of line
    for rer_stop in rer_stop_data:
        if rer_stop[1] == station_name:
            list_of_ids.append(rer_stop[0])
    
    return list_of_ids

def add_minutes_to_time_str(time_str, minutes):
    """Add minutes to a time string in HH:MM:SS format"""
    time_format = "%H:%M:%S"
    time_obj = datetime.strptime(time_str, time_format)
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime(time_format)

def add_seconds_to_time_str(time_str, seconds):
    """Add seconds to a time string in HH:MM:SS format"""
    time_format = "%H:%M:%S"
    time_obj = datetime.strptime(time_str, time_format)
    new_time = time_obj + timedelta(seconds=seconds)
    return new_time.strftime(time_format)

def list_of_trajet_names(line_type, line_id, depart_name, all_metro_info, rer_stop_data, actual_time, trajects_per_metro, rer_trajects, rer_filtered_trips, destination_name=None):
    """
    Find available trajets/trips for a given line type and departure station
    """
    lists = []
    
    if line_type == 'metro':
        metro_name = f"Metro :{line_id}"
        # Find all station IDs with this name
        station_ids = get_station_id_from_name(depart_name, all_metro_info, rer_stop_data)
        
        # If destination is provided, get its IDs too
        destination_ids = []
        if destination_name:
            destination_ids = get_station_id_from_name(destination_name, all_metro_info, rer_stop_data)
        
        for station_id in station_ids:
            # Check if this station belongs to the metro line
            for triplet in all_metro_info:
                if triplet[0] == station_id.replace("IDFM:", "") and triplet[2] == line_id:
                    # For each destination ID, try to find a trajet that connects both stations
                    if destination_ids:
                        for dest_id in destination_ids:
                            trajet_info = search_nearest_time_trajet(actual_time, station_id, metro_name, trajects_per_metro, dest_id)
                            if len(trajet_info) > 0 and trajet_info[0] == metro_name:
                                lists.append(trajet_info)
                                break  # Found a valid trajet for this start station
                    else:
                        # No destination specified, use original logic
                        trajet_info = search_nearest_time_trajet(actual_time, station_id, metro_name, trajects_per_metro)
                        if len(trajet_info) > 0 and trajet_info[0] == metro_name:
                            lists.append(trajet_info)
                    break
    
    elif line_type == 'rer':
        # Map RER line letter to IDFM route ID
        from app.functions.reads_and_pickles import read_RER_lines
        rer_lines = read_RER_lines()
        target_rer_route_id = None
        for line_info in rer_lines:
            if line_info[2] == line_id:  # line_info[2] is the RER letter (A, B, C, D, E)
                target_rer_route_id = line_info[0]  # line_info[0] is the IDFM route ID
                break
        
        if not target_rer_route_id:
            print(f"Warning: Could not find route ID for RER line {line_id}")
            return lists
        
        # Find all station IDs with this name
        station_ids = get_station_id_from_name(depart_name, all_metro_info, rer_stop_data)
        
        # If destination is provided, get its IDs too
        destination_ids = []
        if destination_name:
            destination_ids = get_station_id_from_name(destination_name, all_metro_info, rer_stop_data)
        
        for station_id in station_ids:
            # Check if this station belongs to the RER line
            for rer_stop in rer_stop_data:
                if rer_stop[0] == station_id:
                    # If destination is specified, try to find trips that connect both stations
                    if destination_ids:
                        for dest_id in destination_ids:
                            trip_info = search_nearest_time_rer_trip(actual_time, station_id, target_rer_route_id, rer_trajects, rer_filtered_trips, dest_id)
                            if len(trip_info) > 0:
                                lists.append(trip_info)
                                break  # Found a valid trip for this start station
                    else:
                        # No destination specified, use original logic
                        trip_info = search_nearest_time_rer_trip(actual_time, station_id, target_rer_route_id, rer_trajects, rer_filtered_trips)
                        if len(trip_info) > 0:
                            lists.append(trip_info)
                    break
    
    return lists

def select_correct_trajet_by_direction(lists, first_station_name, last_station_name, all_metro_info, rer_stop_data, line_type, line_id, trajects_per_metro, rer_trajects):
    """
    Select the correct trajet/trip based on station order direction
    """
    if not lists:
        return None
    
    # Get station IDs for first and last stations
    first_station_ids = get_station_id_from_name(first_station_name, all_metro_info, rer_stop_data)
    last_station_ids = get_station_id_from_name(last_station_name, all_metro_info, rer_stop_data)

    

    for line in lists:
        if line_type == 'metro':
            metro_name = line[0]
            trajet_name = line[1]

            # Get the trajet stops
            trajet_stops = trajects_per_metro[metro_name][trajet_name]
            stop_ids_in_order = [stop[7] for stop in trajet_stops]
            
        elif line_type == 'rer':
            rer_route_id = line[0]  # This is the IDFM route ID (e.g., 'IDFM:C01743')
            trip_name = line[1]
            
            # Handle synthetic trips
            if trip_name.startswith("Trip: SYNTHETIC_"):
                # For synthetic trips, we'll just return it as valid since it's a fallback
                return {
                    'ligne_info': line,
                    'first_station_id': first_station_ids[0] if first_station_ids else None,
                    'last_station_id': last_station_ids[0] if last_station_ids else None,
                    'trajet_name': trip_name,
                    'line_name': rer_route_id,
                    'line_type': line_type
                }
            
            # Get the trip stops for real trips
            if rer_route_id not in rer_trajects or trip_name not in rer_trajects[rer_route_id]:
                continue  # Skip this trip if it doesn't exist
                
            trip_stops = rer_trajects[rer_route_id][trip_name]
            stop_ids_in_order = [stop[3] for stop in trip_stops]
        
        
        # Check if this trajet/trip contains both stations in the correct order
        for first_id in first_station_ids:
            for last_id in last_station_ids:
                if first_id in stop_ids_in_order and last_id in stop_ids_in_order:

                    first_index = stop_ids_in_order.index(first_id)
                    
                    last_index = stop_ids_in_order.index(last_id)
                    first_index_name = next((stop[1] for stop in all_metro_info if stop[0] == first_id.replace("IDFM:", "")), None)
                    last_index_name = next((stop[1] for stop in all_metro_info if stop[0] == last_id.replace("IDFM:", "")), None)
                   


                    if [first_station_name, last_station_name] == [first_index_name, last_index_name] and first_index < last_index:
                        return {
                            'ligne_info': line,
                            'first_station_id': first_id,
                            'last_station_id': last_id,
                            'trajet_name': trajet_name if line_type == 'metro' else trip_name,
                            'line_name': metro_name if line_type == 'metro' else rer_route_id,
                            'line_type': line_type
                        }
    
    # If no trajet matches the correct direction, return the first one as fallback
    return {
        'ligne_info': lists[0],
        'first_station_id': None,
        'last_station_id': None,
        'trajet_name': lists[0][1],
        'line_name': lists[0][0],
        'line_type': line_type
    }

def get_transfer_time_enhanced(station_name, from_line, to_line, from_line_type, to_line_type, all_metro_info, rer_stop_data, complete_data):
    """
    Calculate transfer time between different lines (metro-metro, metro-rer, rer-rer)
    """
    if from_line == to_line and from_line_type == to_line_type:
        return 0  # No transfer needed if same line
    
    # Get station IDs for both lines at this station
    from_line_ids = []
    to_line_ids = []
    
    # Handle different line types
    if from_line_type == 'metro':
        for triplet in all_metro_info:
            if triplet[1] == station_name and triplet[2] == from_line:
                from_line_ids.append(triplet[0])
    elif from_line_type == 'rer':
        for rer_stop in rer_stop_data:
            if rer_stop[1] == station_name:
                from_line_ids.append(rer_stop[0])
    
    if to_line_type == 'metro':
        for triplet in all_metro_info:
            if triplet[1] == station_name and triplet[2] == to_line:
                to_line_ids.append(triplet[0])
    elif to_line_type == 'rer':
        for rer_stop in rer_stop_data:
            if rer_stop[1] == station_name:
                to_line_ids.append(rer_stop[0])
    
    # Look for transfer time in complete_data
    for from_id in from_line_ids:
        for to_id in to_line_ids:
            # Check both directions since connections are symmetric
            for connection in complete_data:
                if (connection[0] == from_id and connection[1] == to_id) or \
                   (connection[0] == to_id and connection[1] == from_id):
                    return int(connection[2])
    
    # If no specific transfer time found, return default transfer time based on line types
    if from_line_type != to_line_type:
        # Metro-RER or RER-Metro transfers typically take longer
        default_time = 180  # 3 minutes
    else:
        # Same type transfers
        default_time = 120  # 2 minutes
    
    print(f"Warning: No transfer time found between {from_line_type} {from_line} and {to_line_type} {to_line} at {station_name}, using default {default_time}s")
    return default_time

def calculate_total_realistic_duration_enhanced(paths, actual_time, all_metro_info, trajects_per_metro, rer_stop_data, rer_trajects, rer_filtered_trips, complete_data, list_of_trajet, edges, all_station_ids, id_to_index):
    """
    Calculate realistic duration for a complete journey including metro and RER with wheelchair accessibility
    Returns: dictionary with realistic timing and accessibility info
    """
    total_seconds = 0
    current_time = actual_time
    previous_line = None
    previous_line_type = None
    
    # Keep the same stations structure from paths
    result_stations = paths['stations'].copy()
    accessibility_info = []
    
    for i, segment_dict in enumerate(paths['stations']):
        # Extract line info from segment
        line_key = list(segment_dict.keys())[0]
        stations = segment_dict[line_key]
        
        # Determine line type and extract line info
        if line_key.startswith("Metro"):
            line_type = 'metro'
            line_display = line_key.replace("Metro ", "")
            if line_display == '3bis':
                line_id = 15
            elif line_display == '7bis':
                line_id = 16
            else:
                line_id = int(line_display)
        elif line_key.startswith("RER"):
            line_type = 'rer'
            line_id = line_key.replace("RER ", "")
        else:
            continue
        
        first_station_name = stations[0]['station']
        last_station_name = stations[-1]['station']
        
        # Check accessibility for this segment
        segment_accessible = all(station.get('wheelchair_accessible', 0) == 1 for station in stations)
        accessibility_info.append({
            'line': line_key,
            'accessible': segment_accessible,
            'first_station': first_station_name,
            'last_station': last_station_name
        })
        

        
        # Find available trajets/trips
        lists = list_of_trajet_names(line_type, line_id, first_station_name, all_metro_info, rer_stop_data, current_time, trajects_per_metro, rer_trajects, rer_filtered_trips, last_station_name)

        
        if not lists:
            print(f"Warning: No {line_type} options found for {line_key} from {first_station_name}")
            continue
        

        # Select the correct trajet/trip based on direction
        selected_option = select_correct_trajet_by_direction(lists, first_station_name, last_station_name, all_metro_info, rer_stop_data, line_type, line_id, trajects_per_metro, rer_trajects)
        
        if not selected_option:
            print(f"Warning: No suitable {line_type} option found for {line_key}")
            continue
        
        ligne = selected_option['ligne_info']
        trajet_name = selected_option['trajet_name']
        line_name = selected_option['line_name']
        depart_time = ligne[2][5] if line_type == 'metro' else ligne[2][2]  # Different time format for RER
        
        # Calculate wait time based on line type
        if line_type == 'rer':
            # For RER, use more reasonable wait times to match previous implementation behavior
            if not trajet_name.startswith("Trip: SYNTHETIC_"):
                # Real RER trip - but cap wait time to maintain consistency with previous results
                wait_time_seconds = time_difference_seconds(depart_time, current_time)
                if wait_time_seconds <= 0:
                    # If trip already departed, assume next trip in 10 minutes (typical RER frequency)
                    wait_time_seconds = 600  # 10 minutes

                elif wait_time_seconds > 600:  # More than 10 minutes - cap to maintain previous behavior
                    # Cap at 10 minutes to match previous implementation behavior
                    wait_time_seconds = 600  # 10 minutes max
                else:
                    pass  # Wait time is within acceptable range

            else:
                # Synthetic RER trip - use fixed reasonable wait time
                wait_time_seconds = 600  # 10 minutes for synthetic trips
        else:
            wait_time_seconds = time_difference_seconds(depart_time, current_time)
            # Handle case where wait time is negative (trip already departed) or zero
            if wait_time_seconds <= 0:
                # If negative, assume this is the next day service + add penalty time
                if wait_time_seconds < 0:
                    # Assume it's next day, so add 24 hours and recalculate
                    wait_time_seconds = 24 * 3600 + wait_time_seconds
                else:
                    # If exactly 0, assume minimal wait time
                    wait_time_seconds = 30  # 30 seconds minimal wait
            else:
                pass  # Wait time is positive and reasonable
            
            # Cap extremely long wait times (more than 1 hour suggests data issue)
            if wait_time_seconds > 3600:
                wait_time_seconds = 1200  # 20 minutes max
        
        # Use the selected station IDs for metro calculations only
        # For RER, we use the Yen algorithm directly on the segment
        if line_type == 'metro':
            if selected_option['first_station_id'] and selected_option['last_station_id']:
                depart_id = selected_option['first_station_id']
                arrivee_id = selected_option['last_station_id']
            else:
                # Fallback to finding station IDs for metro
                depart_ids = get_station_id_from_name(first_station_name, all_metro_info, rer_stop_data)
                arrivee_ids = get_station_id_from_name(last_station_name, all_metro_info, rer_stop_data)
                depart_id = depart_ids[0] if depart_ids else None
                arrivee_id = arrivee_ids[0] if arrivee_ids else None
            
            if not depart_id or not arrivee_id:
                print(f"Warning: Could not find station IDs for metro {first_station_name} or {last_station_name}")
                continue
        
        try:
            # Calculate duration based on line type
            if line_type == 'metro':
                duree_info = calculate_partial_duration(trajet_name, depart_id, arrivee_id, line_name, current_time, trajects_per_metro)
            else:  # RER - use Yen algorithm directly on the station segment
                duree_info = calculate_partial_rer_duration_realistic(stations, edges, all_station_ids, id_to_index)
            
            if duree_info['total_seconds'] >= 0 and wait_time_seconds >= 0:
                total_segment_time = duree_info['total_seconds'] + wait_time_seconds
                
                # Add transfer time if changing lines (except for the first segment)
                transfer_time_added = 0
                if i > 0:  # Not the first segment, so we have a transfer
                    # Get previous segment info
                    prev_segment_dict = paths['stations'][i - 1]
                    prev_line_key = list(prev_segment_dict.keys())[0]
                    
                    # Determine previous line type and ID
                    if prev_line_key.startswith("Metro"):
                        prev_line_type = 'metro'
                        prev_line_display = prev_line_key.replace("Metro ", "")
                        if prev_line_display == '3bis':
                            prev_line_id = 15
                        elif prev_line_display == '7bis':
                            prev_line_id = 16
                        else:
                            prev_line_id = int(prev_line_display)
                    elif prev_line_key.startswith("RER"):
                        prev_line_type = 'rer'
                        prev_line_id = prev_line_key.replace("RER ", "")
                    
                    # Check if we're changing lines
                    if line_id != prev_line_id or line_type != prev_line_type:
                        transfer_time_added = get_transfer_time_enhanced(first_station_name, prev_line_id, line_id, prev_line_type, line_type, all_metro_info, rer_stop_data, complete_data)
                        total_segment_time += transfer_time_added
                
                best_option = {
                    'wait_time_seconds': wait_time_seconds,
                    'travel_time_seconds': duree_info['total_seconds'],
                    'transfer_time_seconds': transfer_time_added,
                    'total_segment_seconds': total_segment_time,
                    'departure_time': depart_time,
                    'line_type': line_type,
                    'accessible': segment_accessible
                }
                
                # Process the option immediately
                total_seconds += best_option['total_segment_seconds']
                
                # Update current_time for next segment
                current_time = add_seconds_to_time_str(current_time, best_option['total_segment_seconds'])
                
                # Update for next iteration
                previous_line = line_id
                previous_line_type = line_type
                
            else:
                print(f"Warning: Invalid times calculated for {line_key}")
                continue
                
        except ValueError as e:
            print(f"Error calculating duration: {e}")
            continue
    
    total_minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60
    
    # Check overall accessibility
    overall_accessible = all(segment['accessible'] for segment in accessibility_info)
    
    return {
        'total_time': f"{total_minutes} minutes and {remaining_seconds} seconds",
        'stations': result_stations,
        'wheelchair_accessible': overall_accessible,
        'accessibility_details': accessibility_info,
        'total_seconds': total_seconds
    }

def calculate_total_realistic_duration_with_details(paths, actual_time, all_metro_info, trajects_per_metro, rer_stop_data, rer_trajects, rer_filtered_trips, complete_data, list_of_trajet, edges, all_station_ids, id_to_index):
    """
    Calculate realistic duration and return detailed timing breakdown for frontend use.
    Returns both the timing summary and detailed segment information.
    """
    total_seconds = 0
    current_time = actual_time
    previous_line = None
    previous_line_type = None
    
    # Keep the same stations structure from paths
    result_stations = paths['stations'].copy()
    accessibility_info = []
    segment_details = []  # New: detailed timing per segment
    
    for i, segment_dict in enumerate(paths['stations']):
        # Extract line info from segment
        line_key = list(segment_dict.keys())[0]
        stations = segment_dict[line_key]
        
        # Determine line type and extract line info
        if line_key.startswith("Metro"):
            line_type = 'metro'
            line_display = line_key.replace("Metro ", "")
            if line_display == '3bis':
                line_id = 15
            elif line_display == '7bis':
                line_id = 16
            else:
                line_id = int(line_display)
        elif line_key.startswith("RER"):
            line_type = 'rer'
            line_id = line_key.replace("RER ", "")
        else:
            continue
        
        first_station_name = stations[0]['station']
        last_station_name = stations[-1]['station']
        
        # Check accessibility for this segment
        segment_accessible = all(station.get('wheelchair_accessible', 0) == 1 for station in stations)
        accessibility_info.append({
            'line': line_key,
            'accessible': segment_accessible,
            'first_station': first_station_name,
            'last_station': last_station_name
        })
        
        # Find available trajets/trips
        lists = list_of_trajet_names(line_type, line_id, first_station_name, all_metro_info, rer_stop_data, current_time, trajects_per_metro, rer_trajects, rer_filtered_trips, last_station_name)

        
        if not lists:
            print(f"Warning: No {line_type} options found for {line_key} from {first_station_name}")
            continue
        

        # Select the correct trajet/trip based on direction
        selected_option = select_correct_trajet_by_direction(lists, first_station_name, last_station_name, all_metro_info, rer_stop_data, line_type, line_id, trajects_per_metro, rer_trajects)
        
        if not selected_option:
            print(f"Warning: No suitable {line_type} option found for {line_key}")
            continue
        
        ligne = selected_option['ligne_info']
        trajet_name = selected_option['trajet_name']
        line_name = selected_option['line_name']
        depart_time = ligne[2][5] if line_type == 'metro' else ligne[2][2]  # Different time format for RER
        
        # Calculate wait time based on line type
        if line_type == 'rer':
            # For RER, use more reasonable wait times to match previous implementation behavior
            if not trajet_name.startswith("Trip: SYNTHETIC_"):
                # Real RER trip - but cap wait time to maintain consistency with previous results
                wait_time_seconds = time_difference_seconds(depart_time, current_time)
                if wait_time_seconds <= 0:
                    # If trip already departed, assume next trip in 10 minutes (typical RER frequency)
                    wait_time_seconds = 600  # 10 minutes

                elif wait_time_seconds > 600:  # More than 10 minutes - cap to maintain previous behavior
                    # Cap at 10 minutes to match previous implementation behavior
                    wait_time_seconds = 600  # 10 minutes max
                else:
                    pass  # Wait time is within acceptable range

            else:
                # Synthetic RER trip - use fixed reasonable wait time
                wait_time_seconds = 600  # 10 minutes for synthetic trips
        else:
            wait_time_seconds = time_difference_seconds(depart_time, current_time)
            # Handle case where wait time is negative (trip already departed) or zero
            if wait_time_seconds <= 0:
                # If negative, assume this is the next day service + add penalty time
                if wait_time_seconds < 0:
                    # Assume it's next day, so add 24 hours and recalculate
                    wait_time_seconds = 24 * 3600 + wait_time_seconds
                else:
                    # If exactly 0, assume minimal wait time
                    wait_time_seconds = 30  # 30 seconds minimal wait
            else:
                pass  # Wait time is positive and reasonable
            
            # Cap extremely long wait times (more than 1 hour suggests data issue)
            if wait_time_seconds > 3600:
                wait_time_seconds = 1200  # 20 minutes max
        
        # Use the selected station IDs for metro calculations only
        # For RER, we use the Yen algorithm directly on the segment
        if line_type == 'metro':
            if selected_option['first_station_id'] and selected_option['last_station_id']:
                depart_id = selected_option['first_station_id']
                arrivee_id = selected_option['last_station_id']
            else:
                # Fallback to finding station IDs for metro
                depart_ids = get_station_id_from_name(first_station_name, all_metro_info, rer_stop_data)
                arrivee_ids = get_station_id_from_name(last_station_name, all_metro_info, rer_stop_data)
                depart_id = depart_ids[0] if depart_ids else None
                arrivee_id = arrivee_ids[0] if arrivee_ids else None
            
            if not depart_id or not arrivee_id:
                print(f"Warning: Could not find station IDs for metro {first_station_name} or {last_station_name}")
                continue
        
        try:
            # Calculate duration based on line type
            if line_type == 'metro':
                duree_info = calculate_partial_duration(trajet_name, depart_id, arrivee_id, line_name, current_time, trajects_per_metro)
            else:  # RER - use Yen algorithm directly on the station segment
                duree_info = calculate_partial_rer_duration_realistic(stations, edges, all_station_ids, id_to_index)
            
            if duree_info['total_seconds'] >= 0 and wait_time_seconds >= 0:
                total_segment_time = duree_info['total_seconds'] + wait_time_seconds
                
                # Add transfer time if changing lines (except for the first segment)
                transfer_time_added = 0
                if i > 0:  # Not the first segment, so we have a transfer
                    # Get previous segment info
                    prev_segment_dict = paths['stations'][i - 1]
                    prev_line_key = list(prev_segment_dict.keys())[0]
                    
                    # Determine previous line type and ID
                    if prev_line_key.startswith("Metro"):
                        prev_line_type = 'metro'
                        prev_line_display = prev_line_key.replace("Metro ", "")
                        if prev_line_display == '3bis':
                            prev_line_id = 15
                        elif prev_line_display == '7bis':
                            prev_line_id = 16
                        else:
                            prev_line_id = int(prev_line_display)
                    elif prev_line_key.startswith("RER"):
                        prev_line_type = 'rer'
                        prev_line_id = prev_line_key.replace("RER ", "")
                    
                    # Check if we're changing lines
                    if line_id != prev_line_id or line_type != prev_line_type:
                        transfer_time_added = get_transfer_time_enhanced(first_station_name, prev_line_id, line_id, prev_line_type, line_type, all_metro_info, rer_stop_data, complete_data)
                        total_segment_time += transfer_time_added
                
                # Store detailed segment information
                segment_detail = {
                    'line': line_key,
                    'from_station': first_station_name,
                    'to_station': last_station_name,
                    'wait_time_seconds': max(0, wait_time_seconds),  # Ensure never negative
                    'travel_time_seconds': max(0, duree_info['total_seconds']),  # Ensure never negative
                    'transfer_time_seconds': max(0, transfer_time_added),  # Include transfer time in this segment
                    'total_segment_seconds': duree_info['total_seconds'] + wait_time_seconds + transfer_time_added,  # Include all times
                    'departure_time': depart_time,
                    'arrival_time': add_seconds_to_time_str(current_time, duree_info['total_seconds'] + wait_time_seconds + transfer_time_added),
                    'segment_start_time': current_time,  # Time when we start this segment (including wait)
                    'segment_end_time': add_seconds_to_time_str(current_time, duree_info['total_seconds'] + wait_time_seconds + transfer_time_added),
                    'line_type': line_type,
                    'accessible': segment_accessible,
                    'segment_index': i  # Add segment index for frontend reference
                }
                segment_details.append(segment_detail)
                
                # Process the option immediately - add all times to total
                total_segment_time = duree_info['total_seconds'] + wait_time_seconds + transfer_time_added
                total_seconds += total_segment_time
                
                # Update current_time for next segment
                current_time = add_seconds_to_time_str(current_time, total_segment_time)
                
                # Update for next iteration
                previous_line = line_id
                previous_line_type = line_type
                
            else:
                print(f"Warning: Invalid times calculated for {line_key}")
                continue
                
        except ValueError as e:
            print(f"Error calculating duration: {e}")
            continue
    
    total_minutes = total_seconds // 60
    remaining_seconds = total_seconds % 60
    
    # Check overall accessibility
    overall_accessible = all(segment['accessible'] for segment in accessibility_info)
    
    return {
        'total_time': f"{total_minutes} minutes and {remaining_seconds} seconds",
        'total_seconds': total_seconds,
        'stations': result_stations,
        'wheelchair_accessible': overall_accessible,
        'accessibility_details': accessibility_info,
        'segment_details': segment_details,  # New: detailed timing per segment for frontend
        'total_wait_time': sum(seg.get('wait_time_seconds', 0) for seg in segment_details),
        'total_travel_time': sum(seg.get('travel_time_seconds', 0) for seg in segment_details),
        'total_transfer_time': sum(seg.get('transfer_time_seconds', 0) for seg in segment_details)
    }

def apply_realistic_timing_to_all_trips(trips_list, actual_time, all_metro_info, trajects_per_metro, rer_stop_data, rer_trajects, rer_filtered_trips, complete_data, list_of_trajet, edges, all_station_ids, id_to_index):
    """
    Apply realistic timing to all trips returned by calculate_path_and_time.
    Returns the same structure as the original trips but with updated timing and wait time details.
    
    Args:
        trips_list: List of trips from calculate_path_and_time
        actual_time: Starting time for the journey (HH:MM:SS format)
        all_metro_info: Metro station information
        trajects_per_metro: Metro trajectory data
        rer_stop_data: RER station data
        rer_trajects: RER trajectory data
        rer_filtered_trips: Filtered RER trips
        complete_data: Complete connection data
        list_of_trajet: List of trajectories
        edges: Graph edges
        all_station_ids: All station IDs
        id_to_index: ID to index mapping
    
    Returns:
        List of trips with same structure but realistic timing applied and wait time details
    """
    realistic_trips = []
    
    for i, trip in enumerate(trips_list):
        try:
            # Calculate realistic timing with detailed breakdown for this trip
            realistic_data = calculate_total_realistic_duration_with_details(
                trip, 
                actual_time, 
                all_metro_info, 
                trajects_per_metro, 
                rer_stop_data, 
                rer_trajects, 
                rer_filtered_trips, 
                complete_data, 
                list_of_trajet,
                edges,
                all_station_ids,
                id_to_index
            )
            
            # Create updated trip with same structure as original
            # Use the components sum for consistent timing
            components_total_seconds = realistic_data['total_wait_time'] + realistic_data['total_travel_time'] + realistic_data['total_transfer_time']
            components_minutes = components_total_seconds // 60
            components_remaining_seconds = components_total_seconds % 60
            
            updated_trip = {
                "total_time": f"{components_minutes} minutes and {components_remaining_seconds} seconds",  # Use components sum
                "stations": trip['stations']  # Keep original stations structure
            }
            
            # Add detailed timing information for frontend (including wait times)
            updated_trip['timing_details'] = {
                'realistic_total_seconds': components_total_seconds,  # Use components sum
                'wheelchair_accessible': realistic_data['wheelchair_accessible'],
                'accessibility_details': realistic_data['accessibility_details'],
                'trip_rank': i + 1,
                'total_wait_time': realistic_data['total_wait_time'],
                'total_travel_time': realistic_data['total_travel_time'],
                'total_transfer_time': realistic_data['total_transfer_time'],
                'segment_details': realistic_data['segment_details']  # Detailed timing per segment
            }
            
            realistic_trips.append(updated_trip)
            
        except Exception as e:
            print(f"Warning: Failed to calculate realistic timing for trip {i+1}: {e}")
            # If realistic timing fails, keep the original trip structure but mark it
            fallback_trip = {
                "total_time": trip['total_time'],  # Keep original time
                "stations": trip['stations']  # Keep original stations
            }
            
            # Add timing details indicating failure
            fallback_trip['timing_details'] = {
                'realistic_timing_failed': True,
                'trip_rank': i + 1,
                'wheelchair_accessible': None,
                'accessibility_details': [],
                'total_wait_time': 0,  # Ensure wait time is always present
                'total_travel_time': 0,  # Ensure travel time is always present
                'total_transfer_time': 0,  # Ensure transfer time is always present
                'segment_details': []
            }
            
            realistic_trips.append(fallback_trip)
    
    # Sort by realistic total time (shortest first)
    realistic_trips.sort(key=lambda x: x.get('timing_details', {}).get('realistic_total_seconds', float('inf')))
    
    # Update rankings after sorting
    for i, trip in enumerate(realistic_trips):
        trip['timing_details']['realistic_rank'] = i + 1
    
    return realistic_trips

def deduplicate_trips_by_route(trips):
    """
    Remove duplicate trips based on the actual route taken (sequence of lines and key stations).
    Keeps the trip with the shortest total time for each unique route.
    Also filters out trips with unrealistic line patterns.
    """
    if not trips:
        return trips
    
    def get_route_signature(trip):
        """Generate a signature for a trip based on the route taken"""
        signature = []
        
        for segment in trip.get("stations", []):
            for line_key, stations in segment.items():
                if line_key != "transfer_time":
                    # Add line and key stations (first and last of each segment)
                    if stations:
                        first_station = stations[0].get("station", "")
                        last_station = stations[-1].get("station", "")
                        signature.append((line_key, first_station, last_station))
        
        return tuple(signature)
    
    def has_line_repetition(signature):
        """Check if the route signature has the same line used multiple times"""
        seen_lines = set()
        for line_key, first_station, last_station in signature:
            if line_key in seen_lines:
                return True
            seen_lines.add(line_key)
        return False
    
    # First filter: Remove trips with line repetitions
    filtered_trips = []
    for trip in trips:
        signature = get_route_signature(trip)
        if not has_line_repetition(signature):
            filtered_trips.append(trip)
        else:
            print(f"Filtered out trip with repeated line usage: {[line_key for line_key, _, _ in signature]}")
    
    # Group remaining trips by their route signature
    route_groups = {}
    for trip in filtered_trips:
        signature = get_route_signature(trip)
        if signature not in route_groups:
            route_groups[signature] = []
        route_groups[signature].append(trip)
    
    # Keep the best trip from each group (shortest time)
    deduplicated_trips = []
    for signature, group_trips in route_groups.items():
        if len(group_trips) == 1:
            deduplicated_trips.append(group_trips[0])
        else:
            # Find the trip with shortest total time
            best_trip = min(group_trips, key=lambda t: parse_total_time(t.get("total_time", "0 minutes and 0 seconds")))
            deduplicated_trips.append(best_trip)
    
    return deduplicated_trips

def parse_total_time(time_str):
    """Parse time string to get total seconds for comparison"""
    try:
        # Handle formats like "15 minutes and 30 seconds" or "0 min 45 sec"
        time_str = time_str.lower()
        minutes = 0
        seconds = 0
        
        if "minute" in time_str:
            parts = time_str.split("minute")
            if parts[0].strip():
                minutes = int(parts[0].strip().split()[-1])
        elif "min" in time_str:
            parts = time_str.split("min")
            if parts[0].strip():
                minutes = int(parts[0].strip().split()[-1])
        
        if "second" in time_str:
            parts = time_str.split("second")
            if len(parts) > 1:
                sec_part = parts[0].split()[-1]
                if "and" in sec_part:
                    sec_part = sec_part.split("and")[-1].strip()
                seconds = int(sec_part)
        elif "sec" in time_str:
            parts = time_str.split("sec")
            if len(parts) > 1:
                sec_part = parts[0].split()[-1]
                seconds = int(sec_part)
        
        return minutes * 60 + seconds
    except:
        return 0

def calculate_path_and_time_with_realistic_timing(start_id, end_id, edges, metro_info, all_station_ids, id_to_index, rer_stop_data, rer_with_line, actual_time="8:30:00", complete_data=None, trajects_per_metro=None, rer_trajects=None, rer_filtered_trips=None, list_of_trajet=None):
    """
    Convenience function that combines path calculation with realistic timing.
    Returns trips in the same format as calculate_path_and_time but with realistic timing.
    
    Args:
        start_id: Starting station index
        end_id: Ending station index
        edges: Graph edges
        metro_info: Metro station information
        all_station_ids: All station IDs
        id_to_index: ID to index mapping
        rer_stop_data: RER station data
        rer_with_line: RER station data with line information
        actual_time: Starting time for the journey (HH:MM:SS format)
        complete_data: Complete connection data
    
    Returns:
        List of trips with realistic timing applied, same structure as calculate_path_and_time
    """
    # First, get all possible paths using Dijkstra
    original_trips = calculate_path_and_time(
        start_id, end_id, edges, metro_info, all_station_ids, 
        id_to_index, rer_stop_data, rer_with_line, complete_data
    )
    
    if not original_trips:
        return []
    
    # Apply realistic timing to all trips
    realistic_trips = apply_realistic_timing_to_all_trips(
        original_trips,
        actual_time,
        metro_info,
        trajects_per_metro,
        rer_stop_data,
        rer_trajects,
        rer_filtered_trips,
        complete_data,
        list_of_trajet,
        edges,
        all_station_ids,
        id_to_index
    )
    
    # Deduplicate trips based on route taken
    deduplicated_trips = deduplicate_trips_by_route(realistic_trips)
    
    return deduplicated_trips

def has_unrealistic_line_pattern(path, index_to_id, metro_info, rer_with_line):
    """
    Check if a path has unrealistic line patterns, such as:
    - Taking the same metro/RER line multiple times (e.g., Metro 6 -> Metro 4 -> Metro 6)
    - Excessive line changes for short distances
    """
    if len(path) < 3:
        return False
    
    # Create info mappings
    metro_id_to_line = {id: line for id, name, line, wheelchair in metro_info}
    
    # Create RER line mapping
    rer_id_to_lines = {}
    for id, name, line_name, wheelchair in rer_with_line:
        if id not in rer_id_to_lines:
            rer_id_to_lines[id] = set()
        rer_id_to_lines[id].add(line_name)
    
    # Track the sequence of lines used
    line_sequence = []
    prev_line_info = None
    
    for idx in path:
        stop_id = index_to_id[idx]
        current_line_info = None
        
        # Determine line for this station
        if stop_id in metro_id_to_line:
            line = metro_id_to_line[stop_id]
            # Map special metro lines
            if line == 15:
                line_display = '3bis'
            elif line == 16:
                line_display = '7bis'
            else:
                line_display = str(line)
            current_line_info = ('metro', line_display)
            
        elif stop_id in rer_id_to_lines:
            # For RER, we need to determine which line is being used
            # Use the first line available (could be improved with context)
            rer_lines = list(rer_id_to_lines[stop_id])
            if rer_lines:
                current_line_info = ('rer', rer_lines[0])
        
        # Add to sequence if it's a new line or line type
        if current_line_info and current_line_info != prev_line_info:
            line_sequence.append(current_line_info)
            prev_line_info = current_line_info
    
    # Check for unrealistic patterns
    if len(line_sequence) < 2:
        return False
    
    # Pattern 1: Same line used multiple times (A -> B -> A pattern)
    seen_lines = set()
    for line_info in line_sequence:
        line_key = f"{line_info[0]}_{line_info[1]}"
        
        seen_lines.add(line_key)
    
    # Pattern 2: Too many line changes for short paths
    if len(line_sequence) > 4 and len(path) < 15:
        print(f"Unrealistic pattern detected: {len(line_sequence)} line changes for only {len(path)} stations")
        return True
    
    # Pattern 3: Excessive transfers (more than 4 line changes total)
    if len(line_sequence) > 5:
        print(f"Unrealistic pattern detected: Too many transfers ({len(line_sequence)} lines)")
        return True
    
    return False
