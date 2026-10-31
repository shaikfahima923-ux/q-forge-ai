
from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    topic_id: int | None = None

    question_type: Literal["MCQ", "MSQ", "Assertion", "Reasoning"]
    difficulty: Literal["Easy", "Moderate", "Difficult"]

    source_filename: str | None = None
    question_text: str = Field(min_length=1)
    options: dict[str, Any] | list[Any] | None = None
    correct_answer: str | list[str] | None = None
    explanation: str | None = None


class QuestionVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    parent_version_id: int | None
    version_number: int
    question_text: str
    options: dict[str, Any] | list[Any] | None
    correct_answer: str | list[str] | None
    explanation: str | None
    status: str
    regeneration_count: int
    is_immutable: bool
    created_at: datetime


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int | None
    question_type: str
    difficulty: str
    source_filename: str | None
    created_at: datetime
