import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.database import Base, get_db
from app.models import AuditLog, Question, QuestionVersion, ReviewDecision
from app.routers.questions import router as questions_router
from app.routers.reviews import router as reviews_router


@pytest.fixture
def client():
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    Base.metadata.create_all(bind=test_engine)

    test_app = FastAPI()
    test_app.include_router(questions_router)
    test_app.include_router(reviews_router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db

    with TestClient(test_app) as test_client:
        yield test_client

    test_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)
    test_engine.dispose()



def test_approval_makes_version_immutable(client):
    response = client.post(
        "/questions",
        json={
            "question_type": "MCQ",
            "difficulty": "Easy",
            "question_text": "What is 2 + 2?",
            "options": {"A": "3", "B": "4"},
            "correct_answer": "B",
        },
    )
    assert response.status_code == 201
    version_id = response.json()["versions"][0]["id"]

    approval = client.post(
        f"/question-versions/{version_id}/decision",
        json={
            "reviewer": "test_reviewer",
            "decision": "approved",
            "comments": "Automated approval test",
        },
    )
    assert approval.status_code == 200
    assert approval.json()["new_status"] == "approved"

    second_decision = client.post(
        f"/question-versions/{version_id}/decision",
        json={
            "reviewer": "test_reviewer",
            "decision": "rejected",
            "comments": "This should be blocked",
        },
    )
    assert second_decision.status_code == 409


def test_missing_version_returns_404(client):
    response = client.post(
        "/question-versions/99999/decision",
        json={
            "reviewer": "test_reviewer",
            "decision": "approved",
            "comments": "Missing version test",
        },
    )
    assert response.status_code == 404
