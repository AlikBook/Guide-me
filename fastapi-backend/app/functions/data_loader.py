"""Data loading functions for metro and RER data from SQLite database."""

import os
import pickle
from app.core.database import db_cursor
from app.services.transport_service import (
    get_all_stops,
    get_rer_lines,
    get_detailed_rer_trips,
)


def get_pickle_path(filename):
    """Helper to get pickle file path (for legacy support during transition)."""
    pickle_dir = os.path.join(os.path.dirname(__file__), "container_pkl_files")
    os.makedirs(pickle_dir, exist_ok=True)
    return os.path.join(pickle_dir, filename)


def _normalize_metro_line(route_short_name):
    """Map GTFS route short names to legacy metro numeric keys.

    Legacy contract used in the app:
    - Metro 1..14 as numbers
    - 3bis -> 15
    - 7bis -> 16
    """
    if route_short_name is None:
        return None

    short = str(route_short_name).strip().lower()
    if short in {"3bis", "3b"}:
        return 15
    if short in {"7bis", "7b"}:
        return 16

    if short.isdigit():
        value = int(short)
        if 1 <= value <= 14:
            return value

    return None


def get_trajets_for_metro():
    """Load metro trajectories from SQL using the legacy in-memory shape.

    Returns:
        dict like:
            {
                "Metro :1": {
                    "Trajet 1": [[..., route_id, trip_id, arrival, departure, stop_id], ...],
                    ...
                },
                ...
            }
    """
    # Use route_short_name mapping instead of route_id prefix.
    # A single route_id prefix only matches part of the metro network.
    query = """
        SELECT t.route_id, r.route_short_name, st.trip_id, st.arrival_time, st.departure_time, st.stop_id
        FROM stop_times st
        JOIN trips t ON st.trip_id = t.trip_id
        JOIN routes r ON t.route_id = r.route_id
        WHERE lower(trim(r.route_short_name)) IN (
            '1','2','3','4','5','6','7','8','9','10','11','12','13','14','3bis','3b','7bis','7b'
        )
        ORDER BY t.route_id, st.trip_id, st.arrival_time, st.departure_time
    """

    with db_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    by_line_and_trip = {}
    for row in rows:
        line_n = _normalize_metro_line(row["route_short_name"])
        if line_n is None:
            continue

        trip_id = row["trip_id"]
        if line_n not in by_line_and_trip:
            by_line_and_trip[line_n] = {}
        if trip_id not in by_line_and_trip[line_n]:
            by_line_and_trip[line_n][trip_id] = []

        by_line_and_trip[line_n][trip_id].append([
            None,
            None,
            None,
            row["route_id"],
            row["trip_id"],
            row["arrival_time"],
            row["departure_time"],
            row["stop_id"],
        ])

    trajects_per_metro = {}
    for line_n in range(1, 17):
        line_key = f"Metro :{line_n}"
        trajects_per_metro[line_key] = {}

        line_trips = by_line_and_trip.get(line_n, {})
        for idx, trip_id in enumerate(sorted(line_trips.keys()), start=1):
            trajects_per_metro[line_key][f"Trajet {idx}"] = line_trips[trip_id]

    return trajects_per_metro


def is_subsequence(sub, seq):
    """Return True when sub appears as a contiguous subsequence of seq."""
    sub = tuple(sub)
    seq = tuple(seq)
    n, m = len(sub), len(seq)
    if n == 0:
        return True
    if n > m:
        return False
    for i in range(m - n + 1):
        if seq[i:i + n] == sub:
            return True
    return False


