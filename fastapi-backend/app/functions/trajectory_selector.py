"""Trajectory and trip selection functions for route planning."""

from app.functions.utils.time_utils import time_difference_seconds, add_seconds_to_time_str
from app.functions.utils.station_utils import get_station_id_from_name


def _normalize_station_id(station_id):
    """Normalize station IDs so IDFM-prefixed and raw IDs can be compared safely."""
    if station_id is None:
        return None
    return str(station_id).split(":")[-1]


def _time_to_seconds(time_str):
    """Convert HH:MM:SS (including >24h GTFS values) to seconds."""
    h, m, s = map(int, str(time_str).split(":"))
    return h * 3600 + m * 60 + s


def search_nearest_time_trajet(actual_time, start_id, target_metro_key, trajects_per_metro, end_id=None):
    """
    Find the nearest trajet that departs after the given time.
    If end_id is provided, only consider trajets that contain both start and end stations.
    If no future trips found, find the earliest trip and assume next day.
    """
    nearest_trajet = []
    min_time_diff = float('inf')
    duration = float('inf')
    earliest_trip = None
    earliest_time_seconds = None

    normalized_start_id = _normalize_station_id(start_id)
    normalized_end_id = _normalize_station_id(end_id) if end_id is not None else None

    for trajet, stops in trajects_per_metro[target_metro_key].items():
        # Get all station IDs in this trajet
        trajet_station_ids = {_normalize_station_id(stop[7]) for stop in stops}
        
        # If end_id is specified, check if both start and end stations are in this trajet
        if end_id is not None:
            if normalized_start_id not in trajet_station_ids or normalized_end_id not in trajet_station_ids:
                continue
        
        for stop in stops:
            if _normalize_station_id(stop[7]) == normalized_start_id:
                # Use departure time for boarding decisions.
                departure_time = stop[6]
                time_diff = time_difference_seconds(departure_time, actual_time)
                
                # Track earliest trip in case no future trips are found
                departure_seconds = _time_to_seconds(departure_time)
                if earliest_trip is None or departure_seconds < earliest_time_seconds:
                    earliest_trip = [target_metro_key, trajet, stop]
                    earliest_time_seconds = departure_seconds
                
                # Look for trips departing after current time (including exact time)
                if 0 <= time_diff < min_time_diff:
                    min_time_diff = time_diff
                    nearest_trajet = [target_metro_key, trajet, stop]
                    duration_info = _get_trajet_duration(target_metro_key, trajet, trajects_per_metro)
                    duration = duration_info['total_seconds']
                elif 0 <= time_diff == min_time_diff:
                    # Compare durations if times are equal
                    duration_info = _get_trajet_duration(target_metro_key, trajet, trajects_per_metro)
                    if duration_info['total_seconds'] < duration:
                        nearest_trajet = [target_metro_key, trajet, stop]
                        duration = duration_info['total_seconds']
    
    # If no future trips found, use earliest trip from next day
    if not nearest_trajet and earliest_trip:
        print(f"Warning: No future trips found for {target_metro_key} from {start_id} after {actual_time}")
        nearest_trajet = earliest_trip
    
    return nearest_trajet


def search_nearest_time_rer_trip(actual_time, start_id, target_rer_id, rer_trajects, rer_filtered_trips, end_id=None):
    """
    Find RER trip for realistic wait time calculation.
    """
    nearest_trip = []
    min_time_diff = float('inf')
    earliest_trip = None
    earliest_time = None
    
    # Try to find a real trip for realistic wait time
    if target_rer_id in rer_filtered_trips:
        for trip_idx in rer_filtered_trips[target_rer_id]:
            trip_key = trip_idx if trip_idx in rer_trajects[target_rer_id] else f"Trip: {trip_idx}"
            if trip_key in rer_trajects[target_rer_id]:
                trip_stops = rer_trajects[target_rer_id][trip_key]
                
                # If end_id is specified, check if both stations are in this trip
                if end_id is not None:
                    stop_ids = [stop[3] for stop in trip_stops]
                    if start_id not in stop_ids or end_id not in stop_ids:
                        continue
                
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
            from app.functions.utils.time_utils import add_seconds_to_time_str
            synthetic_time = add_seconds_to_time_str(actual_time, 600)
            synthetic_stop = [
                f"SYNTHETIC_{target_rer_id}",
                target_rer_id,
                synthetic_time,
                start_id
            ]
            nearest_trip = [target_rer_id, f"Trip: SYNTHETIC_{target_rer_id}", synthetic_stop]
    
    return nearest_trip


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
                weight = max(1, 10 - distance)
                line_scores[line] += weight
    
    # Return the line with the highest score
    if line_scores:
        best_line = max(line_scores.keys(), key=lambda x: line_scores[x])
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


