DROP DATABASE IF EXISTS DelftX;
CREATE DATABASE DelftX CHARACTER SET `latin1`;

USE DelftX;

DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses` (
course_id varchar(255) NOT NULL,
course_name varchar(255),
start_time datetime,
end_time datetime,
PRIMARY KEY (course_id),
INDEX `index` (`course_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `learner_demographic`;
CREATE TABLE `learner_demographic` (
course_learner_id varchar(255) NOT NULL,
gender varchar(255),
year_of_birth int,
level_of_education varchar(255),
country varchar(255),
email varchar(255),
PRIMARY KEY (course_learner_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`course_learner_id`(50), `gender`, `year_of_birth`, `level_of_education`, `country`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `learner_index`;
CREATE TABLE `learner_index` (
global_learner_id int NOT NULL,
course_id varchar(255) NOT NULL,
course_learner_id varchar(255) NOT NULL,
PRIMARY KEY (course_learner_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id),
FOREIGN KEY (global_learner_id) REFERENCES learner_demographic(global_learner_id),
INDEX `index` (`global_learner_id`, `course_id`, `course_learner_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `course_learner`;
CREATE TABLE `course_learner` (
course_learner_id varchar(255) NOT NULL,
final_grade FLOAT,
enrollment_mode varchar(255),
certificate_status varchar(255),
register_time datetime,
PRIMARY KEY (course_learner_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`course_learner_id`, `enrollment_mode`, `certificate_status`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `course_elements`;
CREATE TABLE `course_elements` (
element_id varchar(255) NOT NULL,
element_type varchar(255),
week int,
course_id varchar(255),
PRIMARY KEY (element_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id),
INDEX `index` (`element_id`, `element_type`, `week`, `course_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `sessions`;
CREATE TABLE `sessions` (
session_id varchar(255) NOT NULL,
course_learner_id varchar(255) NOT NULL,
start_time datetime,
end_time datetime,
duration int,
PRIMARY KEY (session_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`session_id`, `course_learner_id`)
) ENGINE=MyISAM;




DROP TABLE IF EXISTS `quiz_questions`;
CREATE TABLE `quiz_questions` (
question_id varchar(255) NOT NULL,
question_type varchar(255),
question_weight float,
question_due datetime,
PRIMARY KEY (question_id),
FOREIGN KEY (question_id) REFERENCES course_elements(element_id),
INDEX `index` (`question_id`, `question_type`, `question_weight`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `submissions`;
CREATE TABLE `submissions` (
submission_id varchar(255) NOT NULL,
course_learner_id varchar(255) NOT NULL,
question_id varchar(255) NOT NULL,
submission_timestamp datetime,
PRIMARY KEY (submission_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
FOREIGN KEY (question_id) REFERENCES course_elements(element_id),
INDEX `index` (`submission_id`, `course_learner_id`, `question_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `assessments`;
CREATE TABLE `assessments` (
assessment_id varchar(255) NOT NULL,
course_learner_id varchar(255),
max_grade float,
grade float,
PRIMARY KEY (assessment_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
FOREIGN KEY (assessment_id) REFERENCES submissions(submission_id),
INDEX `index` (`assessment_id`, `course_learner_id`, `max_grade`, `grade`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `quiz_sessions`;
CREATE TABLE `quiz_sessions` (
session_id varchar(255) NOT NULL,
course_learner_id varchar(255) NOT NULL,
start_time datetime,
end_time datetime,
duration int,
PRIMARY KEY (session_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`session_id`, `course_learner_id`)
) ENGINE=MyISAM;



DROP TABLE IF EXISTS `video_interaction`;
CREATE TABLE `video_interaction` (
interaction_id varchar(255) NOT NULL,
course_learner_id varchar(255) NOT NULL,
video_id varchar(255) NOT NULL,
duration double,
times_forward_seek int,
duration_forward_seek double,
times_backward_seek int,
duration_backward_seek double,
times_speed_up int,
times_speed_down int,
times_pause int,
duration_pause double,
start_time datetime,
end_time datetime,

PRIMARY KEY (interaction_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
FOREIGN KEY (video_id) REFERENCES course_elements(element_id),

INDEX `index` (`interaction_id`(50), `course_learner_id`(50), `video_id`(50))

) ENGINE=MyISAM;




DROP TABLE IF EXISTS `forum_interaction`;
CREATE TABLE `forum_interaction` (
post_id varchar(255) NOT NULL,
course_learner_id varchar(255),
post_type varchar(255),
post_title text,
post_content text,
post_timestamp datetime,
post_parent_id varchar(255),
post_thread_id varchar(255),
PRIMARY KEY (post_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`post_id`, `course_learner_id`, `post_type`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `forum_sessions`;
CREATE TABLE `forum_sessions` (
session_id varchar(255) NOT NULL,
course_learner_id varchar(255) NOT NULL,
times_search int,
start_time datetime,
end_time datetime,
duration int,
PRIMARY KEY (session_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`session_id`, `course_learner_id`)
) ENGINE=MyISAM;



DROP TABLE IF EXISTS `survey_descriptions`;
CREATE TABLE `survey_descriptions` (
question_id varchar(255) NOT NULL,
course_id varchar(255),
question_type varchar(255),
question_description text,
PRIMARY KEY (question_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id),
INDEX `index` (`question_id`, `course_id`, `question_type`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `survey_responses`;
CREATE TABLE survey_responses (
response_id varchar(255) NOT NULL,
course_learner_id varchar(255),
question_id varchar(255),
answer text,
PRIMARY KEY (response_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`response_id`, `course_learner_id`, `question_id`)
) ENGINE=MyISAM;

