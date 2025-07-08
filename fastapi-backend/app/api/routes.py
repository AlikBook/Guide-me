from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.services.metro_service import get_trip, get_all_station_ids, analyze_network_and_mst
from app.core.auto_build import check_yen_wrapper_available
import platform

router = APIRouter()

class TripRequest(BaseModel):
    start: int
    end: int
    actual_time: str = "8:30:00"  # Default time if not provided

@router.post("/calculate_trip")
async def calculate_trip_endpoint(request_body: TripRequest, request: Request):
    try:
        data = request.app.state.metro_data
        return get_trip(request_body.start, request_body.end, data, request_body.actual_time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/station_ids")
async def station_ids_endpoint(request: Request):
    try:
        data = request.app.state.metro_data
        return get_all_station_ids(data)
    except Exception as e:
        print("Error in /station_ids:", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/analyze_network")
async def analyze_network_endpoint(request: Request):
    try:
        data = request.app.state.metro_data
        return analyze_network_and_mst(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system_status")
async def system_status_endpoint(request: Request):
    """Get system status including C extension availability."""
    try:
        yen_available = getattr(request.app.state, 'yen_available', check_yen_wrapper_available())
        
        status = {
            "status": "ok",
            "c_extension_available": yen_available,
            "performance_mode": "high" if yen_available else "compatibility",
            "platform": {
                "system": platform.system(),
                "machine": platform.machine(),
                "python_version": platform.python_version()
            },
            "message": "High-performance pathfinding enabled" if yen_available else 
                      "Running in compatibility mode - consider building C extension for better performance"
        }
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/build_extension")
async def build_extension_endpoint():
    """Manually trigger C extension build."""
    try:
        from app.core.auto_build import auto_build_yen_wrapper
        
        print("🔨 Manual C extension build triggered...")
        success = auto_build_yen_wrapper()
        
        if success:
            return {
                "status": "success", 
                "message": "C extension built successfully",
                "performance_mode": "high"
            }
        else:
            return {
                "status": "failed",
                "message": "C extension build failed - see server logs for details",
                "performance_mode": "compatibility"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Build error: {str(e)}")