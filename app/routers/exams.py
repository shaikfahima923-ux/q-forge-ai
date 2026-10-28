from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Question, QuestionVersion
from app.schemas.question import QuestionVersionResponse

router = APIRouter(prefix="/exam-questions", tags=["Exams"])


@router.get("", response_model=list[QuestionVersionResponse])
def get_exam_questions(
    topic_id: int | None = None,
    difficulty: str | None = None,
    question_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = (
        db.query(QuestionVersion)
        .join(Question, Question.id == QuestionVersion.question_id)
        .filter(
            QuestionVersion.status == "approved",
            QuestionVersion.is_immutable.is_(True),
        )
    )

    if topic_id is not None:
        query = query.filter(Question.topic_id == topic_id)

    if difficulty is not None:
        query = query.filter(Question.difficulty == difficulty)

    if question_type is not None:
        query = query.filter(Question.question_type == question_type)

    return query.order_by(QuestionVersion.id.asc()).all()