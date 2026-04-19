import sqlite3
import os

# Path Configuration
V2_TEXT_FILES_DIR = os.path.join(os.path.dirname(__file__), "..", "V2_text_files")
DATABASE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "database")
DB_PATH = os.path.join(DATABASE_DIR, "transport_data.db")

if not os.path.exists(DATABASE_DIR):
    os.makedirs(DATABASE_DIR)
    print(f"Created directory: {DATABASE_DIR}")

def get_v2_file_path(filename):
    return os.path.join(V2_TEXT_FILES_DIR, filename)

def migrate_to_sqlite():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. DROP AND CREATE TABLES
    print("Initializing Database Schema...")
    cursor.execute('DROP TABLE IF EXISTS stops')
    cursor.execute('CREATE TABLE stops (stop_id TEXT PRIMARY KEY, stop_name TEXT, wheelchair_int INTEGER)')
    
    cursor.execute('DROP TABLE IF EXISTS stop_times')
    cursor.execute('CREATE TABLE stop_times (trip_id TEXT, arrival_time TEXT, departure_time TEXT, stop_id TEXT)')

    cursor.execute('DROP TABLE IF EXISTS trips')
    cursor.execute('CREATE TABLE trips (route_id TEXT, service_id TEXT, trip_id TEXT PRIMARY KEY, trip_headsign TEXT)')

    cursor.execute('DROP TABLE IF EXISTS routes')
    cursor.execute('CREATE TABLE routes (route_id TEXT PRIMARY KEY, agency_id TEXT, route_short_name TEXT, route_type INTEGER)')

    cursor.execute('DROP TABLE IF EXISTS transfers')
    cursor.execute('CREATE TABLE transfers (from_stop_id TEXT, to_stop_id TEXT, transfer_type INTEGER, min_transfer_time INTEGER)')

    # 2. MIGRATE STOPS
    print("Migrating stops.txt...")
    with open(get_v2_file_path("stops.txt"), "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx_id, idx_name = header.index("stop_id"), header.index("stop_name")
        idx_wheel = header.index("wheelchair_boarding") if "wheelchair_boarding" in header else -1
        
        data = []
        for line in f:
            p = line.strip().split(",")
            if len(p) < 2: continue
            wheelchair = int(p[idx_wheel]) if idx_wheel != -1 and p[idx_wheel].isdigit() else 0
            data.append((p[idx_id].split(":")[-1], p[idx_name], wheelchair))
        cursor.executemany("INSERT OR REPLACE INTO stops VALUES (?,?,?)", data)

    # 3. MIGRATE ROUTES
    print("Migrating routes.txt...")
    with open(get_v2_file_path("routes.txt"), "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx_rid = header.index("route_id")
        idx_aid = header.index("agency_id")
        idx_name = header.index("route_short_name")
        
        data = []
        for line in f:
            p = line.strip().split(",")
            data.append((p[idx_rid], p[idx_aid], p[idx_name], 1)) # 1 for Metro/RER
        cursor.executemany("INSERT OR REPLACE INTO routes VALUES (?,?,?,?)", data)

    # 4. MIGRATE TRIPS
    print("Migrating trips.txt...")
    with open(get_v2_file_path("trips.txt"), "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx_rid, idx_sid, idx_tid = header.index("route_id"), header.index("service_id"), header.index("trip_id")
        idx_head = header.index("trip_headsign")
        
        data = []
        for line in f:
            p = line.strip().split(",")
            data.append((p[idx_rid], p[idx_sid], p[idx_tid].split(":")[-1], p[idx_head]))
        cursor.executemany("INSERT OR REPLACE INTO trips VALUES (?,?,?,?)", data)

    # 5. MIGRATE STOP_TIMES (Filtered for RATP/RER)
    print("Migrating stop_times.txt (Large file)...")
    with open(get_v2_file_path("stop_times.txt"), "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx_tid, idx_arr, idx_dep, idx_sid = header.index("trip_id"), header.index("arrival_time"), header.index("departure_time"), header.index("stop_id")
        
        batch = []
        for line in f:
            if "IDFM:RATP" in line or "IDFM:C017" in line:
                p = line.strip().split(",")
                batch.append((p[idx_tid].split(":")[-1], p[idx_arr], p[idx_dep], p[idx_sid].split(":")[-1]))
                if len(batch) >= 20000:
                    cursor.executemany("INSERT INTO stop_times VALUES (?,?,?,?)", batch)
                    batch = []
        cursor.executemany("INSERT INTO stop_times VALUES (?,?,?,?)", batch)

    # 6. MIGRATE TRANSFERS
    print("Migrating transfers.txt...")
    with open(get_v2_file_path("transfers.txt"), "r", encoding="utf-8") as f:
        header = f.readline().strip().split(",")
        idx_from, idx_to = header.index("from_stop_id"), header.index("to_stop_id")
        idx_type, idx_time = header.index("transfer_type"), header.index("min_transfer_time")
        
        data = []
        for line in f:
            p = line.strip().split(",")
            data.append((p[idx_from].split(":")[-1], p[idx_to].split(":")[-1], p[idx_type], p[idx_time]))
        cursor.executemany("INSERT INTO transfers VALUES (?,?,?,?)", data)

    # 7. CREATE INDEXES (CRITICAL FOR PERFORMANCE)
    print("Creating database indexes...")
    cursor.execute("CREATE INDEX idx_st_trip ON stop_times(trip_id)")
    cursor.execute("CREATE INDEX idx_st_stop ON stop_times(stop_id)")
    cursor.execute("CREATE INDEX idx_trips_route ON trips(route_id)")
    cursor.execute("CREATE INDEX idx_transfers_from ON transfers(from_stop_id)")

    conn.commit()
    conn.close()
    print(f"Migration successful! Database stored at: {DB_PATH}")

if __name__ == "__main__":
    migrate_to_sqlite()