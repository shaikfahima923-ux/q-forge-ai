
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.models import Question, QuestionVersion
from app.routers.questions import router as questions_router
from app.routers.reviews import router as reviews_router
from app.routers.exams import router as exams_router


def make_test_client():
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
    test_app.include_router(exams_router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    test_app.dependency_overrides[get_db] = override_get_db
    return TestClient(test_app), test_engine, TestingSessionLocal


def test_revision_creates_new_version_and_preserves_old_one():
    client, engine, session_local = make_test_client()
    try:
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
        original = response.json()["versions"][0]

        revision = client.post(
            f"/questions/{response.json()['id']}/revisions",
            json={
                "question_text": "What is 3 + 2?",
                "options": {"A": "4", "B": "5"},
                "correct_answer": "B",
                "explanation": "Three plus two equals five.",
            },
        )
        assert revision.status_code == 201

        versions = revision.json()["versions"]
        assert len(versions) == 2

        old_version = next(v for v in versions if v["id"] == original["id"])
        new_version = next(v for v in versions if v["id"] != original["id"])

        assert old_version["question_text"] == "What is 2 + 2?"
        assert new_version["question_text"] == "What is 3 + 2?"
        assert new_version["version_number"] == 2
        assert new_version["parent_version_id"] == original["id"]
        assert new_version["status"] == "draft"
        assert new_version["is_immutable"] is False
    finally:
        client.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_exam_questions_returns_only_approved_immutable_versions():
    client, engine, session_local = make_test_client()
    try:
        response = client.post(
            "/questions",
            json={
                "question_type": "MCQ",
                "difficulty": "Easy",
                "question_text": "Approved question?",
                "options": {"A": "Yes", "B": "No"},
                "correct_answer": "A",
            },
        )
        assert response.status_code == 201
        question = response.json()
        version_id = question["versions"][0]["id"]

        approval = client.post(
            f"/question-versions/{version_id}/decision",
            json={
                "reviewer": "test_reviewer",
                "decision": "approved",
                "comments": "Approved for exam",
            },
        )
        assert approval.status_code == 200

        # Add one draft version directly to the isolated test database.
        db = session_local()
        try:
            question_record = db.get(Question, question["id"])
            draft = QuestionVersion(
                question_id=question_record.id,
                parent_version_id=version_id,
                version_number=2,
                question_text="Draft question?",
                options={"A": "Yes", "B": "No"},
                correct_answer="A",
                status="draft",
                regeneration_count=1,
                is_immutable=False,
            )
            db.add(draft)
            db.commit()
        finally:
            db.close()

        exam_response = client.get("/exam-questions")
        assert exam_response.status_code == 200

        exam_versions = exam_response.json()
        assert len(exam_versions) == 1
        assert exam_versions[0]["id"] == version_id
        assert exam_versions[0]["status"] == "approved"
        assert exam_versions[0]["is_immutable"] is True
    finally:
        client.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
