from fastapi import FastAPI
from src.routes.whatsapp_webhook import router as whatsapp_router
from src.services.cronjob import *
#################
from src.routes.auth import router as auth_router
from src.routes.about import router as about_router
from src.routes.guidelines import router as guidelines_router
from src.routes.dashboard import router as dashboard_router

app = FastAPI()

app.include_router(whatsapp_router)
app.include_router(auth_router)
app.include_router(about_router)
app.include_router(guidelines_router)
app.include_router(dashboard_router)
############
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

################################################################################

