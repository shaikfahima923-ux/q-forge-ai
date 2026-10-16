
USE q_forge_ai;

-- Insert a sample subject
INSERT IGNORE INTO subjects (subject_name, description)
VALUES (
    'Computer Science Basics',
    'Sample subject for database testing'
);

-- Insert a syllabus unit
INSERT IGNORE INTO syllabus_units
    (subject_id, unit_number, unit_name)
SELECT subject_id, 1, 'Introduction to Programming'
FROM subjects
WHERE subject_name = 'Computer Science Basics';

-- Insert a topic
INSERT IGNORE INTO topics (unit_id, topic_name)
SELECT unit_id, 'Python Fundamentals'
FROM syllabus_units
WHERE unit_number = 1
AND subject_id = (
    SELECT subject_id
    FROM subjects
    WHERE subject_name = 'Computer Science Basics'
);

-- Insert a sample question
INSERT INTO questions (topic_id, question_type, difficulty)
SELECT topic_id, 'MCQ', 'easy'
FROM topics
WHERE topic_name = 'Python Fundamentals'
AND NOT EXISTS (
    SELECT 1
    FROM questions q
    WHERE q.topic_id = topics.topic_id
      AND q.question_type = 'MCQ'
      AND q.difficulty = 'easy'
);

-- Insert version 1 of the sample question
INSERT INTO question_versions
    (question_id, version_number, question_text,
     correct_answer, explanation, status)
SELECT
    q.question_id,
    1,
    'Which keyword is used to define a function in Python?',
    'def',
    'Python uses the def keyword to define a function.',
    'draft'
FROM questions q
WHERE q.question_type = 'MCQ'
AND q.difficulty = 'easy'
AND NOT EXISTS (
    SELECT 1
    FROM question_versions qv
    WHERE qv.question_id = q.question_id
      AND qv.version_number = 1
);
