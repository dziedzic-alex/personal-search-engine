import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers.documents.documents import router as documents_router
from tests.api.factories import uid

DOCUMENT_ROUTES = [
    pytest.param("post", "/documents/list", {"json": {"page": 0}}, id="list"),
    pytest.param(
        "post",
        "/documents/by-ids",
        {"json": {"documentIds": [str(uid(1))]}},
        id="by-ids",
    ),
    pytest.param(
        "get",
        "/documents/search",
        {"params": {"query": "test", "search_mode": "text"}},
        id="search",
    ),
    pytest.param(
        "get",
        "/documents/search/v2",
        {"params": {"query": "test"}},
        id="search-v2",
    ),
    pytest.param(
        "get",
        "/documents/suggest",
        {"params": {"query": "test"}},
        id="suggest",
    ),
    pytest.param(
        "post",
        "/documents/",
        {"files": [("files", ("test.pdf", b"pdf content", "application/pdf"))]},
        id="upload",
    ),
    pytest.param(
        "post",
        "/documents/v2",
        {"files": [("files", ("test.pdf", b"pdf content", "application/pdf"))]},
        id="upload-v2",
    ),
    pytest.param(
        "patch",
        f"/documents/{uid(1)}",
        {"json": {"name": "test.pdf"}},
        id="update",
    ),
    pytest.param("delete", f"/documents/{uid(1)}", {}, id="delete"),
    pytest.param(
        "delete",
        "/documents/bulk-delete",
        {},
        id="bulk-delete",
    ),
    pytest.param(
        "post",
        "/documents/bulk-download",
        {"json": {"documentIds": [str(uid(1)), str(uid(2))]}},
        id="bulk-download",
    ),
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
