from fastapi import FastAPI

from api.routers import upload
from api.routers import search

app = FastAPI()

app.include_router(upload.router)
app.include_router(search.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}