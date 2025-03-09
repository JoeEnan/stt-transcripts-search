from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["health"])


"""
Task 2ai:
GET /health: Returns the status of the service.
Assumptions:
    - Simply return {"status": "OK"} to ensure FastAPI server is running
"""
@router.get("/health")
async def health_check():
    return {"status": "OK"}