def filter_subsequences(list_of_trajet, trajects_per_metro):
    """Remove trajet indexes that are strict subsequences of other trajets on same line."""
    for i in range(1, 17):
        key = f"Metro :{i}"
        if key not in trajects_per_metro:
            continue

        idx_to_remove = []
        for idx in list_of_trajet[i - 1]:
            trajet_key = f"Trajet {idx}"
            if trajet_key not in trajects_per_metro[key]:
                continue
            stops = tuple(stop[7] for stop in trajects_per_metro[key][trajet_key])
            for other_idx in list_of_trajet[i - 1]:
                other_trajet_key = f"Trajet {other_idx}"
                if other_trajet_key not in trajects_per_metro[key]:
                    continue
                other_stops = tuple(stop[7] for stop in trajects_per_metro[key][other_trajet_key])
                if is_subsequence(stops, other_stops) and idx != other_idx:
                    idx_to_remove.append(idx)

        for idx in set(idx_to_remove):
            if idx in list_of_trajet[i - 1]:
                list_of_trajet[i - 1].remove(idx)

        if key == "Metro :10" and len(list_of_trajet[i - 1]) > 1:
            list_of_trajet[i - 1] = list_of_trajet[i - 1][1:]

    return list_of_trajet


def get_max_len(trajects_per_metro):
    """Compute canonical trajet indexes for each metro line (legacy contract)."""
    list_of_trajet = []

    for i in range(1, 17):
        key = f"Metro :{i}"
        line_data = trajects_per_metro.get(key, {})
        trajet_keys = list(line_data.keys())

        # First, keep only one trip index per exact stop sequence.
        # GTFS data contains many timetable variants with identical station shapes.
        sequence_to_first_idx = {}
        for j, trajet in enumerate(trajet_keys, 1):
            stops = tuple(stop[7] for stop in line_data[trajet])
            if stops and stops not in sequence_to_first_idx:
                sequence_to_first_idx[stops] = j

        unique_sequences = list(sequence_to_first_idx.keys())
        kept_sequences = []

        # Then remove strict subsequences across the unique shapes only.
        for current_stops in unique_sequences:
            is_strict_subseq = False
            for other_stops in unique_sequences:
                if current_stops == other_stops:
                    continue
                if len(current_stops) < len(other_stops) and is_subsequence(current_stops, other_stops):
                    is_strict_subseq = True
                    break
            if not is_strict_subseq:
                kept_sequences.append(current_stops)

        idx_to_add = sorted(sequence_to_first_idx[stops] for stops in kept_sequences)
        list_of_trajet.append(idx_to_add)

    return filter_subsequences(list_of_trajet, trajects_per_metro)


def get_stations_id_and_name_per_metro(trajects_per_metro, list_of_trajet, stop_data):
    """Build station metadata used by pathfinding and display functions."""
    metro_stop_info = []
    all_metro_stop_info = []

    for stop in stop_data:
        stop_id = stop[0]
        wheelchair = stop[2] if len(stop) > 2 else 0

        for i, metro_trajet in enumerate(list_of_trajet, 1):
            key = f"Metro :{i}"
            if key not in trajects_per_metro:
                continue
            for idx in metro_trajet:
                trajet_key = f"Trajet {idx}"
                if trajet_key not in trajects_per_metro[key]:
                    continue
                for trajet in trajects_per_metro[key][trajet_key]:
                    if stop_id == trajet[7].split(":")[-1]:
                        all_metro_stop_info.append((stop_id, stop[1], i, wheelchair))
                        if all(existing_id != stop_id for existing_id, *_ in metro_stop_info):
                            metro_stop_info.append((stop_id, stop[1], i, wheelchair))

    return metro_stop_info, all_metro_stop_info


def filter_idx_trajects(trajects_per_metro, metro_stop_info, list_of_trajet):
    """Reduce trajets per line to unique endpoint pairs (legacy contract)."""
    new_list_of_trajet = []

    for i, trajet in enumerate(list_of_trajet, 1):
        key = f"Metro :{i}"
        if key not in trajects_per_metro:
            new_list_of_trajet.append([])
            continue

        if i in (10, 16):
            new_list_of_trajet.append(trajet[:])
            continue

        temp_list = []
        new_trajet = []
        for idx in trajet:
            trajet_key = f"Trajet {idx}"
            if trajet_key not in trajects_per_metro[key]:
                continue

            stops = trajects_per_metro[key][trajet_key]
            init_stop = stops[0][7].split(":")[-1]
            final_stop = stops[-1][7].split(":")[-1]
            init_stop_name = next((stop[1] for stop in metro_stop_info if stop[0] == init_stop), None)
            final_stop_name = next((stop[1] for stop in metro_stop_info if stop[0] == final_stop), None)

            if (init_stop_name, final_stop_name) not in temp_list and (final_stop_name, init_stop_name) not in temp_list:
                temp_list.append((init_stop_name, final_stop_name))
                new_trajet.append(idx)

        new_list_of_trajet.append(new_trajet)

    return new_list_of_trajet


