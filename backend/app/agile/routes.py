from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from agile.forms import AgileForm
router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/test", response_class=HTMLResponse)
async def test(request: Request):
    form = AgileForm()
    return templates.TemplateResponse("test.html", {"request": request, "form": form})