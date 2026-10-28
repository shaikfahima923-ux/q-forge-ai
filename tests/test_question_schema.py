import pytest
from pydantic import ValidationError

from app.schemas.question import QuestionCreate


def test_valid_question_is_accepted():
    question = QuestionCreate(
        question_type="MCQ",
        difficulty="Easy",
        question_text="What is 2 + 2?",
        options={"A": "3", "B": "4", "C": "5"},
        correct_answer="B",
        explanation="Two plus two equals four.",
    )

    assert question.question_text == "What is 2 + 2?"
    assert question.status == "draft"


def test_empty_question_text_is_rejected():
    with pytest.raises(ValidationError):
        QuestionCreate(
            question_type="MCQ",
            difficulty="Easy",
            question_text="",
        )


def test_invalid_difficulty_is_rejected():
    with pytest.raises(ValidationError):
        QuestionCreate(
            question_type="MCQ",
            difficulty="Very Easy",
            question_text="What is 2 + 2?",
        )


def test_invalid_question_type_is_rejected():
    with pytest.raises(ValidationError):
        QuestionCreate(
            question_type="Essay",
            difficulty="Easy",
            question_text="Explain addition.",
        )
