"""Graph analysis functions for connectivity and minimum spanning tree."""

import heapq


def is_connected(graph: dict[str, dict[str, int]]):
    """Check if the graph is fully connected using DFS."""
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
    """Calculate Minimum Spanning Tree using Prim's algorithm."""
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


def convert_graph_list_to_dict(matrix, all_station_ids):
    """Convert matrix to dictionary format for analysis."""
    graph = {node_id: {} for node_id in all_station_ids}
    n = len(matrix)
    for i in range(n):
        for j in range(n):
            if matrix[i][j] > 0:
                graph[all_station_ids[i]][all_station_ids[j]] = matrix[i][j]
    return graph


def analyze_graph(matrix, all_station_ids, metro_info=None):
    """Analyze graph connectivity and compute MST."""
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


def display_ids(metro_info, all_station_ids, rer_stop_data=None, rer_with_line=None):
    """Display all station IDs and information in JSON format."""
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
