from fastapi import APIRouter
from fastapi.responses import JSONResponse


router = APIRouter()


@router.get("/")
def root():
    return JSONResponse(content={"message": "Hello World!"})


@router.get("/health")
def health():
    return JSONResponse(content={"status": "ok"})
