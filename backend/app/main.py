from __future__ import annotations

from dotenv import load_dotenv
load_dotenv()

from fastapi import Depends, WebSocket
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from prompt.routes import router as prompt_router
from user.routes import router as user_router
from api.routes import router as api_router
from agile.routes import router as agile_router
from api.routes import login_for_access_token, websocket_endpoint
from database import get_db, engine
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Instrumentator().instrument(app).expose(app)

# Include the routers of sub  modules
app.include_router(agile_router, prefix="/agile/api/v1")
app.include_router(api_router, prefix="/api/v1")
app.include_router(user_router, prefix="/user/api/v1")
app.include_router(prompt_router, prefix="/prompt/api/v1")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    return await login_for_access_token(form_data, db)

@app.websocket("/ws/{name}")
async def connect(websocket: WebSocket, name: str, token: str):
    return await websocket_endpoint(websocket, name, token)

@app.get("/", response_class=HTMLResponse)
async def release_notes(request: Request):
    features = [ ]
    return templates.TemplateResponse("index.html", {"request": request,
                                                    "features": features})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
