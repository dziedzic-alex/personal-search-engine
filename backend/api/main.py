from fastapi import FastAPI
from pillow_heif import register_heif_opener

from api.routers import documents
from api.routers.auth.auth import router as auth_router
from api.routers.upload.upload import router as upload_router
from shared.models.cross_encoding import get_cross_encoding_model
from shared.models.image_embedding import get_image_embedding_model
from shared.models.text_embedding import get_text_embedding_model
from shared.redis_client import get_redis_client
from shared.s3_client import get_s3_client

get_text_embedding_model()
get_image_embedding_model()
get_cross_encoding_model()
get_redis_client()
register_heif_opener()
get_s3_client()

app = FastAPI()

app.include_router(auth_router)
app.include_router(upload_router)
app.include_router(documents.router)


@app.get("/")
def read_root():
    return {"Hello": "World"}
