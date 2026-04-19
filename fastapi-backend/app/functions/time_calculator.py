"""Time calculation functions for realistic route timing."""

import heapq
from app.functions.utils.time_utils import time_difference_seconds, add_seconds_to_time_str
from app.functions.utils.station_utils import get_station_name_from_id, get_station_id_from_name
from app.functions.utils.format_utils import parse_total_time
from app.functions.trajectory_selector import (
    list_of_trajet_names,
    select_correct_trajet_by_direction,
    get_transfer_time_enhanced
)

# Global for Yen's wrapper availability
HAS_YEN_WRAPPER = False
get_k_shortest_paths = None

try:
    from app.functions.yen_compiler.yen_wrapper import get_k_shortest_paths
    HAS_YEN_WRAPPER = True
except ImportError:
    HAS_YEN_WRAPPER = False


def duration_trajet(metro_name, trajet_name, trajects_per_metro):
    """Calculate the total duration of a metro journey in seconds."""
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


def calculate_partial_duration(trajet_name, start_id, end_id, metro_name, actual_time, trajects_per_metro):
    """Calculate partial duration between two stations in a metro journey."""
    trajet = trajects_per_metro[metro_name][trajet_name]

    def normalize_station_ids(station_id):
        if station_id is None:
            return set()
        value = str(station_id)
        if value.startswith("IDFM:"):
            return {value, value.replace("IDFM:", "")}
        return {value, f"IDFM:{value}"}

    def time_diff_with_wrap(time1, time2):
        # GTFS can contain wrapped times around midnight.
        diff = time_difference_seconds(time1, time2)
        if diff < 0:
            diff += 24 * 3600
        return diff

    start_ids = normalize_station_ids(start_id)
    end_ids = normalize_station_ids(end_id)

    start_positions = [idx for idx, stop in enumerate(trajet) if stop[7] in start_ids]
    end_positions = [idx for idx, stop in enumerate(trajet) if stop[7] in end_ids]

    if not start_positions or not end_positions:
        print(f"Warning: Station not found in trajet {trajet_name} ({metro_name})")
        fallback_duration = 120
        return {
            'total_seconds': fallback_duration,
            'minutes': fallback_duration // 60,
            'seconds': fallback_duration % 60,
            'formatted': f"{fallback_duration // 60}m {fallback_duration % 60}s"
        }

    # Prefer direction-consistent indices where end comes after start.
    selected_pair = None
    best_span = None
    for s_idx in start_positions:
        for e_idx in end_positions:
            if e_idx > s_idx:
                span = e_idx - s_idx
                if best_span is None or span < best_span:
                    best_span = span
                    selected_pair = (s_idx, e_idx)

    # Fallback: choose the closest pair if no forward ordering is found.
    if selected_pair is None:
        selected_pair = min(
            ((s_idx, e_idx) for s_idx in start_positions for e_idx in end_positions),
            key=lambda pair: abs(pair[1] - pair[0])
        )

    start_idx, end_idx = selected_pair
    if start_idx == end_idx:
        total_seconds = 0
    else:
        low = min(start_idx, end_idx)
        high = max(start_idx, end_idx)
        total_seconds = 0
        for pos in range(low + 1, high + 1):
            delta = time_diff_with_wrap(trajet[pos][5], trajet[pos - 1][5])
            if delta <= 0:
                delta = 60
            total_seconds += delta

        # Guarantee positive travel time when moving between different stations.
        if total_seconds <= 0:
            total_seconds = max(60, (high - low) * 60)
    
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    
    return {
        'total_seconds': total_seconds,
        'minutes': minutes,
        'seconds': seconds,
        'formatted': f"{minutes}m {seconds}s"
    }


