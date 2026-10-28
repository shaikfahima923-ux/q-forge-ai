from typing import Literal

from pydantic import BaseModel, Field


class ReviewDecisionCreate(BaseModel):
    reviewer: str = Field(min_length=1, max_length=100)
    decision: Literal["approved", "rejected", "revision_required"]
    comments: str | None = None


class ReviewDecisionResponse(BaseModel):
    id: int
    question_version_id: int
    reviewer: str
    decision: str
    comments: str | None = None


class ReviewStatusResponse(BaseModel):
    question_version_id: int
    old_status: str | None
    new_status: str
    message: str
