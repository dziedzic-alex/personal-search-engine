from sentence_transformers import CrossEncoder

# BAAI/bge-reranker-base
# cross-encoder/ms-marco-MiniLM-L-6-v2
MODEL_NAME = "BAAI/bge-reranker-base"
model: CrossEncoder | None = None


def get_cross_encoding_model() -> CrossEncoder:
    global model
    if model is None:
        model = CrossEncoder(MODEL_NAME)
    return model