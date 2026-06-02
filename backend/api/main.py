from fastapi import FastAPI
from shared.models.text_embedding import get_text_embedding_model
from shared.models.image_embedding import get_image_embedding_model
from shared.redis_client import get_redis_client
from api.routers import upload
from api.routers import search

get_text_embedding_model()
get_image_embedding_model()
get_redis_client()

app = FastAPI()

app.include_router(upload.router)
app.include_router(search.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
