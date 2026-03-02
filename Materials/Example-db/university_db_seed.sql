-- University database seed data
-- Run after university_db_schema.sql

-- Teachers
INSERT INTO teachers (full_name, email) VALUES
  ('Liisa Korhonen', 'liisa@uni.fi'),
  ('Pekka Salo', 'pekka@uni.fi'),
  ('Maria Lind', 'maria@uni.fi');

-- Students
INSERT INTO students (full_name, email) VALUES
  ('Aino Laine', 'aino@uni.fi'),
  ('Mika Virtanen', 'mika@uni.fi'),
  ('Sara Niemi', NULL),
  ('Olli Koski', 'olli@gmail.com');

-- Courses
INSERT INTO courses (title, credits, teacher_id) VALUES
  ('Databases', 5, 1),
  ('Algorithms', 6, 2),
  ('Web Development', 5, 3);

-- Enrollments
INSERT INTO enrollments (student_id, course_id) VALUES
  (1, 1),
  (1, 2),
  (2, 1),
  (3, 1),
  (3, 3),
  (4, 3);

-- Grades
INSERT INTO grades (student_id, course_id, grade) VALUES
  (1, 1, 5),
  (1, 2, 4),
  (2, 1, 3),
  (3, 1, 2),
  (3, 3, 5),
  (4, 3, 4);
