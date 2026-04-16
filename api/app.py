import uvicorn

from fastapi import FastAPI

from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware
from api.security import SecurityHeadersMiddleware

from api.routes._root import router as root_router
from api.database import PG_DATABASE_URL


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[],
    allow_methods=[],
    allow_headers=[],
)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1"]
)

app.include_router(root_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