def list_of_trajet_names(line_type, line_id, depart_name, all_metro_info, rer_stop_data, actual_time, trajects_per_metro, rer_trajects, rer_filtered_trips, destination_name=None):
    """
    Find available trajets/trips for a given line type and departure station
    """
    lists = []
    
    if line_type == 'metro':
        metro_name = f"Metro :{line_id}"
        # Find all station IDs with this name
        departure_station_ids = get_station_id_from_name(depart_name, all_metro_info, rer_stop_data)
        
        
        # If destination is provided, get its IDs too
        destination_ids = []
        if destination_name:
            destination_ids = get_station_id_from_name(destination_name, all_metro_info, rer_stop_data)
        
        for station_id in departure_station_ids:
            # Check if this station belongs to the metro line
            for triplet in all_metro_info:
                if triplet[0] == station_id.replace("IDFM:", "") and triplet[2] == line_id:
                    # For each destination ID, try to find a trajet that connects both stations
                    if destination_ids:
                        for dest_id in destination_ids:
                            trajet_info = search_nearest_time_trajet(actual_time, station_id, metro_name, trajects_per_metro, dest_id)
                            if len(trajet_info) > 0 and trajet_info[0] == metro_name:
                                lists.append(trajet_info)
                                break
                    else:
                        # No destination specified, use original logic
                        trajet_info = search_nearest_time_trajet(actual_time, station_id, metro_name, trajects_per_metro)
                        if len(trajet_info) > 0 and trajet_info[0] == metro_name:
                            lists.append(trajet_info)
                    break
    
    elif line_type == 'rer':
        # Map RER line letter to IDFM route ID
        from app.functions.data_loader import get_rer_lines
        rer_lines = get_rer_lines()
        target_rer_route_id = None
        for line_info in rer_lines:
            if line_info[2] == line_id:
                target_rer_route_id = line_info[0]
                break
        
        if not target_rer_route_id:
            print(f"Warning: Could not find route ID for RER line {line_id}")
            return lists
        
        # Find all station IDs with this name
        departure_station_ids = get_station_id_from_name(depart_name, all_metro_info, rer_stop_data)
        
        # If destination is provided, get its IDs too
        destination_ids = []
        if destination_name:
            destination_ids = get_station_id_from_name(destination_name, all_metro_info, rer_stop_data)
        
        for station_id in departure_station_ids:
            # Check if this station belongs to the RER line
            for rer_stop in rer_stop_data:
                if rer_stop[0] == station_id:
                    # If destination is specified, try to find trips that connect both stations
                    if destination_ids:
                        for dest_id in destination_ids:
                            trip_info = search_nearest_time_rer_trip(actual_time, station_id, target_rer_route_id, rer_trajects, rer_filtered_trips, dest_id)
                            if len(trip_info) > 0:
                                lists.append(trip_info)
                                break
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
            stop_ids_in_order = [_normalize_station_id(stop[7]) for stop in trajet_stops]
            
        elif line_type == 'rer':
            rer_route_id = line[0]
            trip_name = line[1]
            
            # Handle synthetic trips
            if trip_name.startswith("Trip: SYNTHETIC_"):
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
                continue
                
            trip_stops = rer_trajects[rer_route_id][trip_name]
            stop_ids_in_order = [stop[3] for stop in trip_stops]
        
        # Check if this trajet/trip contains both stations in the correct order
        for first_id in first_station_ids:
            for last_id in last_station_ids:
                first_cmp = _normalize_station_id(first_id) if line_type == 'metro' else first_id
                last_cmp = _normalize_station_id(last_id) if line_type == 'metro' else last_id
                if first_cmp in stop_ids_in_order and last_cmp in stop_ids_in_order:
                    first_index = stop_ids_in_order.index(first_cmp)
                    last_index = stop_ids_in_order.index(last_cmp)
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
        return 0
    
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
            for connection in complete_data:
                if (connection[0] == from_id and connection[1] == to_id) or \
                   (connection[0] == to_id and connection[1] == from_id):
                    return int(connection[2])
    
    # If no specific transfer time found, return default transfer time based on line types
    if from_line_type != to_line_type:
        default_time = 180
    else:
        default_time = 120
    
    print(f"Warning: No transfer time found between {from_line_type} {from_line} and {to_line_type} {to_line} at {station_name}")
    return default_time


def _get_trajet_duration(metro_name, trajet_name, trajects_per_metro):
    """Helper function to calculate total duration of a metro journey in seconds."""
    total_time = 0
    trajet = trajects_per_metro[metro_name][trajet_name]
    for i in range(1, len(trajet)):
        total_time += time_difference_seconds(trajet[i][5], trajet[i-1][5])
    
    return {
        'total_seconds': total_time,
        'minutes': total_time // 60,
        'seconds': total_time % 60,
        'formatted': f"{total_time // 60}m {total_time % 60}s"
    }
