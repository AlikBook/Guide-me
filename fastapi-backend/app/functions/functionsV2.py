import os
import pickle
from pathlib import Path
import json

BASE_DIR = Path(__file__).resolve().parent
def create_metro_ids():
    metro_lines = []
    for i in range(1,18):
        if i != 15:
            metro_lines.append("C0"+str(1370+i))
    return metro_lines

def read_all_stops_times_and_save():
    ratp_data = []
    pathfile = Path(__file__).parent.parent / "V2_text_files" / "stop_times.txt"
    pathfile = pathfile.resolve()

    with open(pathfile, "r") as f:
        for i, line in enumerate(f, 1):
            if i > 1 and "IDFM:RATP" in line:  
                separate_commas = line.strip().split(",")
                separate_2_points = separate_commas[0].split(":")
                get_id = separate_2_points[2].split("-")
                line_combined = separate_2_points[:2] + get_id + separate_commas[1:]
                ratp_data.append(line_combined)
    
    pkl_path = BASE_DIR / "container_pkl_files" / "ratp_data.pkl"
    with open(pkl_path, "wb") as f:
        pickle.dump(ratp_data, f)

def load_ratp_data():
    folder = BASE_DIR / "container_pkl_files"
    folder.mkdir(parents=True, exist_ok=True)  # Ensure folder exists

    pkl_file = folder / "ratp_data.pkl"

    if not os.path.exists(pkl_file) or os.path.getsize(pkl_file) == 0:
        print("ratp_data.pkl not found or empty. Creating it...")
        read_all_stops_times_and_save()

    with open(pkl_file, "rb") as f:
        ratp_data = pickle.load(f)

    return ratp_data


def read_and_save_stops():
    pathfile = Path(__file__).parent.parent / "V2_text_files" / "stops.txt"
    pathfile = pathfile.resolve()

    pkl_file = BASE_DIR / "container_pkl_files" / "stop_data.pkl"
    data = []

    if not os.path.exists(pkl_file) or os.path.getsize(pkl_file) == 0:
        print("stop_data.pkl not found or empty. Creating it...")
        with open(pathfile,"r", encoding="utf-8") as f:
            for i, line in enumerate(f,1):
                if i>1:
                    line_to_Add = line.strip().split(",")
                    line_to_Add = [x for x in line_to_Add if x != '']
                    id = line_to_Add[0].split(":")[-1]
                    
                    line_to_Add = [id] + [line_to_Add[1]]
                    data.append(line_to_Add)
        ratp_data = data
        with open(pkl_file, "wb") as f:
           pickle.dump(ratp_data, f)
    else:
        with open(pkl_file, "rb") as f:
            ratp_data = pickle.load(f)
    return ratp_data

def get_trajets_for_metro():

    pkl_file = BASE_DIR / "container_pkl_files" / "trajects_per_metro.pkl"

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
    pickle_file = BASE_DIR / "container_pkl_files" / "max_len_results.pkl"

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

def get_stations_id_and_name_per_metro(trajects_per_metro, list_of_trajet):
    
    pickle_file = BASE_DIR / "container_pkl_files" / "station_info_cache.pkl"
    # Return cached result if available
    if os.path.exists(pickle_file):
        with open(pickle_file, "rb") as f:
            return pickle.load(f)

    # Compute and cache result
    ratp_data = read_and_save_stops()
    metro_stop_info = []

    for stop in ratp_data:
        stop_id = stop[0]
        for i, metro_trajet in enumerate(list_of_trajet, 1):
            for idx in metro_trajet:
                key = f"Metro :{i}"
                for trajet in trajects_per_metro[key][f"Trajet {idx}"]:
                    if stop_id == trajet[7].split(":")[-1]:
                        if all(existing_id != stop_id for existing_id, *_ in metro_stop_info):
                            metro_stop_info.append((stop_id, stop[1], i))

    # Save to pickle
    with open(pickle_file, "wb") as f:
        pickle.dump(metro_stop_info, f)

    return metro_stop_info

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

def read_transfers(metro_stations_id):
    pathfile = Path(__file__).parent.parent / "V2_text_files" / "transfers.txt"
    pathfile = pathfile.resolve()
   
    data = []
    with open(pathfile, "r") as f:
        for i, line in enumerate(f, 1):
            if i > 1:
                separate_commas = line.strip().split(",")
                separate_2_points_array = []

                for item in separate_commas[:2]:
                    separate_2_points_array.append(item.split(":"))
                if(separate_2_points_array[0][len(separate_2_points_array[0])-1] in metro_stations_id and
                   separate_2_points_array[1][len(separate_2_points_array[1])-1] in metro_stations_id):
                    line_to_add = [separate_2_points_array[0][len(separate_2_points_array[0])-1]] + [separate_2_points_array[1][len(separate_2_points_array[1])-1]] + [separate_commas[3]]
                    data.append(line_to_add)
    return data

