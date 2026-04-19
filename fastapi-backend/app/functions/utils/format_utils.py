"""Format utility functions for output processing."""


def parse_total_time(time_str):
    """Parse time string to get total seconds for comparison."""
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
