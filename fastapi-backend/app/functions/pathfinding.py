"""Core pathfinding module - delegates to specialized modules."""

import os
import sys

# Import all specialized modules
from app.functions.path_validator import check_connection, has_unrealistic_line_pattern
from app.functions.graph_builder import get_edges_and_graph_v2
from app.functions.time_calculator import (
    calculate_total_realistic_duration_with_details,
    apply_realistic_timing_to_all_trips
)
from app.functions.trajectory_selector import (
    determine_rer_line_from_context,
    search_nearest_time_trajet,
    search_nearest_time_rer_trip,
    list_of_trajet_names,
    select_correct_trajet_by_direction,
    get_transfer_time_enhanced
)
from app.functions.utils.format_utils import deduplicate_trips_by_route, parse_total_time
from app.functions.utils.station_utils import get_station_name_from_id, get_station_id_from_name
from app.functions.utils.time_utils import add_minutes_to_time_str, add_seconds_to_time_str

# Global for Yen's C implementation
HAS_YEN_WRAPPER = False

def check_yen_wrapper_available():
    """Check if yen_wrapper is available for import."""
    try:
        from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
        return True
    except ImportError:
        return False

def update_yen_wrapper_status():
    """Update the global HAS_YEN_WRAPPER status."""
    global HAS_YEN_WRAPPER
    try:
        if 'app.functions.yen_compiler.yen_wrapper' in sys.modules:
            del sys.modules['app.functions.yen_compiler.yen_wrapper']
        from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
        HAS_YEN_WRAPPER = True
        print("SUCCESS: Fast C implementation of Yen's algorithm loaded successfully")
        return True
    except ImportError:
        HAS_YEN_WRAPPER = False
        print("Warning: yen_wrapper not available. Install with python setup.py build_ext --inplace")
        return False

# Initial check at import time
try:
    from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
    HAS_YEN_WRAPPER = True
except ImportError:
    HAS_YEN_WRAPPER = False
    get_k_shortest_paths = None
    print("Warning: yen_wrapper not available")


