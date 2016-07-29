DROP DATABASE IF EXISTS DelftX;
CREATE DATABASE DelftX CHARACTER SET `utf8mb4`;

USE DelftX;

DROP TABLE IF EXISTS `courses`;
CREATE TABLE `courses` (
course_id varchar(250) NOT NULL,
course_name varchar(250),
start_time datetime,
end_time datetime,
PRIMARY KEY (course_id)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `learner_demographic`;
CREATE TABLE `learner_demographic` (
course_learner_id varchar(250) NOT NULL,
gender varchar(250),
year_of_birth int,
level_of_education varchar(250),
country varchar(250),
email varchar(250),
PRIMARY KEY (course_learner_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index_birth` (`year_of_birth`),
INDEX `index_country` (`country`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `learner_index`;
CREATE TABLE `learner_index` (
global_learner_id int NOT NULL,
course_id varchar(250) NOT NULL,
course_learner_id varchar(250) NOT NULL,
PRIMARY KEY (course_learner_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id),
FOREIGN KEY (global_learner_id) REFERENCES learner_demographic(global_learner_id),
INDEX `index_cid` (`course_id`),
INDEX `index_clid` (`course_learner_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `course_learner`;
CREATE TABLE `course_learner` (
course_learner_id varchar(250) NOT NULL,
final_grade FLOAT,
enrollment_mode varchar(250),
certificate_status varchar(250),
register_time datetime,
PRIMARY KEY (course_learner_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index_enrollment` (`enrollment_mode`),
INDEX `index_certificate` (`certificate_status`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `course_elements`;
CREATE TABLE `course_elements` (
element_id varchar(250) NOT NULL,
element_type varchar(250),
week int,
course_id varchar(250),
PRIMARY KEY (element_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id),
INDEX `index_type` ( `element_type`),
INDEX `index_week` ( `week`),
INDEX `index_courseid` (`course_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `sessions`;
CREATE TABLE `sessions` (
session_id varchar(250) NOT NULL,
course_learner_id varchar(250) NOT NULL,
start_time datetime,
end_time datetime,
duration int,
PRIMARY KEY (session_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`course_learner_id`)
) ENGINE=MyISAM;




DROP TABLE IF EXISTS `quiz_questions`;
CREATE TABLE `quiz_questions` (
question_id varchar(250) NOT NULL,
question_type varchar(250),
question_weight float,
question_due datetime,
PRIMARY KEY (question_id),
FOREIGN KEY (question_id) REFERENCES course_elements(element_id),
INDEX `index_type` (`question_type`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `submissions`;
CREATE TABLE `submissions` (
submission_id varchar(250) NOT NULL,
course_learner_id varchar(250) NOT NULL,
question_id varchar(250) NOT NULL,
submission_timestamp datetime,
PRIMARY KEY (submission_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
FOREIGN KEY (question_id) REFERENCES course_elements(element_id),
INDEX `index_c` (`course_learner_id`),
INDEX `index_q` (`question_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `assessments`;
CREATE TABLE `assessments` (
assessment_id varchar(250) NOT NULL,
course_learner_id varchar(250),
max_grade float,
grade float,
PRIMARY KEY (assessment_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
FOREIGN KEY (assessment_id) REFERENCES submissions(submission_id),
INDEX `index` (`course_learner_id`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `quiz_sessions`;
CREATE TABLE `quiz_sessions` (
session_id varchar(250) NOT NULL,
course_learner_id varchar(250) NOT NULL,
start_time datetime,
end_time datetime,
duration int,
PRIMARY KEY (session_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`course_learner_id`)
) ENGINE=MyISAM;



DROP TABLE IF EXISTS `video_interaction`;
CREATE TABLE `video_interaction` (
interaction_id varchar(250) NOT NULL,
course_learner_id varchar(250) NOT NULL,
video_id varchar(250) NOT NULL,
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
post_id varchar(250) NOT NULL,
course_learner_id varchar(250),
post_type varchar(250),
post_title text,
post_content text,
post_timestamp datetime,
post_parent_id varchar(250),
post_thread_id varchar(250),
PRIMARY KEY (post_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`course_learner_id`),
INDEX `index_pt` (`post_type`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `forum_sessions`;
CREATE TABLE `forum_sessions` (
session_id varchar(250) NOT NULL,
course_learner_id varchar(250) NOT NULL,
times_search int,
start_time datetime,
end_time datetime,
duration int,
relevent_element_id varchar(250),
PRIMARY KEY (session_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`course_learner_id`)
) ENGINE=MyISAM;


DROP TABLE IF EXISTS `survey_descriptions`;
CREATE TABLE `survey_descriptions` (
question_id varchar(250) NOT NULL,
course_id varchar(250),
question_type varchar(250),
question_description text,
PRIMARY KEY (question_id),
FOREIGN KEY (course_id) REFERENCES courses(course_id),
INDEX `index` (`course_id`),
INDEX `index_q` (`question_type`)
) ENGINE=MyISAM;

DROP TABLE IF EXISTS `survey_responses`;
CREATE TABLE survey_responses (
response_id varchar(250) NOT NULL,
course_learner_id varchar(250),
question_id varchar(250),
answer text,
PRIMARY KEY (response_id),
FOREIGN KEY (course_learner_id) REFERENCES learner_index(course_learner_id),
INDEX `index` (`course_learner_id`),
INDEX `index_q` (`question_id`)
) ENGINE=MyISAM;

