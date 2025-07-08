import requests

# Get station coordinates
response = requests.get('http://127.0.0.1:8000/station_coordinates')
data = response.json()
stations = data['stations']

# Search for villejuif stations
villejuif_like = {k: v for k, v in stations.items() if 'vill' in k.lower()}
print('Stations with "vill" in name:')
for k, v in list(villejuif_like.items())[:10]:
    print(f'  {k}: {v}')

# Check the exact station names from the route
print('\nChecking exact station names from route:')
test_stations = [
    'Villejuif Paul Vaillant-Couturier',
    'Villejuif Léo Lagrange', 
    'Le Kremlin-Bicêtre',
    'Maison Blanche',
    'Tolbiac'
]

for station in test_stations:
    if station in stations:
        print(f'  ✓ {station}: {stations[station]}')
    else:
        print(f'  ✗ {station}: NOT FOUND')
        # Try to find similar names
        similar = [k for k in stations.keys() if station.lower().replace('-', ' ').replace("'", " ") in k.lower().replace('-', ' ').replace("'", " ") or k.lower().replace('-', ' ').replace("'", " ") in station.lower().replace('-', ' ').replace("'", " ")]
        if similar:
            print(f'    Similar: {similar}')