def calculate_path_and_time(start_id, end_id, edges, metro_info, all_station_ids, id_to_index, rer_stop_data, rer_with_line, complete_data=None):
    """
    Calculate k-shortest paths using Yen's algorithm and format for API response.
    Main entry point for pathfinding.
    """
    if not HAS_YEN_WRAPPER:
        print("Error: yen_wrapper not available. Please restart the application.")
        return []
    
    try:
        yen_function = get_k_shortest_paths
        if not yen_function:
            print("Error: Could not get yen_wrapper function")
            return []
    except Exception as e:
        print(f"Error: Failed to get yen_wrapper function: {e}")
        return []
    
    k = 10
    try:
        paths = yen_function(edges, start_id, end_id, k)
    except Exception as e:
        print(f"Error: Failed to calculate paths: {e}")
        return []
    
    index_to_id = {idx: stop_id for idx, stop_id in enumerate(all_station_ids)}
    list_of_paths = []
    list_of_trips = []
    
    # Create transfer time lookup
    transfer_times = {}
    if complete_data:
        for id1, id2, time in complete_data:
            transfer_times[(id1, id2)] = int(time)
            transfer_times[(id2, id1)] = int(time)
    
    # Create info mappings
    metro_id_to_info = {id: (name, line, wheelchair) for id, name, line, wheelchair in metro_info}
    rer_id_to_all_info = {}
    for id, name, line_name, wheelchair in rer_with_line:
        if id not in rer_id_to_all_info:
            rer_id_to_all_info[id] = []
        rer_id_to_all_info[id].append((name, line_name, wheelchair))
    
    for cost, path in paths:
        # Skip duplicate paths
        if path in list_of_paths:
            continue
        
        # Validate path (no backtracking or loops)
        if check_connection(path, index_to_id, metro_info, rer_stop_data):
            continue
        
        # Check for unrealistic patterns
        if has_unrealistic_line_pattern(path, index_to_id, metro_info, rer_with_line):
            continue
        
        # Skip very long paths
        if len(path) > 50:
            continue
        
        list_of_paths.append(path)
        
        # Determine RER line assignments for this path
        rer_line_assignments = {}
        for path_idx, idx in enumerate(path):
            stop_id = index_to_id[idx]
            if stop_id in rer_id_to_all_info:
                correct_line = determine_rer_line_from_context(stop_id, path_idx, path, index_to_id, rer_with_line)
                rer_line_assignments[stop_id] = correct_line
        
        # Build station segments grouped by line
        stations_segments = []
        current_segment = None
        prev_line = None
        prev_line_type = None
        
        for path_idx, idx in enumerate(path):
            stop_id = index_to_id[idx]
            
            # Determine line and station info
            if stop_id in metro_id_to_info:
                name, line, wheelchair = metro_id_to_info[stop_id]
                line_type = 'metro'
                display_line = line
                if line == 15:
                    display_line = '3bis'
                elif line == 16:
                    display_line = '7bis'
                key = f"Metro {display_line}"
                
            elif stop_id in rer_id_to_all_info:
                correct_line = rer_line_assignments[stop_id]
                station_info = next((name, line_name, wheelchair) for name, line_name, wheelchair in rer_id_to_all_info[stop_id] if line_name == correct_line)
                name, line_name, wheelchair = station_info
                line = line_name
                line_type = 'rer'
                key = f"RER {line_name}"
            else:
                continue
            
            station_info_dict = {
                "id": str(id_to_index.get(stop_id, idx)),
                "station": name,
                "wheelchair_accessible": wheelchair
            }
            
            # Start new segment if line changes
            if line != prev_line or line_type != prev_line_type or current_segment is None:
                current_segment = {
                    "line_key": key,
                    "stations": [station_info_dict]
                }
                stations_segments.append(current_segment)
            else:
                current_segment["stations"].append(station_info_dict)
            
            prev_line = line
            prev_line_type = line_type
        
        # Format segments with transfer times
        stations_list = []
        for i, segment in enumerate(stations_segments):
            segment_dict = {segment["line_key"]: segment["stations"]}
            
            # Add transfer time if not first segment
            if i > 0:
                prev_segment = stations_segments[i-1]
                prev_last_station_id = prev_segment["stations"][-1]["id"]
                current_first_station_id = segment["stations"][0]["id"]
                
                prev_station_actual_id = index_to_id[int(prev_last_station_id)]
                current_station_actual_id = index_to_id[int(current_first_station_id)]
                
                transfer_time = transfer_times.get((prev_station_actual_id, current_station_actual_id))
                if transfer_time:
                    segment_dict["transfer_time"] = f"{transfer_time // 60} min {transfer_time % 60} sec"
            
            stations_list.append(segment_dict)
        
        trip = {
            "total_time": f"{int(cost // 60)} minutes and {int(cost % 60)} seconds",
            "stations": stations_list
        }
        list_of_trips.append(trip)
    
    return list_of_trips


def calculate_path_and_time_with_realistic_timing(start_id, end_id, edges, metro_info, all_station_ids, id_to_index, rer_stop_data, rer_with_line, actual_time="8:30:00", complete_data=None, trajects_per_metro=None, rer_trajects=None, rer_filtered_trips=None, list_of_trajet=None):
    """
    Convenience function that combines path calculation with realistic timing.
    Returns trips with realistic timing applied.
    """
    # First, get all possible paths using Yen's algorithm
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


def display_ids(metro_info, all_station_ids, rer_stop_data=None, rer_with_line=None):
    """Display all stations in JSON format."""
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


def analyze_graph(matrix, all_station_ids, metro_info=None):
    """Analyze graph connectivity and compute MST."""
    from app.functions.graph_analayser import analyze_graph as analyze_graph_impl
    return analyze_graph_impl(matrix, all_station_ids, metro_info)
"""Core pathfinding module - delegates to specialized modules."""

import os
import sys

