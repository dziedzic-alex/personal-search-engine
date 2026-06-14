from sentence_transformers import CrossEncoder

MODEL_NAME = "BAAI/bge-reranker-base"
model: CrossEncoder | None = None


def get_cross_encoding_model() -> CrossEncoder:
    global model
    if model is None:
        model = CrossEncoder(MODEL_NAME)
    return model
