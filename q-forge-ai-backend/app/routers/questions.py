

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Question, QuestionVersion
from app.schemas.question import (
    QuestionCreate,
    QuestionResponse,
    QuestionVersionResponse,
)

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("", response_model=QuestionVersionResponse, status_code=201)
def create_question(payload: QuestionCreate, db: Session = Depends(get_db)):
    try:
        question = Question(
            topic_id=payload.topic_id,
            question_type=payload.question_type,
            difficulty=payload.difficulty,
            source_filename=payload.source_filename,
        )

        db.add(question)
        db.flush()

        version = QuestionVersion(
            question_id=question.id,
            version_number=1,
            question_text=payload.question_text,
            options=payload.options,
            correct_answer=payload.correct_answer,
            explanation=payload.explanation,
            status="draft",
            regeneration_count=0,
            is_immutable=False,
        )

        db.add(version)
        db.commit()
        db.refresh(version)

        return version

    except Exception:
        db.rollback()
        raise


@router.get("", response_model=list[QuestionResponse])
def get_questions(db: Session = Depends(get_db)):
    return db.query(Question).order_by(Question.id.desc()).all()


@router.get(
    "/versions/{version_id}",
    response_model=QuestionVersionResponse,
)
def get_question_version(version_id: int, db: Session = Depends(get_db)):
    version = db.query(QuestionVersion).filter(
        QuestionVersion.id == version_id
    ).first()

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="Question version not found",
        )

    return version


@router.post(
    "/versions/{version_id}/submit-for-review",
    response_model=QuestionVersionResponse,
)
def submit_for_review(version_id: int, db: Session = Depends(get_db)):
    version = db.query(QuestionVersion).filter(
        QuestionVersion.id == version_id
    ).first()

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="Question version not found",
        )

    if version.is_immutable:
        raise HTTPException(
            status_code=403,
            detail="Approved question versions cannot be modified",
        )

    if version.status not in ("draft", "revision_required"):
        raise HTTPException(
            status_code=400,
            detail="Only draft or revision-required versions can be submitted",
        )

    version.status = "human_review"
    db.commit()
    db.refresh(version)

    return version
