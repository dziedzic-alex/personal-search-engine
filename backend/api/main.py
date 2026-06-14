from fastapi import FastAPI

from api.routers import search
from api.routers.upload.upload import router as upload_router
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from shared.models.cross_encoding import get_cross_encoding_model
from shared.redis_client import get_redis_client

get_text_embedding_model()
get_image_embedding_model()
get_cross_encoding_model()
get_redis_client()

app = FastAPI()

app.include_router(upload_router)
app.include_router(search.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
