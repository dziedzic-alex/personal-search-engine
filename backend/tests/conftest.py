import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from api.routers import search
from api.routers.upload.upload import router as upload_router
from db.session import get_session


@pytest.fixture
def upload_client(mocker, tmp_path):
    mocker.patch("api.routers.upload.upload.UPLOAD_DIR", tmp_path)

    mock_session = mocker.MagicMock()
    next_document_id = 1

    def assign_document_id(document):
        nonlocal next_document_id
        document.id = next_document_id
        next_document_id += 1

    mock_session.add.side_effect = assign_document_id
    mock_session.__enter__ = mocker.Mock(return_value=mock_session)
    mock_session.__exit__ = mocker.Mock(return_value=False)

    mocker.patch("api.routers.upload.upload.SessionLocal", return_value=mock_session)

    mock_redis = mocker.MagicMock()
    mocker.patch("api.routers.upload.upload.get_redis_client", return_value=mock_redis)

    app = FastAPI()
    app.include_router(upload_router)

    return TestClient(app), mock_session, mock_redis


@pytest.fixture
def search_client(mocker):
    mock_session = mocker.MagicMock()

    def override_get_session():
        yield mock_session

    mocker.patch(
        "api.routers.search.DocumentRepository.get_relevant_documents",
        return_value=[],
    )

    app = FastAPI()
    app.include_router(search.router)
    app.dependency_overrides[get_session] = override_get_session

    return TestClient(app)
