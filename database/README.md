
# Q-Forge AI Database

## Database
MySQL 8.0

## Purpose
This database supports the Q-Forge AI question generation,
verification, question bank, and examination platform.

## Files
- schema.sql: Creates the database and initial tables.
- seed.sql: Inserts sample data for testing.
- migrations/: Stores future database changes.

## Current Tables
1. subjects
2. syllabus_units
3. topics
4. source_documents
5. source_chunks
6. questions
7. question_versions
8. question_options
9. question_sources

## Setup Instructions
1. Open MySQL 8.0 Command Line Client.
2. Run schema.sql using the SOURCE command.
3. Run seed.sql using the SOURCE command.
4. Run SHOW TABLES to verify the database.

## Sample Test
The seed file inserts a sample Python question.
Its initial status is draft.

## Pending Work
- Finalize question approval workflow with the team.
- Add exam blueprint and exam tables.
- Add attempts, autosave, and scoring.
- Integrate with the FastAPI backend.
