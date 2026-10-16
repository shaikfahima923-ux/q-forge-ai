
# Q-Forge AI — Database Design

## Database Technology
MySQL 8.0

## Table Relationships

- One subject can contain many syllabus units.
- One syllabus unit can contain many topics.
- One topic can have many questions.
- One question can have multiple versions.
- One question version can have multiple answer options.
- One source document can contain many extracted text chunks.
- Question versions can reference multiple source chunks.

## Question Lifecycle

The proposed question statuses are:

- draft
- revision_required
- human_review
- approved
- rejected

These values are provisional until confirmed by the team.

## Exam Eligibility

Only approved question versions should be eligible
for exam selection.

The backend must enforce this rule. A published exam
should retain the exact question versions selected.

## Planned Database Extensions

- User accounts and roles
- Question validation and review records
- Exam blueprints
- Exams and selected question versions
- Candidate attempts and responses
- Scoring and analytics
- Audit logs