# Import all specialized modules
from app.functions.path_validator import check_connection, has_unrealistic_line_pattern
from app.functions.graph_builder import get_edges_and_graph_v2
from app.functions.time_calculator import (
    calculate_total_realistic_duration_with_details,
    apply_realistic_timing_to_all_trips
)
from app.functions.trajectory_selector import (
    determine_rer_line_from_context,
    search_nearest_time_trajet,
    search_nearest_time_rer_trip,
    list_of_trajet_names,
    select_correct_trajet_by_direction,
    get_transfer_time_enhanced
)
from app.functions.utils.format_utils import deduplicate_trips_by_route, parse_total_time
from app.functions.utils.station_utils import get_station_name_from_id, get_station_id_from_name
from app.functions.utils.time_utils import add_minutes_to_time_str, add_seconds_to_time_str

# Global for Yen's C implementation
HAS_YEN_WRAPPER = False

def check_yen_wrapper_available():
    """Check if yen_wrapper is available for import."""
    try:
        from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
        return True
    except ImportError:
        return False

def update_yen_wrapper_status():
    """Update the global HAS_YEN_WRAPPER status."""
    global HAS_YEN_WRAPPER
    try:
        if 'app.functions.yen_compiler.yen_wrapper' in sys.modules:
            del sys.modules['app.functions.yen_compiler.yen_wrapper']
        from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
        HAS_YEN_WRAPPER = True
        print("SUCCESS: Fast C implementation of Yen's algorithm loaded successfully")
        return True
    except ImportError:
        HAS_YEN_WRAPPER = False
        print("Warning: yen_wrapper not available. Install with python setup.py build_ext --inplace")
        return False

# Initial check at import time
try:
    from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
    HAS_YEN_WRAPPER = True
except ImportError:
    HAS_YEN_WRAPPER = False
    get_k_shortest_paths = None
    print("Warning: yen_wrapper not available")


