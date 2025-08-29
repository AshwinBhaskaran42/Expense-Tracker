from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from util_functions.handle_otp_jwt import get_loggedin_user

templates = Jinja2Templates(directory='templates')

router = APIRouter()

@router.get('/dashboard', response_class=HTMLResponse) #
async def dashboard(request: Request): 
    user, new_access = await get_loggedin_user(request)
    if not user:
        return RedirectResponse("/login")
    
    # ADD THE BUSINESS LOGIC 
    
    response =  templates.TemplateResponse("dashboard.html", {"request": request, "user": user})

    # Attach cookie to the actual response:
    if new_access:
        response.set_cookie("access_token", new_access, httponly=True, samesite="lax", max_age=3600)
    return response

    

    