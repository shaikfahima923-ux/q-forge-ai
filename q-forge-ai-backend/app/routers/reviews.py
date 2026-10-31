
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import QuestionVersion, ReviewDecision, AuditLog
from app.schemas.review import (
    ReviewDecisionCreate,
    ReviewDecisionResponse,
    ReviewStatusResponse,
)

router = APIRouter(tags=["Reviews"])


@router.post(
    "/question-versions/{version_id}/decision",
    response_model=ReviewStatusResponse,
)
def make_review_decision(
    version_id: int,
    payload: ReviewDecisionCreate,
    db: Session = Depends(get_db),
):
    version = db.query(QuestionVersion).filter(
        QuestionVersion.id == version_id
    ).first()

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="Question version not found",
        )

    # Check immutability before checking the review status
    if version.is_immutable:
        raise HTTPException(
            status_code=409,
            detail="Approved question versions cannot be changed",
        )

    if version.status != "human_review":
        raise HTTPException(
            status_code=400,
            detail="Only questions awaiting human review can receive a decision",
        )

    old_status = version.status
    new_status = payload.decision

    try:
        decision = ReviewDecision(
            question_version_id=version_id,
            reviewer=payload.reviewer,
            decision=payload.decision,
            comments=payload.comments,
        )

        version.status = new_status
        version.is_immutable = new_status == "approved"

        audit = AuditLog(
            question_version_id=version_id,
            old_status=old_status,
            new_status=new_status,
            changed_by=payload.reviewer,
            reason=payload.comments,
        )

        db.add(decision)
        db.add(audit)
        db.commit()

        return ReviewStatusResponse(
            question_version_id=version_id,
            old_status=old_status,
            new_status=new_status,
            message=f"Question review completed: {new_status}",
        )

    except Exception:
        db.rollback()
        raise


@router.get(
    "/question-versions/{version_id}/decisions",
    response_model=list[ReviewDecisionResponse],
)
def get_review_decisions(
    version_id: int,
    db: Session = Depends(get_db),
):
    version = db.query(QuestionVersion).filter(
        QuestionVersion.id == version_id
    ).first()

    if version is None:
        raise HTTPException(
            status_code=404,
            detail="Question version not found",
        )

    return (
        db.query(ReviewDecision)
        .filter(ReviewDecision.question_version_id == version_id)
        .order_by(ReviewDecision.id.desc())
        .all()
    )