def calculate_path_and_time(start_id, end_id, edges, metro_info, all_station_ids, id_to_index, rer_stop_data, rer_with_line, complete_data=None):
    """
    Calculate k-shortest paths using Yen's algorithm and format for API response.
    Main entry point for pathfinding.
    """
    if not HAS_YEN_WRAPPER:
        print("Error: yen_wrapper not available. Please restart the application.")
        return []
    
    try:
        yen_function = get_k_shortest_paths
        if not yen_function:
            print("Error: Could not get yen_wrapper function")
            return []
    except Exception as e:
        print(f"Error: Failed to get yen_wrapper function: {e}")
        return []
    
    k = 10
    try:
        paths = yen_function(edges, start_id, end_id, k)
    except Exception as e:
        print(f"Error: Failed to calculate paths: {e}")
        return []
    
    index_to_id = {idx: stop_id for idx, stop_id in enumerate(all_station_ids)}
    list_of_paths = []
    list_of_trips = []
    
    # Create transfer time lookup
    transfer_times = {}
    if complete_data:
        for id1, id2, time in complete_data:
            transfer_times[(id1, id2)] = int(time)
            transfer_times[(id2, id1)] = int(time)
    
    # Create info mappings
    metro_id_to_info = {id: (name, line, wheelchair) for id, name, line, wheelchair in metro_info}
    rer_id_to_all_info = {}
    for id, name, line_name, wheelchair in rer_with_line:
        if id not in rer_id_to_all_info:
            rer_id_to_all_info[id] = []
        rer_id_to_all_info[id].append((name, line_name, wheelchair))
    
    for cost, path in paths:
        # Skip duplicate paths
        if path in list_of_paths:
            continue
        
        # Validate path (no backtracking or loops)
        if check_connection(path, index_to_id, metro_info, rer_stop_data):
            continue
        
        # Check for unrealistic patterns
        if has_unrealistic_line_pattern(path, index_to_id, metro_info, rer_with_line):
            continue
        
        # Skip very long paths
        if len(path) > 50:
            continue
        
        list_of_paths.append(path)
        
        # Determine RER line assignments for this path
        rer_line_assignments = {}
        for path_idx, idx in enumerate(path):
            stop_id = index_to_id[idx]
            if stop_id in rer_id_to_all_info:
                correct_line = determine_rer_line_from_context(stop_id, path_idx, path, index_to_id, rer_with_line)
                rer_line_assignments[stop_id] = correct_line
        
        # Build station segments grouped by line
        stations_segments = []
        current_segment = None
        prev_line = None
        prev_line_type = None
        
        for path_idx, idx in enumerate(path):
            stop_id = index_to_id[idx]
            
            # Determine line and station info
            if stop_id in metro_id_to_info:
                name, line, wheelchair = metro_id_to_info[stop_id]
                line_type = 'metro'
                display_line = line
                if line == 15:
                    display_line = '3bis'
                elif line == 16:
                    display_line = '7bis'
                key = f"Metro {display_line}"
                
            elif stop_id in rer_id_to_all_info:
                correct_line = rer_line_assignments[stop_id]
                station_info = next((name, line_name, wheelchair) for name, line_name, wheelchair in rer_id_to_all_info[stop_id] if line_name == correct_line)
                name, line_name, wheelchair = station_info
                line = line_name
                line_type = 'rer'
                key = f"RER {line_name}"
            else:
                continue
            
            station_info_dict = {
                "id": str(id_to_index.get(stop_id, idx)),
                "station": name,
                "wheelchair_accessible": wheelchair
            }
            
            # Start new segment if line changes
            if line != prev_line or line_type != prev_line_type or current_segment is None:
                current_segment = {
                    "line_key": key,
                    "stations": [station_info_dict]
                }
                stations_segments.append(current_segment)
            else:
                current_segment["stations"].append(station_info_dict)
            
            prev_line = line
            prev_line_type = line_type
        
        # Format segments with transfer times
        stations_list = []
        for i, segment in enumerate(stations_segments):
            segment_dict = {segment["line_key"]: segment["stations"]}
            
            # Add transfer time if not first segment
            if i > 0:
                prev_segment = stations_segments[i-1]
                prev_last_station_id = prev_segment["stations"][-1]["id"]
                current_first_station_id = segment["stations"][0]["id"]
                
                prev_station_actual_id = index_to_id[int(prev_last_station_id)]
                current_station_actual_id = index_to_id[int(current_first_station_id)]
                
                transfer_time = transfer_times.get((prev_station_actual_id, current_station_actual_id))
                if transfer_time:
                    segment_dict["transfer_time"] = f"{transfer_time // 60} min {transfer_time % 60} sec"
            
            stations_list.append(segment_dict)
        
        trip = {
            "total_time": f"{int(cost // 60)} minutes and {int(cost % 60)} seconds",
            "stations": stations_list
        }
        list_of_trips.append(trip)
    
    return list_of_trips


def calculate_path_and_time_with_realistic_timing(start_id, end_id, edges, metro_info, all_station_ids, id_to_index, rer_stop_data, rer_with_line, actual_time="8:30:00", complete_data=None, trajects_per_metro=None, rer_trajects=None, rer_filtered_trips=None, list_of_trajet=None):
    """
    Convenience function that combines path calculation with realistic timing.
    Returns trips with realistic timing applied.
    """
    # First, get all possible paths using Yen's algorithm
    original_trips = calculate_path_and_time(
        start_id, end_id, edges, metro_info, all_station_ids, 
        id_to_index, rer_stop_data, rer_with_line, complete_data
    )
    #print(f"Original trips found: {original_trips}")
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
    #print(f"Realistic trips after timing applied: {realistic_trips}")
    
    # Deduplicate trips based on route taken
    deduplicated_trips = deduplicate_trips_by_route(realistic_trips)
    #print(f"Deduplicated trips: {deduplicated_trips}")
    
    return deduplicated_trips


def display_ids(metro_info, all_station_ids, rer_stop_data=None, rer_with_line=None):
    """Display all stations in JSON format."""
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
