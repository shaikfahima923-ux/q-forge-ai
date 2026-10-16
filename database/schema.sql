
CREATE DATABASE IF NOT EXISTS q_forge_ai;
USE q_forge_ai;

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(150) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS syllabus_units (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    unit_number INT NOT NULL,
    unit_name VARCHAR(200) NOT NULL,
    FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),
    UNIQUE (subject_id, unit_number)
);

CREATE TABLE IF NOT EXISTS topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    unit_id INT NOT NULL,
    topic_name VARCHAR(200) NOT NULL,
    FOREIGN KEY (unit_id)
        REFERENCES syllabus_units(unit_id),
    UNIQUE (unit_id, topic_name)
);

CREATE TABLE IF NOT EXISTS source_documents (
    document_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(20),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
);

CREATE TABLE IF NOT EXISTS source_chunks (
    chunk_id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    page_number INT,
    chunk_text TEXT NOT NULL,
    FOREIGN KEY (document_id)
        REFERENCES source_documents(document_id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS questions (
    question_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    question_type VARCHAR(30) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id)
        REFERENCES topics(topic_id),
    CHECK (question_type IN (
        'MCQ', 'MSQ', 'TRUE_FALSE',
        'FILL_BLANK', 'NUMERICAL',
        'ASSERTION_REASON'
    )),
    CHECK (difficulty IN ('easy', 'medium', 'hard'))
);

CREATE TABLE IF NOT EXISTS question_versions (
    version_id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    version_number INT NOT NULL,
    question_text TEXT NOT NULL,
    correct_answer TEXT,
    explanation TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (question_id)
        REFERENCES questions(question_id),
    UNIQUE (question_id, version_number),
    CHECK (status IN (
        'draft', 'revision_required',
        'human_review', 'approved', 'rejected'
    ))
);

CREATE TABLE IF NOT EXISTS question_options (
    option_id INT AUTO_INCREMENT PRIMARY KEY,
    version_id INT NOT NULL,
    option_label VARCHAR(10) NOT NULL,
    option_text TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL DEFAULT FALSE,
    FOREIGN KEY (version_id)
        REFERENCES question_versions(version_id)
        ON DELETE CASCADE,
    UNIQUE (version_id, option_label)
);

CREATE TABLE IF NOT EXISTS question_sources (
    version_id INT NOT NULL,
    chunk_id INT NOT NULL,
    PRIMARY KEY (version_id, chunk_id),
    FOREIGN KEY (version_id)
        REFERENCES question_versions(version_id)
        ON DELETE CASCADE,
    FOREIGN KEY (chunk_id)
        REFERENCES source_chunks(chunk_id)
);