def calculate_partial_rer_duration_realistic(segment_stations, edges, all_station_ids, id_to_index):
    """Calculate realistic partial duration for RER journey using Yen implementation."""
    if not HAS_YEN_WRAPPER:
        print("Error: yen_wrapper not available for RER duration calculation")
        return {
            'total_seconds': 300,
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
        k = 1
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
            print(f"Warning: No path found between {start_station_id} and {end_station_id}")
            fallback_time = max(180, (len(segment_stations) - 1) * 120)
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


def calculate_total_realistic_duration_with_details(paths, actual_time, all_metro_info, trajects_per_metro, rer_stop_data, rer_trajects, rer_filtered_trips, complete_data, list_of_trajet, edges, all_station_ids, id_to_index):
    """
    Calculate realistic duration and return detailed timing breakdown for frontend use.
    Returns both the timing summary and detailed segment information.
    """
    total_seconds = 0
    current_time = actual_time
    previous_line = None
    previous_line_type = None
    
    result_stations = paths['stations'].copy()
    accessibility_info = []
    segment_details = []
    
    for i, segment_dict in enumerate(paths['stations']):
        line_key = list(segment_dict.keys())[0]
        stations = segment_dict[line_key]
        
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
        
        segment_accessible = all(station.get('wheelchair_accessible', 0) == 1 for station in stations)
        accessibility_info.append({
            'line': line_key,
            'accessible': segment_accessible,
            'first_station': first_station_name,
            'last_station': last_station_name
        })
        
        lists = list_of_trajet_names(line_type, line_id, first_station_name, all_metro_info, rer_stop_data, current_time, trajects_per_metro, rer_trajects, rer_filtered_trips, last_station_name)
        
        if not lists:
            print(f"Warning: No {line_type} options found for {line_key} from {first_station_name}")
            continue
        
        selected_option = select_correct_trajet_by_direction(lists, first_station_name, last_station_name, all_metro_info, rer_stop_data, line_type, line_id, trajects_per_metro, rer_trajects)
        
        if not selected_option:
            print(f"Warning: No suitable {line_type} option found for {line_key}")
            continue
        
        ligne = selected_option['ligne_info']
        trajet_name = selected_option['trajet_name']
        line_name = selected_option['line_name']
        # Use departure time for metro boarding (same basis used in trajectory selection).
        depart_time = ligne[2][6] if line_type == 'metro' else ligne[2][2]
        
        if line_type == 'rer':
            if not trajet_name.startswith("Trip: SYNTHETIC_"):
                wait_time_seconds = time_difference_seconds(depart_time, current_time)
                if wait_time_seconds <= 0:
                    wait_time_seconds = 600
                elif wait_time_seconds > 600:
                    wait_time_seconds = 600
            else:
                wait_time_seconds = 600
        else:
            raw_wait = time_difference_seconds(depart_time, current_time)
            wait_time_seconds = raw_wait
            if wait_time_seconds <= 0:
                if wait_time_seconds < 0:
                    wait_time_seconds = 24 * 3600 + wait_time_seconds
                else:
                    wait_time_seconds = 30
            if wait_time_seconds > 3600:
                wait_time_seconds = 1200
        
        if line_type == 'metro':
            if selected_option['first_station_id'] and selected_option['last_station_id']:
                depart_id = selected_option['first_station_id']
                arrivee_id = selected_option['last_station_id']
            else:
                depart_ids = get_station_id_from_name(first_station_name, all_metro_info, rer_stop_data)
                arrivee_ids = get_station_id_from_name(last_station_name, all_metro_info, rer_stop_data)
                depart_id = depart_ids[0] if depart_ids else None
                arrivee_id = arrivee_ids[0] if arrivee_ids else None
            
            if not depart_id or not arrivee_id:
                print(f"Warning: Could not find station IDs for metro {first_station_name} or {last_station_name}")
                continue
        
        try:
            if line_type == 'metro':
                duree_info = calculate_partial_duration(trajet_name, depart_id, arrivee_id, line_name, current_time, trajects_per_metro)
            else:
                duree_info = calculate_partial_rer_duration_realistic(stations, edges, all_station_ids, id_to_index)
            
            if duree_info['total_seconds'] >= 0 and wait_time_seconds >= 0:
                transfer_time_added = 0
                if i > 0:
                    prev_segment_dict = paths['stations'][i - 1]
                    prev_line_key = list(prev_segment_dict.keys())[0]
                    
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
                    
                    if line_id != prev_line_id or line_type != prev_line_type:
                        transfer_time_added = get_transfer_time_enhanced(first_station_name, prev_line_id, line_id, prev_line_type, line_type, all_metro_info, rer_stop_data, complete_data)
                
                segment_detail = {
                    'line': line_key,
                    'from_station': first_station_name,
                    'to_station': last_station_name,
                    'wait_time_seconds': max(0, wait_time_seconds),
                    'travel_time_seconds': max(0, duree_info['total_seconds']),
                    'transfer_time_seconds': max(0, transfer_time_added),
                    'total_segment_seconds': duree_info['total_seconds'] + wait_time_seconds + transfer_time_added,
                    'departure_time': depart_time,
                    'arrival_time': add_seconds_to_time_str(current_time, duree_info['total_seconds'] + wait_time_seconds + transfer_time_added),
                    'segment_start_time': current_time,
                    'segment_end_time': add_seconds_to_time_str(current_time, duree_info['total_seconds'] + wait_time_seconds + transfer_time_added),
                    'line_type': line_type,
                    'accessible': segment_accessible,
                    'segment_index': i
                }
                segment_details.append(segment_detail)

                total_segment_time = duree_info['total_seconds'] + wait_time_seconds + transfer_time_added

                total_seconds += total_segment_time
                
                current_time = add_seconds_to_time_str(current_time, total_segment_time)
                
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
    
    overall_accessible = all(segment['accessible'] for segment in accessibility_info)
    
    return {
        'total_time': f"{total_minutes} minutes and {remaining_seconds} seconds",
        'total_seconds': total_seconds,
        'stations': result_stations,
        'wheelchair_accessible': overall_accessible,
        'accessibility_details': accessibility_info,
        'segment_details': segment_details,
        'total_wait_time': sum(seg.get('wait_time_seconds', 0) for seg in segment_details),
        'total_travel_time': sum(seg.get('travel_time_seconds', 0) for seg in segment_details),
        'total_transfer_time': sum(seg.get('transfer_time_seconds', 0) for seg in segment_details)
    }


def apply_realistic_timing_to_all_trips(trips_list, actual_time, all_metro_info, trajects_per_metro, rer_stop_data, rer_trajects, rer_filtered_trips, complete_data, list_of_trajet, edges, all_station_ids, id_to_index):
    """
    Apply realistic timing to all trips returned by calculate_path_and_time.
    Returns the same structure as the original trips but with updated timing and wait time details.
    """
    realistic_trips = []

    def trip_has_movement(trip):
        """Return True when the trip contains at least one station-to-station movement."""
        station_ids = []
        for segment in trip.get("stations", []):
            for line_key, stations in segment.items():
                if line_key == "transfer_time" or not isinstance(stations, list):
                    continue
                for station in stations:
                    station_ids.append(str(station.get("id", "")))

        if len(station_ids) < 2:
            return False

        return any(station_ids[i] != station_ids[i - 1] for i in range(1, len(station_ids)))
    
    for i, trip in enumerate(trips_list):
        try:
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
            
            components_total_seconds = realistic_data['total_wait_time'] + realistic_data['total_travel_time'] + realistic_data['total_transfer_time']
            original_total_seconds = parse_total_time(trip.get("total_time", "0 minutes and 0 seconds"))

            # Guardrail: if detailed timing produced 0 for a trip that clearly moves,
            # keep the original path duration instead of returning a zero-time trip.
            if components_total_seconds <= 0 and trip_has_movement(trip):
                components_total_seconds = max(original_total_seconds, 60)
                realistic_data['total_wait_time'] = 0
                realistic_data['total_transfer_time'] = 0
                realistic_data['total_travel_time'] = components_total_seconds

            components_minutes = components_total_seconds // 60
            components_remaining_seconds = components_total_seconds % 60
            
            updated_trip = {
                "total_time": f"{components_minutes} minutes and {components_remaining_seconds} seconds",
                "stations": trip['stations']
            }
            
            updated_trip['timing_details'] = {
                'realistic_total_seconds': components_total_seconds,
                'wheelchair_accessible': realistic_data['wheelchair_accessible'],
                'accessibility_details': realistic_data['accessibility_details'],
                'trip_rank': i + 1,
                'total_wait_time': realistic_data['total_wait_time'],
                'total_travel_time': realistic_data['total_travel_time'],
                'total_transfer_time': realistic_data['total_transfer_time'],
                'segment_details': realistic_data['segment_details']
            }
            
            realistic_trips.append(updated_trip)
            
        except Exception as e:
            print(f"Warning: Failed to calculate realistic timing for trip {i+1}: {e}")
            fallback_seconds = parse_total_time(trip.get("total_time", "0 minutes and 0 seconds"))
            if trip_has_movement(trip):
                fallback_seconds = max(fallback_seconds, 60)

            fallback_trip = {
                "total_time": f"{fallback_seconds // 60} minutes and {fallback_seconds % 60} seconds",
                "stations": trip['stations']
            }
            
            fallback_trip['timing_details'] = {
                'realistic_timing_failed': True,
                'trip_rank': i + 1,
                'wheelchair_accessible': None,
                'accessibility_details': [],
                'total_wait_time': 0,
                'total_travel_time': fallback_seconds,
                'total_transfer_time': 0,
                'segment_details': [],
                'realistic_total_seconds': fallback_seconds
            }
            
            realistic_trips.append(fallback_trip)
    
    realistic_trips.sort(key=lambda x: x.get('timing_details', {}).get('realistic_total_seconds', float('inf')))
    
    for i, trip in enumerate(realistic_trips):
        trip['timing_details']['realistic_rank'] = i + 1
    
    return realistic_trips
