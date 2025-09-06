from fastapi import APIRouter, FastAPI
from .routers import auth, recipes
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

app = FastAPI()
app.include_router(auth.router) #connecting the authentication router to main
app.include_router(recipes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    # Redirect the root URL to the login page
    return RedirectResponse(url="/static/login.html")