"""Path validation and filtering functions."""


def check_connection(path, index_to_id, metro_info, rer_stop_data=None):
    """Validate if a path is realistic without backtracking or inefficient patterns."""
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
    """Check if station transfers are consistent between line segments."""
    prev_last_station = None
    for line_dict in stations_by_line:
        line_name, stations = next(iter(line_dict.items()))
        if prev_last_station:
            current_first_station = stations[0]["station"]
            if current_first_station != prev_last_station:
                return False
        prev_last_station = stations[-1]["station"]
    return True


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
