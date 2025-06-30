from pathlib import Path

filepath = Path(__file__).parent.parent / "v1_text_files" / "metro.txt"
filepath = filepath.resolve()

def read_metro_data(filepath :str):
    start_line = 16
    with open(filepath, "r", encoding="utf-8") as f:
        vertices = []
        edges = []
        for i, line in enumerate(f, 1):
            if i >= start_line:
                if line[0] =="V":
                    state_and_id = line[:6]
                    state_and_id = state_and_id.split()

                    station_and_line = line[7:]
                    station_and_line = station_and_line.split(";")
                    conections = station_and_line[2].replace('\n',"")
                    station_and_line.pop(2)
                    station_and_line+= conections.split()
                    station_and_line[0] = station_and_line[0].strip()
                    

                    line_to_add= state_and_id+station_and_line
                    vertices.append(line_to_add)
                elif line[0] =="E":
                    line_to_add = line.split()
                    edges.append(line_to_add)
    n = len(vertices)
    adjency_matrix = [[0 for _ in range(n)] for _ in range(n)]
    edges_not_symetric = ((145,373),(201,145),(259,36),(36,198),(34,248),(248,280),(280,92),(92,34))

    for edge in edges:        
        i, j, w = int(edge[1]), int(edge[2]), int(edge[3])
        adjency_matrix[i][j] = w
        if (i,j) not in edges_not_symetric:
            adjency_matrix[j][i] = w 
    
    return adjency_matrix, vertices, edges

metro_data = read_metro_data(filepath)
    
def dijkstra_algo_with_path(matrix :list, start: int):
    n = len(matrix)
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
            if matrix[u][v] > 0 and not visited[v]:
                if dist[u] + matrix[u][v] < dist[v]:
                    dist[v] = dist[u] + matrix[u][v]
                    prev[v] = u  

    return dist, prev

def get_path(prev : list, target: int):
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    return path[::-1]  

def calculate_path_and_time(index_start: int, index_finish: int):
    global metro_data
    matrix, vertices, edges = metro_data #read_metro_data(filepath)
    dist, prev = dijkstra_algo_with_path(matrix, start=index_start)
    path = get_path(prev, index_finish)

    # Group stations by metro line
    stations_by_line = {}
    for station_idx in path:
        station = vertices[station_idx]
        line = station[3]
        key = f"Metro {line}"
        station_info = {
            "id": station[1],
            "station": station[2]
        }
        if key not in stations_by_line:
            stations_by_line[key] = []
        stations_by_line[key].append(station_info)

    # Convert to desired list-of-dicts format
    stations_list = [{line: stations} for line, stations in stations_by_line.items()]

    return {
        "total_time": f"{int(dist[index_finish] // 60)} minutes and {int(dist[index_finish] % 60)} seconds",
        "stations": stations_list
    }

def display_ids():
    global metro_data
    matrix, vertices, edges = metro_data #read_metro_data(filepath)
    json_list_return = {}
    json_list_return["stations"] = []
    for station in vertices:
        json_list_return["stations"].append({
            "id": station[1],
            "station": station[2],
            "line": station[3]
        })
    return json_list_return

def display_specific_metro_stations(Metro_line):
    global metro_data
    matrix, vertices, edges = metro_data #read_metro_data(filepath)
    json_list_return = {}
    json_list_return["metro_line"] = Metro_line
    
    metro_stations_list = []
    terminus_ids =[]
    for station in vertices:
        if station[3].strip() == str(Metro_line).strip():
            metro_stations_list.append(station)
            if station[4] == "True":
                terminus_ids.append(station[1]) 
    
    json_list_return["stations"] = calculate_path_and_time(int(terminus_ids[0]),int(terminus_ids[1]))
    return json_list_return

def calculate_degree_of_station(station_id: int):
    """
    Fonction qui retourne le degré d'une station de métro
    ------------------
    return format:
        <degree (int)>
    """
    global metro_data
    matrix, vertices, edges = metro_data
    degree = 0
    for i in range(len(matrix)):
        if matrix[station_id][i] > 0:
            degree += 1
    return degree

def get_station_output(station_id: int):
    """
    Fonction qui retourne les sorties d'une station de métro
    ------------------
    return format:
    {
        <station_id (int)>: <is_outside_line (bool)>
    }
    """
    global metro_data
    matrix, vertices, edges = metro_data
    better_vertices = {int(v[1]): v[2:] for v in vertices}
    station_outputs = {}
    for edge in edges:
        if int(edge[1]) == station_id or int(edge[2]) == station_id:
            other_station_id = int(edge[2]) if int(edge[1]) == station_id else int(edge[1])
            is_outside_line = better_vertices[other_station_id][1] == better_vertices[station_id][1]
            station_outputs[other_station_id] = is_outside_line
    return station_outputs


def stations_position():
    """
    Fonction qui retourne la position des stations de métro du fichier pospoints.txt
    ------------------
    return format:
    { 
        <metro line number (str)> : 
        {
            <Nom de la station (str)> : 
            {
                id: <station_id (int)>,
                x: <pos_x (int)>, 
                y: <pos_y (int)>,
                it: <number_of_iteration (int)>,
                out: 
                {
                    <station_id (int)>: <is_outside_line (bool)>
                },
                d: <degree (int)>
            }
        }
    }
    """
    json_station_positions = {}
    global metro_data
    matrix, vertices, edges = metro_data
    filepath = Path(__file__).parent.parent / "v1_text_files" / "pospoints.txt"
    filepath = filepath.resolve()
    t = str.maketrans({"@": " ", '\n': ''})
    with open(filepath, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            station_id, metro_line, pos_x, pos_y, station = line.split(';')
            station_id = int(station_id)
            station = station.translate(t)
            if metro_line not in json_station_positions:
                json_station_positions[metro_line] = {}
            json_station_positions[metro_line][station] = {"id": station_id, 'x': int(pos_x), 'y': int(pos_y), 'it': 1, 'out': get_station_output(station_id), 'd': calculate_degree_of_station(station_id)}
    return json_station_positions