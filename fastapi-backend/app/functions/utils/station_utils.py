"""Station utility functions for ID and name conversions."""


def get_station_name_from_id(station_id, all_metro_info, rer_stop_data):
    """Get station name from ID, checking both metro and RER data."""
    # Check metro data first
    for triplet in all_metro_info:
        if triplet[0] == station_id:
            return triplet[1]
    
    # Check RER data
    for rer_stop in rer_stop_data:
        if rer_stop[0] == station_id:
            return rer_stop[1]
    
    return None


def get_station_id_from_name(station_name, all_metro_info, rer_stop_data):
    """
    Get station IDs from name, checking both metro and RER data.
    Note: RER station IDs are unique and don't change between lines or directions.
    """
    list_of_ids = []
    
    # Check metro data
    for triplet in all_metro_info:
        if triplet[1] == station_name and f"IDFM:{triplet[0]}" not in list_of_ids:
            list_of_ids.append(f"IDFM:{triplet[0]}")
    
    # Check RER data - each station has only one unique ID regardless of line
    for rer_stop in rer_stop_data:
        if rer_stop[1] == station_name:
            list_of_ids.append(rer_stop[0])
    
    return list_of_ids