def get_unique_stops_per_line(metro_info):
    metro_stations = {}
    for stop_id, stop_name, line_n in metro_info:
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


def join_all_metro_connections(trajects_per_metro, new_list_trajet,metro_info):
    connection = get_connections_per_metro(trajects_per_metro,new_list_trajet,metro_info)
    filtered_metro_ids = get_filtered_metro_ids(connection)
    my_data = read_transfers(filtered_metro_ids)
    complete_data = connection + my_data
    return complete_data,filtered_metro_ids

def create_metro_empty_graph(metro_id, complete_data):
    n = len(metro_id)
    id_to_index = {stop_id: idx for idx, stop_id in enumerate(metro_id)}
    graph = [[0 for _ in range(n)] for _ in range(n)]

    edges_not_symetric = ((id_to_index["462958"], id_to_index["21971"]), 
(id_to_index["21982"], id_to_index["462958"]), 
(id_to_index["21988"], id_to_index["463239"]), 
(id_to_index["21974"], id_to_index["21988"]), 
(id_to_index["24686"], id_to_index["24682"]), 
(id_to_index["24687"], id_to_index["24686"]))

    for id1, id2, time in complete_data:
        if id1 in id_to_index and id2 in id_to_index:
            i = id_to_index[id1]
            j = id_to_index[id2]

            graph[i][j] = int(time)
            if (i,j) not in edges_not_symetric:
                graph[j][i] = int(time)  
    return graph

def dijstra_algorithm(graph, start):
    n = len(graph)
    visited = [False] * n
    dist = [float('inf')] * n
    prev = [None] * n
    dist[start] = 0
    
    for _ in range(n):
        min_dist = float('inf')
        u = -1
        for i in range(n):
            if not visited[i] and dist[i] < min_dist:
                min_dist = dist[i]
                u = i
        if u == -1:
            break

        visited[u] = True

        for v in range(n):
            if graph[u][v] > 0 and not visited[v]:
                if dist[u] + graph[u][v] < dist[v]:
                    dist[v] = dist[u] + graph[u][v]
                    prev[v] = u

    return dist, prev

def get_path(prev, target):
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    return path[::-1]

def calculate_path_and_time(start_id, end_id, graph, metro_info, filtered_metro_ids):
    id_to_index = {stop_id: idx for idx, stop_id in enumerate(filtered_metro_ids)}
    index_to_id = {idx: stop_id for idx, stop_id in enumerate(filtered_metro_ids)}

    if start_id not in index_to_id or end_id not in index_to_id:
        return

    index_start = start_id
    index_finish = end_id

    dist, prev = dijstra_algorithm(graph, start=index_start)
    target = index_finish
    path = get_path(prev, target)
    #print(f"Trip time: {int(dist[target]/60)} minutes and {dist[target]%60} seconds \n")

    id_to_info = {id: (name, line) for id, name, line in metro_info}

    line_to_take = []
    stations_by_line = {}

    for idx in path:
        stop_id = index_to_id[idx]
        name, line = id_to_info.get(stop_id, (stop_id, "Unknown"))
        line_to_take.append([stop_id, name, line])
        

    metro_lines = []
    for line in line_to_take:
        if line[2] not in metro_lines:
            metro_lines.append(line[2])
    
    for line_number in enumerate(metro_lines, 1):
        display_line = line_number[1]
        if line_number[1] == 15:
            display_line = '3bis'
        elif line_number[1] == 16:
            display_line = '7bis'

        key = f"Metro {display_line}"
        
        for station in line_to_take:
            if station[2] == line_number[1]:
                station_info = {
                    "id": str(id_to_index[station[0]]),
                    "station": station[1]
            }
                if key not in stations_by_line:
                    stations_by_line[key] = []
                stations_by_line[key].append(station_info)

        stations_list = [{line: stations} for line, stations in stations_by_line.items()]

    return {
        "total_time": f"{int(dist[index_finish] // 60)} minutes and {int(dist[index_finish] % 60)} seconds",
        "stations": stations_list
    }


def display_ids(metro_info,filtered_metro_ids):
    index_to_id = {idx: stop_id for idx, stop_id in enumerate(filtered_metro_ids)}
    metro_dict = {stop_id: (name, line) for stop_id, name, line in metro_info}
    json_list_return = {}

    json_list_return["stations"] = []
    
    for idx, stop_id in index_to_id.items():
        if stop_id in metro_dict:
            name, line = metro_dict[stop_id]
            
            if line == 15:
                line = "3bis"
            elif line == 16:
                line = "7bis"
            
            json_list_return["stations"].append({
                "id": str(idx),
                "station": name,
                "line": str(line)
            })
    
    return json_list_return

"""
Fonctions pour la map

"""

