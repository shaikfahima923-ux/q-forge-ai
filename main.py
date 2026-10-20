import os
import json

import pymupdf
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from google import genai
from google.genai import types

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

app = FastAPI(
    title="Vidyothini AI Question Bank Generator",
    description="Generate educational questions from uploaded textbooks.",
    version="1.0.0",
)

client = genai.Client(api_key=API_KEY) if API_KEY else None


@app.get("/")
def home():
    return {
        "message": "Vidyothini AI Question Bank API is running!",
        "docs": "/docs",
        "generate_endpoint": "/generate"
    }


@app.post("/generate")
async def generate_questions(
    file: UploadFile = File(...),
    difficulty: str = Form("Easy"),
    number_of_questions: int = Form(5),
):
    # 1. Validate inputs
    if client is None:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY is missing. Check your .env file."
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF textbook."
        )

    if difficulty not in ["Easy", "Moderate", "Difficult"]:
        raise HTTPException(
            status_code=400,
            detail="Difficulty must be Easy, Moderate, or Difficult."
        )

    if not 1 <= number_of_questions <= 10:
        raise HTTPException(
            status_code=400,
            detail="Choose between 1 and 10 questions."
        )

    # 2. Read PDF and extract its text
    pdf_bytes = await file.read()

    if len(pdf_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail="PDF is too large. Maximum size is 10 MB."
        )

    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as pdf:
            if pdf.is_encrypted:
                raise HTTPException(
                    status_code=400,
                    detail="Password-protected PDFs are not supported."
                )

            text = "\n".join(page.get_text() for page in pdf)

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read this PDF. Please try another file."
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No selectable text found. Try a text-based PDF."
        )

    # Limit the amount of textbook text sent to the AI.
    text = text[:30000]

    # 3. Ask the AI to generate questions
    prompt = f"""
You are an educational question-bank generation assistant.

Use only the textbook content supplied below.
Do not invent facts that are not supported by the content.

Generate exactly {number_of_questions} multiple-choice questions.
Difficulty: {difficulty}

For every question, provide:
- question: the question text
- options: exactly four options labelled A, B, C, D
- correct_answer: one option label
- correct_explanation: why the correct answer is right
- option_explanations: explain why EACH of the four options
  is correct or incorrect

Return a JSON object in this exact structure:
{{
  "questions": [
    {{
      "question": "Question text",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "correct_explanation": "Explanation",
      "option_explanations": {{
        "A": "Explanation",
        "B": "Explanation",
        "C": "Explanation",
        "D": "Explanation"
      }}
    }}
  ]
}}

TEXTBOOK CONTENT:
{text}
"""

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )

        if not response.text:
            raise ValueError("The AI returned an empty response.")

        result = json.loads(response.text)
        questions = result.get("questions")

        if not isinstance(questions, list):
            raise ValueError("The AI response has no questions list.")

        if len(questions) != number_of_questions:
            raise ValueError("The AI returned an unexpected number of questions.")

        # 4. Validate the generated question structure
        for question in questions:
            if not isinstance(question, dict):
                raise ValueError("Invalid question format.")

            options = question.get("options", {})
            explanations = question.get("option_explanations", {})

            if not all(
                key in question
                for key in [
                    "question",
                    "correct_answer",
                    "correct_explanation",
                ]
            ):
                raise ValueError("A question is missing required fields.")

            if not isinstance(options, dict) or set(options) != {
                "A", "B", "C", "D"
            }:
                raise ValueError("A question must have four labelled options.")

            if question["correct_answer"] not in options:
                raise ValueError("A correct answer does not match an option.")

            if not isinstance(explanations, dict) or set(explanations) != {
                "A", "B", "C", "D"
            }:
                raise ValueError("Option explanations are incomplete.")

        # 5. Return the question bank to the frontend
        return {
            "success": True,
            "filename": file.filename,
            "difficulty": difficulty,
            "question_type": "MCQ",
            "total_questions": len(questions),
            "questions": questions,
        }

    except HTTPException:
        raise
    except Exception as error:
        raise HTTPException(
            status_code=502,
            detail=(
                "Question generation failed. Check your API key, "
                "model availability, API limits, and connection. "
                f"Details: {str(error)[:300]}"
            ),
        )