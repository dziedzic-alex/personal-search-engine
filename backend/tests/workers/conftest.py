import pytest


@pytest.fixture
def mock_worker_session(mocker):
    session = mocker.MagicMock()
    session.__enter__ = mocker.Mock(return_value=session)
    session.__exit__ = mocker.Mock(return_value=False)
    return session


@pytest.fixture
def mock_image_session(mocker, mock_worker_session):
    mocker.patch("workers.image.image.SessionLocal", return_value=mock_worker_session)
    return mock_worker_session


@pytest.fixture
def mock_pdf_session(mocker, mock_worker_session):
    mocker.patch("workers.pdf.pdf.SessionLocal", return_value=mock_worker_session)
    return mock_worker_session


@pytest.fixture
def mock_pdf_utils_session(mocker, mock_worker_session):
    mocker.patch("workers.pdf.pdf_utils.SessionLocal", return_value=mock_worker_session)
    return mock_worker_session


@pytest.fixture
def mock_image_utils_session(mocker, mock_worker_session):
    mocker.patch(
        "workers.image.image_utils.SessionLocal", return_value=mock_worker_session
    )
    return mock_worker_session


@pytest.fixture
def mock_embedding_models(mocker):
    text_model = mocker.MagicMock()
    image_model = mocker.MagicMock()

    def fake_text_encode(data):
        if isinstance(data, str):
            return [0.1] * 384
        return [[0.1] * 384 for _ in data]

    text_model.encode.side_effect = fake_text_encode
    image_model.encode.return_value = [0.2] * 512

    mocker.patch(
        "workers.image.image.get_text_embedding_model", return_value=text_model
    )
    mocker.patch(
        "workers.image.image.get_image_embedding_model", return_value=image_model
    )
    mocker.patch("workers.pdf.pdf.get_text_embedding_model", return_value=text_model)

    return text_model, image_model
