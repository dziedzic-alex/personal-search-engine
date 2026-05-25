from fastapi import FastAPI

from api.routers import upload

app = FastAPI()

app.include_router(upload.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}