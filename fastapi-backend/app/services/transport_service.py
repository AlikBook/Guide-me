from app.core.database import db_cursor

def get_all_stops():
    with db_cursor() as cursor:
        cursor.execute("SELECT stop_id, stop_name, wheelchair_int FROM stops")
        return [list(row) for row in cursor.fetchall()]

def get_transfers(metro_station_ids, rer_stop_data=None):
    all_ids = list(metro_station_ids)
    if rer_stop_data:
        all_ids.extend([s[0] for s in rer_stop_data])

    placeholders = ','.join(['?'] * len(all_ids))
    query = f"""
        SELECT from_stop_id, to_stop_id, min_transfer_time 
        FROM transfers 
        WHERE from_stop_id IN ({placeholders}) 
        AND to_stop_id IN ({placeholders})
    """
    
    with db_cursor() as cursor:
        cursor.execute(query, all_ids + all_ids)
        return [list(row) for row in cursor.fetchall()]

def get_rer_lines():
    query = """
        SELECT route_id, agency_id, route_short_name 
        FROM routes 
        WHERE agency_id = 'IDFM:71' AND route_id LIKE 'IDFM:C017%'
    """
    with db_cursor() as cursor:
        cursor.execute(query)
        return [list(row) for row in cursor.fetchall()]

def get_detailed_rer_trips():
    query = """
        SELECT t.route_id, st.trip_id, st.arrival_time, st.departure_time, st.stop_id
        FROM stop_times st
        JOIN trips t ON st.trip_id = t.trip_id
        WHERE t.route_id LIKE 'IDFM:C017%'
        ORDER BY t.route_id, st.trip_id, st.arrival_time
    """
    with db_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()

    # Data processing (Post-query)
    rer_trajects = {}
    for row in rows:
        r_id, t_id = row['route_id'], row['trip_id']
        if r_id not in rer_trajects:
            rer_trajects[r_id] = {}
        if t_id not in rer_trajects[r_id]:
            rer_trajects[r_id][t_id] = []
        rer_trajects[r_id][t_id].append([t_id, row['arrival_time'], row['departure_time'], row['stop_id']])
        
    return rer_trajects