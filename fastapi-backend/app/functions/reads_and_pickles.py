import os
import pickle

# Ensure the pickle directory exists
PICKLE_DIR = os.path.join(os.path.dirname(__file__), "container_pkl_files")
os.makedirs(PICKLE_DIR, exist_ok=True)

# Define the base path for V2 text files
V2_TEXT_FILES_DIR = os.path.join(os.path.dirname(__file__), "..", "V2_text_files")

def get_pickle_path(filename):
    """Helper function to get the full path for pickle files"""
    return os.path.join(PICKLE_DIR, filename)

def get_v2_file_path(filename):
    """Helper function to get the full path for V2 text files"""
    return os.path.join(V2_TEXT_FILES_DIR, filename)

def read_all_stops_times_and_save():
    ratp_data = []
    pathfile = get_v2_file_path("stop_times.txt")
    
    with open(pathfile, "r") as f:
        for i, line in enumerate(f, 1):
            if i > 1 and "IDFM:RATP" in line:  
                separate_commas = line.strip().split(",")
                separate_2_points = separate_commas[0].split(":")
                get_id = separate_2_points[2].split("-")
                line_combined = separate_2_points[:2] + get_id + separate_commas[1:]
                ratp_data.append(line_combined)
    
    pkl_file = get_pickle_path("ratp_data.pkl")
    with open(pkl_file, "wb") as f:
        pickle.dump(ratp_data, f)

def load_ratp_data():
    pkl_file = get_pickle_path("ratp_data.pkl")
    if not os.path.exists(pkl_file) or os.path.getsize(pkl_file) == 0:
        print("ratp_data.pkl not found or empty. Creating it...")
        read_all_stops_times_and_save()
    with open(pkl_file, "rb") as f:
        ratp_data = pickle.load(f)
    return ratp_data

def read_and_save_stops():
    pathfile = get_v2_file_path("stops.txt")
    data = []
    pkl_file = get_pickle_path("stop_data.pkl")
    if not os.path.exists(pkl_file) or os.path.getsize(pkl_file) == 0:
        print("stop_data.pkl not found or empty. Creating it...")
        with open(pathfile,"r", encoding="utf-8") as f:
            for i, line in enumerate(f,1):
                if i>1:
                    line_to_Add = line.strip().split(",")
                    # Remove empty strings but keep the original structure for indexing
                    id = line_to_Add[0].split(":")[-1]
                    stop_name = line_to_Add[2] if len(line_to_Add) > 2 else ""
                    # Get wheelchair accessibility (index 12), default to 0 if not present
                    wheelchair_boarding = line_to_Add[12] if len(line_to_Add) > 12 and line_to_Add[12] != '' else '0'
                    
                    # Convert wheelchair_boarding to int, handle any conversion errors
                    try:
                        wheelchair_int = int(wheelchair_boarding)
                    except ValueError:
                        wheelchair_int = 0
                    
                    line_to_Add = [id, stop_name, wheelchair_int]
                    data.append(line_to_Add)
        ratp_data = data
        with open(pkl_file, "wb") as f:
           pickle.dump(ratp_data, f)
    else:
        with open(pkl_file, "rb") as f:
            ratp_data = pickle.load(f)
    return ratp_data

#Metro transfers
# This function reads the transfers.txt file and filters the transfers based on metro station IDs.

def read_transfers(metro_stations_id, rer_stop_data=None):
    pathfile = get_v2_file_path("transfers.txt")
    data = []
    
    # Create a combined set of all station IDs (metro + RER)
    all_station_ids = set(metro_stations_id)
    if rer_stop_data:
        rer_ids = {stop[0] for stop in rer_stop_data}  # Extract RER station IDs
        all_station_ids.update(rer_ids)
    
    with open(pathfile, "r") as f:
        for i, line in enumerate(f, 1):
            if i > 1:
                separate_commas = line.strip().split(",")
                separate_2_points_array = []

                for item in separate_commas[:2]:
                    separate_2_points_array.append(item.split(":"))
                
                # Extract station IDs from the transfer data
                station_id1 = separate_2_points_array[0][len(separate_2_points_array[0])-1]
                station_id2 = separate_2_points_array[1][len(separate_2_points_array[1])-1]
                
                # Check if both stations are in our combined list (metro + RER)
                if station_id1 in all_station_ids and station_id2 in all_station_ids:
                    line_to_add = [station_id1, station_id2, separate_commas[3]]
                    data.append(line_to_add)
    return data

# This function reads the RER lines from the routes.txt file and filters them based on specific criteria.

#RER read
# This function reads the RER lines from the routes.txt file and filters them based on specific

def read_RER_lines():
    rer_data = []
    pathfile = get_v2_file_path("routes.txt")
    with open(pathfile, "r") as f:
        for i, line in enumerate(f, 1):
             
            separate_commas = line.strip().split(",")
            if separate_commas[1] =="IDFM:71" and separate_commas[0].startswith("IDFM:C017"):
                rer_data.append(separate_commas[0:3])
          
    return rer_data

def get_RER_trips():
    rer_trips_per_RER = {}
    rer_lines = read_RER_lines()
    for line in rer_lines:
        rer_trips_per_RER[line[0]] = []
    
    pathfile = get_v2_file_path("trips.txt")
    with open(pathfile, "r") as f:
        for i, line in enumerate(f, 1):
            
            separate_commas = line.strip().split(",")
            if separate_commas[0] in rer_trips_per_RER.keys():
                for id in rer_trips_per_RER:
                    get_trip_id = separate_commas[2].split(":")
                    
                    trip_id = get_trip_id[3]
                    if trip_id not in rer_trips_per_RER[id] and separate_commas[0] ==id:
                        rer_trips_per_RER[id].append(trip_id)
    return rer_trips_per_RER

def get_detailed_trips_for_RER():
    pkl_file = get_pickle_path("RER_detailed_trips.pkl")
    if not os.path.exists(pkl_file):
        rer_diccio = get_RER_trips() 
        rer_traject_per_line = {route_id: {} for route_id in rer_diccio}

        trip_id_to_route = {}
        for route_id, trips in rer_diccio.items():
            for i, trip in enumerate(trips):
                trip_id_to_route[trip] = (route_id, f"Trip: {i}")

        pathfile = get_v2_file_path("stop_times.txt")
        with open(pathfile, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) < 4:
                    continue 

                trip_id = parts[0].split(":")[-1]
                arrival_time = parts[1]
                departure_time = parts[2]
                stop_id = parts[3].split(":")[-1]

                if trip_id in trip_id_to_route:
                    route_id, trip_name = trip_id_to_route[trip_id]
                    if trip_name not in rer_traject_per_line[route_id]:
                        rer_traject_per_line[route_id][trip_name] = []

                    rer_traject_per_line[route_id][trip_name].append([trip_id, arrival_time, departure_time, stop_id])
        with open(pkl_file, "wb") as f:
           pickle.dump(rer_traject_per_line, f)
    else:
        with open(pkl_file, "rb") as f:
            rer_traject_per_line = pickle.load(f)

    return rer_traject_per_line