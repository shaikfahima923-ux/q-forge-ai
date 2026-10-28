from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, QuestionVersion, ReviewDecision
from app.schemas.review import ReviewDecisionCreate, ReviewStatusResponse

router = APIRouter(
    prefix="/question-versions",
    tags=["Reviews"],
)


@router.post(
    "/{question_version_id}/decision",
    response_model=ReviewStatusResponse,
    status_code=status.HTTP_200_OK,
)
def submit_review_decision(
    question_version_id: int,
    payload: ReviewDecisionCreate,
    db: Session = Depends(get_db),
):
    version = (
        db.query(QuestionVersion)
        .filter(QuestionVersion.id == question_version_id)
        .first()
    )

    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question version not found.",
        )

    if version.is_immutable:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This question version is immutable and cannot be changed.",
        )

    old_status = version.status

    new_status = {
        "approved": "approved",
        "rejected": "rejected",
        "revision_required": "revision_required",
    }[payload.decision]

    try:
        version.status = new_status
        version.is_immutable = (payload.decision == "approved")

        decision_record = ReviewDecision(
            question_version_id=question_version_id,
            reviewer=payload.reviewer,
            decision=payload.decision,
            comments=payload.comments,
        )

        audit_record = AuditLog(
            question_version_id=question_version_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=payload.reviewer,
            reason=payload.comments,
        )

        db.add(decision_record)
        db.add(audit_record)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save the review decision.",
        )

    return ReviewStatusResponse(
        question_version_id=question_version_id,
        old_status=old_status,
        new_status=new_status,
        message=f"Review decision recorded: {payload.decision}.",
    )
