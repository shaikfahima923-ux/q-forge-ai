
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    topic_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    question_type: Mapped[str] = mapped_column(String(40), nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False)
    source_filename: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    versions: Mapped[list["QuestionVersion"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )


class QuestionVersion(Base):
    __tablename__ = "question_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question_id: Mapped[int] = mapped_column(
        ForeignKey("questions.id"), nullable=False, index=True
    )
    parent_version_id: Mapped[int | None] = mapped_column(
        ForeignKey("question_versions.id"), nullable=True
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[dict | list | None] = mapped_column(JSON, nullable=True)
    correct_answer: Mapped[str | list | None] = mapped_column(JSON, nullable=True)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="draft"
    )
    regeneration_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    is_immutable: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )

    question: Mapped["Question"] = relationship(back_populates="versions")
    parent_version: Mapped["QuestionVersion | None"] = relationship(
        remote_side="QuestionVersion.id"
    )
