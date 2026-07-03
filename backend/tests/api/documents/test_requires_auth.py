import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.documents.documents import router as documents_router

DOCUMENT_ROUTES = [
    pytest.param("post", "/documents/list", {"json": {"page": 0}}, id="list"),
    pytest.param(
        "get",
        "/documents/search",
        {"params": {"query": "test", "search_mode": "text"}},
        id="search",
    ),
    pytest.param(
        "post",
        "/documents/",
        {"files": [("files", ("test.pdf", b"pdf content", "application/pdf"))]},
        id="upload",
    ),
    pytest.param(
        "patch",
        "/documents/1",
        {"json": {"name": "test.pdf"}},
        id="update",
    ),
    pytest.param("delete", "/documents/1", {}, id="delete"),
]


@pytest.fixture
def unauthenticated_documents_client():
    app = FastAPI()
    app.include_router(documents_router)
    return TestClient(app)


@pytest.mark.parametrize("method, path, kwargs", DOCUMENT_ROUTES)
def test_document_routes_require_auth(
    unauthenticated_documents_client, method, path, kwargs
):
    response = getattr(unauthenticated_documents_client, method)(path, **kwargs)

    assert response.status_code == 401
