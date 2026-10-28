
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


QuestionType = Literal[
    "MCQ",
    "MSQ",
    "Assertion-Reasoning",
    "Reasoning",
]

Difficulty = Literal["Easy", "Moderate", "Difficult"]

QuestionStatus = Literal[
    "draft",
    "revision_required",
    "human_review",
    "approved",
    "rejected",
]


class QuestionCreate(BaseModel):
    topic_id: int | None = None
    question_type: QuestionType
    difficulty: Difficulty
    source_filename: str | None = Field(default=None, max_length=255)
    question_text: str = Field(min_length=1)
    options: dict[str, Any] | list[Any] | None = None
    correct_answer: str | list[str] | None = None
    explanation: str | None = None
    status: QuestionStatus = "draft"


class QuestionVersionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    parent_version_id: int | None
    version_number: int
    question_text: str
    options: dict[str, Any] | list[Any] | None
    correct_answer: Any
    explanation: str | None
    status: str
    regeneration_count: int
    is_immutable: bool


class QuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    topic_id: int | None
    question_type: str
    difficulty: str
    source_filename: str | None
    versions: list[QuestionVersionResponse]

class QuestionRevisionCreate(BaseModel):
    question_text: str = Field(min_length=1)
    options: dict[str, Any] | list[Any] | None = None
    correct_answer: str | list[str] | None = None
    explanation: str | None = None
