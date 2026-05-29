from sentence_transformers import SentenceTransformer

MODEL_NAME = 'clip-ViT-B-32'
model: SentenceTransformer | None = None

def get_image_embedding_model() -> SentenceTransformer:
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model