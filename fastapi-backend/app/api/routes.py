from fastapi import APIRouter, Request, HTTPException

from pydantic import BaseModel
from app.services.metro_service import get_trip, get_all_station_ids, get_stations_position, get_stops_position, get_lines_info, get_geojson, get_lines_id_relation

router = APIRouter()


class TripRequest(BaseModel):
    start: int
    end: int

@router.post("/calculate_trip")
async def calculate_trip_endpoint(request_body: TripRequest, request: Request):
    """
    Route API qui retourne ... 
    ------------------
    ...
    """
    data = request.app.state.metro_data
    return get_trip(
        request_body.start,
        request_body.end,
        data["graph"],
        data["metro_info"],
        data["filtered_metro_ids"]
    )

@router.get("/station_ids")
async def station_ids_endpoint(request: Request):
    """
    Route API qui retourne ... 
    ------------------
    ...
    """
    try:
        data = request.app.state.metro_data
        return get_all_station_ids(data["metro_info"], data["filtered_metro_ids"])
    except Exception as e:
        print("Error in /station_ids:", e)
        raise HTTPException(status_code=500, detail="Internal server error")


from app.services.metro_service import analyze_network_and_mst

"""@router.get("/analyze_network")
async def analyze_network_endpoint(request: Request):
    data = request.app.state.metro_data
    graph = data["graph"]
    metro_info = data["metro_info"]
    return analyze_network_and_mst(graph, metro_info)"""

@router.get("/analyze_network")
async def analyze_network_endpoint():
    return analyze_network_and_mst()



"""@router.get("/analyze_network")
async def analyze_network_endpoint(request: Request):
    data = request.app.state.metro_data
    graph = data["graph"]
    metro_info = data["metro_info"]
    return analyze_network_and_mst(graph, metro_info)"""

@router.get("/analyze_network")
async def analyze_network_endpoint():
    return analyze_network_and_mst()


'''@router.get("/stations/{line_number}")
async def stations_for_line_endpoint(line_number: int):
    """
    Route API qui retourne les stations du numéro de la ligne donnée en paramètre
    ------------------
    return: Json
        {
            "metro_line": <line_number>,
            "stations": 
            {
                ...
                {"id": <id>, "station": <nom de la station>, "line": <line_number>}
                ...
            }
        }
    """
    return get_stations_for_line(line_number)'''

"""
Routers de la map

"""

@router.get("/stations_position")
async def stations_position_endpoint():
    """
    Fonction qui retourne la position des stations de métro du fichier pospoints.txt
    ------------------
    return format:
    { 
        <metro line number (str)> : 
        {
            <Nom de la station (str)> : 
            {
                id: <station_id (int)>,
                x: <pos_x (int)>, 
                y: <pos_y (int)>,
                it: <number_of_iteration (int)>,
                out: 
                {
                    <station_id (int)>: <is_outside_line (bool)>
                },
                d: <degree (int)>
            }
        }
    }
    """
    return get_stations_position()

@router.get("/stops_position")
async def stops_position_endpoint():
    """
    Fonction qui retourne les localisations des stops/stations
    ------------------
    return format:
    {
        <stop_id (int)> : 
        {
            name: <stop_name (str)>,
            lat: <stop_latitude (float)>,
            long: <stop_longitude (float)>,
            prev: <previous_stop_id (int)>
        },
    }
    """
    return get_stops_position()

@router.get("/lines_info")
async def lines_info_endpoint():
    """
    Fonction qui retourne des informations utile sur toutes les lignes de transport
    ------------------
    return format:
    {
    Lines:
        {
            <line_name (str)>: 
                {
                    id: <line_id(int),
                    color: <line_color(str)>,
                    tcolor: <text_color(str)>,
                    type: <line_type_number(int)>,
                }
        }
    Types:
        {
            <line_type_number(int)>: <line_type_name(str)>
        }
    }
    """
    return get_lines_info()

@router.get("/metro_lines.geojson")
async def metro_line_geojson_endpoint():
    """
    Fonction qui retourne le geojson des lignes de métro
    ------------------
    return format:
    <file (dict)>
    """
    return get_geojson("traces-du-reseau-ferre-idf.geojson")

@router.get("/lines_id_name")
async def lines_id_relation():
    """
    Fonction qui retourne la realtion entre le nom des lignes et leur id
    ------------------
    return format:
    {
        <line_id (str)>: <line_name (str)>
    }
    """
    return get_lines_id_relation()