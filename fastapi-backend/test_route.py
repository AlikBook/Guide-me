import requests
import json

# Get station IDs
response = requests.get('http://127.0.0.1:8000/station_ids')
data = response.json()['stations']

# Search for stations
chatillon_stations = [s for s in data if 'châtill' in s['station'].lower() or 'montrouge' in s['station'].lower()]
villejuif_stations = [s for s in data if 'villejuif' in s['station'].lower()]

print("Châtillon/Montrouge stations:")
for s in chatillon_stations:
    print(f"  ID {s['id']}: {s['station']} on {s['line']}")

print("\nVillejuif stations:")
for s in villejuif_stations:
    print(f"  ID {s['id']}: {s['station']} on {s['line']}")

# Test route calculation if we find stations
if chatillon_stations and villejuif_stations:
    start_id = chatillon_stations[0]['id']
    end_id = villejuif_stations[0]['id']
    
    print(f"\nTesting route from {chatillon_stations[0]['station']} (ID: {start_id}) to {villejuif_stations[0]['station']} (ID: {end_id})")
    
    route_response = requests.post('http://127.0.0.1:8000/calculate_trip', 
                                  json={'start': int(start_id), 'end': int(end_id), 'actual_time': '08:30:00'})
    
    print(f"Route calculation status: {route_response.status_code}")
    if route_response.status_code == 200:
        route_data = route_response.json()
        print("Route data keys:", list(route_data.keys()))
        
        if 'trips' in route_data:
            trips = route_data['trips']
            print(f"Number of trips found: {len(trips)}")
            if trips:
                first_trip = trips[0]
                print(f"First trip keys: {list(first_trip.keys())}")
                print(f"First trip: time={first_trip.get('time', 'N/A')} min")
                
                if 'stations' in first_trip:
                    print("Stations in trip:")
                    stations = first_trip['stations']
                    print(f"Number of segments: {len(stations)}")
                    for i, segment in enumerate(stations):
                        print(f"  Segment {i+1}:")
                        for line_key, stations_list in segment.items():
                            if isinstance(stations_list, list) and stations_list:
                                station_names = [st.get('station', 'Unknown') for st in stations_list]
                                print(f"    {line_key}: {' -> '.join(station_names)}")
                                
        # Let's also test with Châtillon-Montrouge to Villejuif
        print(f"\n" + "="*50)
        start_id = 434  # Châtillon-Montrouge on Metro 13
        end_id = 187   # Villejuif Paul Vaillant-Couturier on Metro 7
        
        print(f"Testing route from Châtillon-Montrouge (ID: {start_id}) to Villejuif Paul Vaillant-Couturier (ID: {end_id})")
        
        route_response2 = requests.post('http://127.0.0.1:8000/calculate_trip', 
                                       json={'start': start_id, 'end': end_id, 'actual_time': '08:30:00'})
        
        if route_response2.status_code == 200:
            route_data2 = route_response2.json()
            if 'trips' in route_data2 and route_data2['trips']:
                trip = route_data2['trips'][0]
                print(f"Route time: {trip.get('time', 'N/A')} min")
                print(f"Route stations structure:")
                import json
                print(json.dumps(trip.get('stations', []), indent=2, ensure_ascii=False))
    else:
        print(f"Error: {route_response.text}")
