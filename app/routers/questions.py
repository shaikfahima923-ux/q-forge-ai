from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Question, QuestionVersion
from app.schemas.question import QuestionCreate, QuestionResponse

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