def filter_similar_trips(rer_traject_per_line):
    """Filter RER trips to keep only unique terminus pairs."""
    rer_filtered_trips = {route_id: [] for route_id in rer_traject_per_line}

    for id in rer_traject_per_line:
        list_of_terminus = []
        trip_keys = []
        for trajet_n, list_of_trips in rer_traject_per_line[id].items():
            if not list_of_trips:
                continue
            pair_terminus = [list_of_trips[0][3], list_of_trips[-1][3]]
            if pair_terminus not in list_of_terminus:
                list_of_terminus.append(pair_terminus)
                trip_keys.append(trajet_n)
        rer_filtered_trips[id] = trip_keys
    return rer_filtered_trips


def get_RER_unique_station_ids_and_names(rer_traject_per_line, rer_filtered_trips, stops_data):
    """Extract unique RER station IDs and names from trajectory data."""
    unique_ids = {}
    
    for id, list_of_trip_keys in rer_filtered_trips.items():
        for trip_key in list_of_trip_keys:
            resolved_trip_key = trip_key if trip_key in rer_traject_per_line[id] else f"Trip: {trip_key}"
            if resolved_trip_key not in rer_traject_per_line[id]:
                continue
            for trip in rer_traject_per_line[id][resolved_trip_key]:
                if trip[3] not in unique_ids:
                    unique_ids[trip[3]] = set()
                unique_ids[trip[3]].add(id)

    rer_lines = get_rer_lines()
    RER_stop_data = []
    
    for id in unique_ids:
        rer_name = next((stop[1] for stop in stops_data if stop[0] == id), None)
        if rer_name:
            RER_stop_data.append([id, rer_name])
    
    RER_stop_data_with_line = []
    for stop in RER_stop_data:
        stop_id = stop[0]
        stop_name = stop[1]
        # Get wheelchair accessibility from stops_data
        stop_info = next((stop for stop in stops_data if stop[0] == stop_id), None)
        wheelchair = stop_info[2] if stop_info and len(stop_info) > 2 else 0
        
        lines = unique_ids[stop_id]
        for line in rer_lines:
            if line[0] in lines:
                RER_stop_data_with_line.append([stop_id, stop_name, line[2], wheelchair])

    return RER_stop_data, RER_stop_data_with_line


def get_rer_stop_data(stops_data=None):
    """
    Fetches RER station data for transfer connections using the DB service.
    """
    if stops_data is None:
        stops_data = get_all_stops()
    rer_trajects = get_detailed_rer_trips()
    
    # Use existing logic to filter similar trips
    rer_filtered_trips = filter_similar_trips(rer_trajects)
    
    # Get unique stations using existing logic
    rer_stop_data, rer_stop_data_with_line = get_RER_unique_station_ids_and_names(
        rer_trajects, rer_filtered_trips, stops_data
    )
    return rer_stop_data, rer_stop_data_with_line


def get_rer_connections(rer_stop_data):
    """Get RER connections with caching."""
    pkl_file = get_pickle_path("rer_connections.pkl")
    
    if os.path.exists(pkl_file):
        with open(pkl_file, "rb") as f:
            return pickle.load(f)
    
    rer_traject_per_line = get_detailed_rer_trips()
    rer_filtered_trips = filter_similar_trips(rer_traject_per_line)
    
    from app.functions.graph_builder import get_connections_per_rer
    rer_connections = get_connections_per_rer(rer_traject_per_line, rer_filtered_trips)
    
    # Cache the result
    with open(pkl_file, "wb") as f:
        pickle.dump(rer_connections, f)
    
    return rer_connections
