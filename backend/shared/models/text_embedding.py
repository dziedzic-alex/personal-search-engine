from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
model: SentenceTransformer | None = None


def get_text_embedding_model() -> SentenceTransformer:
    global model
    if model is None:
        model = SentenceTransformer(MODEL_NAME)
    return model
