from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from src.config.db import get_supabase, check_if_user_exists

# supclient = await get_supabase() # to be used inside async functions

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get('/about')
def home(request: Request):
    return templates.TemplateResponse("about.html", { 'request': request})