def stops_position() -> dict:
    """
    Fonction qui retourne les localisations des stops/stations
    ------------------
    return format:
    {
        <stop_id (int)> : 
        {
            name: <stop_name (str)>,
            lat: <stop_latitude (float)>,
            long: <stop_longitude (float)>,
            prev: <previous_stop_id (int)>,
            ligne: <stop_metro_line (int)>
        },
    }
    """

    pathfile = Path(__file__).parent.parent / "V2_text_files" / "stops.txt"
    pathfile = pathfile.resolve()

    pkl_file = BASE_DIR / "container_pkl_files" / "stop_position_data.pkl"
    return_data = {}

    if not os.path.exists(pkl_file) or os.path.getsize(pkl_file) == 0:
        print("stop_position_data.pkl not found or empty. Creating it...")
        trajects_per_metro = get_trajets_for_metro()
        list_of_trajet = get_max_len(trajects_per_metro)
        metro_info = get_stations_id_and_name_per_metro(trajects_per_metro, list_of_trajet) # [ ... , (<stop_id(int)>, <stop_name(str)>, <line_num(int)>), ...]
        concerned_stops = {stop[0]: stop[1:] for stop in metro_info}
        with open(pathfile,"r", encoding="utf-8") as f:
            for i, line in enumerate(f,1):
                if i>1:
                    line = line.strip().split(",")
                    stop_id = line[0].split(":")[-1]

                    stop_name = line[2]
                    stop_latitude = line[5]
                    stop_longitude = line[4]
                    previous_stop = line[9]
                    
                    if stop_id in concerned_stops.keys():
                        stop_metro_line = concerned_stops[stop_id][1]
                        return_data[stop_id] = {
                            "name": stop_name if stop_name != '' else "Unknown",
                            "lat": stop_latitude if stop_latitude != '' else 0,
                            "long": stop_longitude if stop_longitude != '' else 0,
                            "prev": previous_stop if previous_stop != '' else -1,
                            "line": stop_metro_line if stop_metro_line != '' else 0
                        }
        with open(pkl_file, "wb") as f:
           pickle.dump(return_data, f)
    else:
        with open(pkl_file, "rb") as f:
            return_data = pickle.load(f)
    return return_data

def lines_info(line_type_list:list =['metro']) -> dict:
    """
    Fonction qui retourne des informations utile sur toutes les lignes de transport
    ------------------
    return format:
    {
    Lines:
        {
            <line_name (str)>: 
                {
                    id: <line_id(int),
                    color: <line_color(str)>,
                    tcolor: <text_color(str)>,
                    type: <line_type_number(int)>,
                }
        }
    Types:
        {
            <line_type_number(int)>: <line_type_name(str)>
        }
    }
    """

    pathfile = Path(__file__).parent.parent / "V2_text_files" / "routes.txt"
    pathfile = pathfile.resolve()

    pkl_file = BASE_DIR / "container_pkl_files" / "routes_info_data.pkl"
    return_data = {}

    if not os.path.exists(pkl_file) or os.path.getsize(pkl_file) == 0:
        print("routes_info_data.pkl not found or empty. Creating it...")
        
        route_types = {
            "tramway": 0,
            "metro" : 1,
            "XER": 2,
            "bus": 3,
            "funiculair": 7
        }
        return_data["Lines"] = {}
        return_data["Types"] = {k: v for k, v in route_types.items() if k in line_type_list}
        route_types_inversed = {v: k for k, v in route_types.items()}

        with open(pathfile,"r", encoding="utf-8") as f:
            for i, line in enumerate(f,1):
                if i>1:
                    line = line.strip().split(",")
                    line_id = line[0].split(":")[-1][3:]
                    line_type_number = line[5]

                    if route_types_inversed[int(line_type_number)] in line_type_list:

                        line_name = line[3]
                        line_color = line[7]
                        text_color = line[8]

                        return_data["Lines"][line_name] = {"id": line_id, "color": line_color, "tcolor": text_color, "type": line_type_number}
        with open(pkl_file, "wb") as f:
           pickle.dump(return_data, f)
    else:
        with open(pkl_file, "rb") as f:
            return_data = pickle.load(f)
    
    return return_data

def geojson_loader(file_name: str) -> dict:
    """
    Fonction qui retourne le geojson passé en paramètre
    ------------------
    return format:
    <return_file (dict)>
    """
    
    pathfile = Path(__file__).parent.parent / "Geojson" / file_name
    pathfile = pathfile.resolve()

    with open(pathfile, "r", encoding="utf-8") as f:
        return_file = json.load(f)

    return return_file

def geojson_metro_filter(file: dict) -> dict:
    """
    Fonction qui retourne seulement les station/trajets geojson des métro du fichier passé en paramètre
    ------------------
    return format:
    <file (dict)>
    """
    
    feature_to_delete_ids = []
    for i, feature in enumerate(file["features"]):
        try:
            is_metro = (feature["properties"]["metro"] == 1)
        except KeyError:
            is_metro = (feature["properties"]["mode"] == "METRO")
        if not is_metro:
            feature_to_delete_ids.append(i)
    
    for i in sorted(feature_to_delete_ids, reverse=True):
        del file["features"][i]

    return file