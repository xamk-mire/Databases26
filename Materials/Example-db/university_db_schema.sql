-- University database schema (PostgreSQL)
-- Creates the database and tables for the university example

-- Delete existing table 
DROP TABLE IF EXISTS university_db;

CREATE DATABASE university_db;

-- Students
CREATE TABLE students (
  student_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(255) UNIQUE
);

-- Teachers
CREATE TABLE teachers (
  teacher_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  full_name  VARCHAR(100) NOT NULL,
  email      VARCHAR(255) UNIQUE
);

-- Courses
CREATE TABLE courses (
  course_id  INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  title      VARCHAR(200) NOT NULL,
  credits    INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 20),
  teacher_id INTEGER NOT NULL REFERENCES teachers(teacher_id) ON DELETE RESTRICT
);

-- Enrollments (junction table)
CREATE TABLE enrollments (
  student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
  course_id  INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE RESTRICT,
  PRIMARY KEY (student_id, course_id)
);

-- Grades
CREATE TABLE grades (
  student_id INTEGER NOT NULL REFERENCES students(student_id) ON DELETE RESTRICT,
  course_id  INTEGER NOT NULL REFERENCES courses(course_id) ON DELETE RESTRICT,
  grade      INTEGER CHECK (grade BETWEEN 0 AND 5),
  PRIMARY KEY (student_id, course_id)
);
