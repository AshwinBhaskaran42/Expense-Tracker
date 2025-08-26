from fastapi import FastAPI
from src.routes.whatsapp_webhook import router as whatsapp_router
from src.services.cronjob import *

app = FastAPI()

app.include_router(whatsapp_router)
# @app.get('/', response_class=HTMLResponse)
# async def home():
#     with open("home.html", "r") as f:
#         home_content= f.read()
#     return HTMLResponse(content=home_content)

# @app.get('/about', response_class=HTMLResponse)
# async def about():
#     with open("about.html", "r") as f1:
#         about_content= f1.read()
#     return HTMLResponse(content=about_content)
