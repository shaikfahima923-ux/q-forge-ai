
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Question, QuestionVersion
from app.schemas.question import QuestionCreate, QuestionResponse, QuestionRevisionCreate

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post(
    "",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
):
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
            status=payload.status,
        )
        db.add(version)
        db.commit()
        db.refresh(question)

        return question

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the question. Check the server logs.",
        )

@router.post(
    "/{question_id}/revisions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_question_revision(
    question_id: int,
    payload: QuestionRevisionCreate,
    db: Session = Depends(get_db),
):
    question = db.query(Question).filter(Question.id == question_id).first()

    if question is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found.",
        )

    latest_version = (
        db.query(QuestionVersion)
        .filter(QuestionVersion.question_id == question_id)
        .order_by(
            QuestionVersion.version_number.desc(),
            QuestionVersion.id.desc(),
        )
        .first()
    )

    if latest_version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existing version found for this question.",
        )

    try:
        new_version = QuestionVersion(
            question_id=question_id,
            parent_version_id=latest_version.id,
            version_number=latest_version.version_number + 1,
            question_text=payload.question_text,
            options=payload.options,
            correct_answer=payload.correct_answer,
            explanation=payload.explanation,
            status="draft",
            regeneration_count=latest_version.regeneration_count + 1,
            is_immutable=False,
        )

        db.add(new_version)
        db.commit()
        db.refresh(question)
        return question

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create the question revision.",
        )
