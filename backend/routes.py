from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()

@router.post('/api/download')
def download_episode(request: Request):
    # Placeholder: implement download logic
    return JSONResponse({'status': 'Download started'})
