filepath = r"Version1\metro.txt"

def read_metro_data(filepath):
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

    for edge in edges:        
        i, j, w = int(edge[1]), int(edge[2]), int(edge[3])
        adjency_matrix[i][j] = w
        adjency_matrix[j][i] = w 
    
    return adjency_matrix, vertices, edges
    
def dijkstra_algo_with_path(matrix, start):
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

def get_path(prev, target):
    path = []
    while target is not None:
        path.append(target)
        target = prev[target]
    return path[::-1]  

def calculate_path_and_time(index_start, index_finish):
    matrix, vertices, edges = read_metro_data(filepath)
    dist, prev = dijkstra_algo_with_path(matrix, start=index_start)
    target = index_finish 
    path = get_path(prev, target)
    print(f"Trip time: {int(dist[target]/60)} minutes and {dist[target]%60} seconds")
    line_to_take = []
    print(path)
    for station in path:
        if line_to_take != vertices[station][3]:
            line_to_take = vertices[station][3]
            print(f"\nMetro {line_to_take}")

        print(f"ID:{vertices[station][1]} Station: {vertices[station][2]}")

def display_ids():
    matrix, vertices, edges = read_metro_data(filepath)
    for station in vertices:
        print(f"ID:{station[1]} Station: {station[2]}")

def display_specific_metro_stations(Metro_line):
    matrix, vertices, edges = read_metro_data(filepath)
    print(f"Stations for Metro line : {Metro_line}")
    metro_stations_list = []
    terminus_ids =[]
    for station in vertices:
        if station[3].strip() == str(Metro_line).strip():
            metro_stations_list.append(station)
            if station[4] == "True":
                terminus_ids.append(station[1]) 
    calculate_path_and_time(int(terminus_ids[0]),int(terminus_ids[1]))
    
