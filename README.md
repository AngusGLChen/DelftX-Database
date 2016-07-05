# Building Database for Courses Data of MOOCs (EDX)

## 1. Database Building

### 1.1 Environmantal Setting

1. This manual is tested on Mac OSX.
    * It should also work well on similar LINUX systems.
    * Please report us if you meet system-related problems. 

2. This manual is tested on course data of EX101x-3T2015 and FP101x-3T2015.

3. Python 2.7 should be well installed in the machine.
    * It will be updated for both python 2 and 3.

### 1.2 Installing MySQL

1. Downloading [MySQL Community Server](http://dev.mysql.com/downloads/mysql/)

2. Installing and recording the initial root password

3. (MAC OSX) Checking if MySQL installed in ```/usr/local/mysql/bin```

4. (MAC OSX) Setting PATH
    * Editting bash profile ```vim ~/.bash_profile```
    * Setting the path ```PATH=$PATH:/usr/local/mysql/bin```
    * Adding this in bash file:
    
    ```
    alias mysql=/usr/local/mysql/bin/mysql
    alias mysqladmin=/usr/local/mysql/bin/mysqladmin
    ```
    * Saving the setting ```esc``` + ```:wq```
    * Sourcing bash profile ```source ~/.bash_profile```

5. Running MySQL Server
    * (MAC OSX) users can start it on System Preferences
    
6. Setting the password of root
    * Using ```mysql -uroot -p``` with password to login MySQL
    * Inputting ```SET PASSWORD FOR 'root'@'localhost' = PASSWORD('newpass');```
    
7. Installing [MySQL Workbench](http://dev.mysql.com/downloads/workbench/) for connecting MySQL Server

8. Installing Connector/Python 
    * Please check the documents [MySQL Connector/Python Developer Guide](https://dev.mysql.com/doc/connector-python/en/connector-python-installation-binary.html)
    * Checking if the package installed by using ```import mysql.connector```
    * Checking if the package version correct by using ```print mysql.connector.__version__```. It should be >= 2.1.3, since we use ```utf8mb4``` in encoding, which may not be supported by some earlier versions.

### 1.3 Building the database

1. Open the file ```DelftX.sql``` by MySQL Workbench and Run the SQL script.


## 2. Reading course data into the the database
    
1. Making a root folder for storing all your course data. For example, the folder can be named as ```course_log```.

2. Preprocessing daily log files:
    * Making a folder named ```Daily_Logs``` under the root folder ```course_log```
    * Put all the gzip files of course daily logs (e.g. ```delftx-edx-events-201X-MM-DD.log.gz```) into the folder ```Daily_Logs```
    
3. For each course, build a folder under the root folder (e.g. ```course_log```) of course data. For example, the course folder name can be ```FP101x-3T2015```
    * Uncompressing all the metadata of the courses (e.g. the file ```FP101x-3T2015.zip```)
    * making a folder ```metadata``` under the course folder (e.g. ```FP101x-3T2015```)
    * put all the uncompressed course metadata into the folder ```metadata```

4. After above steps, the structure of course data should be as following.

	```
	--  course_log
	    --  translated_course_list
	    --  Daily_Logs
	        --  delftx-edx-events-201X-MM-DD.log.gz
	        --  ...
	    --  FP101x-3T2015
	        --  metadata
	            --  DelftX-FP101x-3T2015-auth_user-prod-analytics.sql
	            --  ...
	    --  EX101x-3T2015
	        --  metadata
	            --  DelftX-EX101x-3T2015-auth_user-prod-analytics.sql
	            --  ...  
	```
	```translated_course_list``` is the file which contains all names of transfered courses. It should be empty if a new database is building.

5. Editing config file ```config```
    
    ```
    [mysqld]
    user = root
    password = 123456
    host = 127.0.0.1
    database = DelftX
    [data]
    path = /Volumes/XXXX/XXXX/
    remove_filtered_logs = 0
    ```
    * ```[mysqld]``` is the section of database related configures
        * ```user``` is the user id of the database
        * ```password``` is the password of the database
        * ```host``` is the host ip of the database
        * ```database``` is the name of the database
    * ```[data]``` is the section of data related configures
        * ```path``` is the path of the root folder of all course data (e.g ```$PATH$/course_log/```)
        * ```remove_filtered_logs``` is the configure of removing the filtered daily logs of each course.
            * ```remove_filtered_logs=0``` means that in course transfer, fildered daily logs of each course will be kept unless you delete them manully.
            * ```remove_filtered_logs=1``` means that fildered daily logs of each course will be removed automatically after the course transfered into databse.
            * If you want to keep filtered daily logs for further work, please set it as ```0```. 
            * If you want to save space on your machine and do not need filtered daily logs, please set it as ```1```.  

6. Running the code by ```python main.py config```

7. After the above code, the structure of course data should be as following.
	
	```
	--  course_log
	    --  translated_course_list
	    --  Daily_Logs
	        --  delftx-edx-events-201X-MM-DD.log.gz
	        --  ...
	    --  FP101x-3T2015
	        --  filter_folder
	            --  Delftx-edx-events-201X-MM-DD.log
	            --  ...
	        --  metadata
	            --  DelftX-FP101x-3T2015-auth_user-prod-analytics.sql
	            --  ...
	    --  EX101x-3T2015
	        --  filter_folder
	            --  Delftx-edx-events-201X-MM-DD.log
	            --  ...
	        --  metadata
	            --  DelftX-EX101x-3T2015-auth_user-prod-analytics.sql
	            --  ...  
	```
	```filter_folder``` contains filtered daily logs for the specific course. It can be removed after course data loaded into the database (by seeting in the config file). 


## 3. Relations with The Moocdb Project

### 3.1 The Moocdb Project

[The MOOCdb Project](moocdb.csail.mit.edu) is an open source framework, which sets a shared data model standard for organzing data generated from MOOCs.

The initial schema of moocdb consists of four modules, which are Observing, Submitting, Collaborating and Feedback.

### 3.2 Our current schema

Our current schema is mainly based on the moocdb project. It consists of four modules, which are named as Observations, Submissions, Collaborations and UserModes. 

<!--![Alt](./ReadMeResources/DelftXDatabaseSchema.png "Title")-->

<div style="text-align: center">
<img src="./ReadMeResources/DelftXDatabaseSchema.png"/ width = "600" height = "600">
</div>

As shown in Figure 1, each module in our schema has several tables of information. The differences between our current schema and the initial moocdb schema are discussed in the following sections.

### 3.3 Video Observing

In original Moocdb schema, Observing mode has five tables, which are observed_event, resources, resources_urls, resources_types and urls. 

<!--![Alt](./ReadMeResources/videomode.png "Title")-->

<div style="text-align: center">
<img src="./ReadMeResources/videomode.png"/ width = "140" height = "300">
</div>

In our current schema, we merge them into one tables, named video_interaction. This table represent the video observing events of students and relevant interactives of events.

### 3.4 Quiz Submission

In original Moocdb schema, Submitting mode has four tables, which are problem_type, problems, submissions, and assessments. 

<!--![Alt](./ReadMeResources/quizmode.png "Title")-->

<div style="text-align: center">
<img src="./ReadMeResources/quizmode.png"/ width = "140" height = "400">
</div>

In our current schema of quiz mode, we merge the two problem related table into one table named quiz_questions. After that, a table named quiz_sessions is added. quiz_sessions is leveraged to represent how users answer sessions of quiz.

### 3.5 Forum Interactions

In our current schema, two tables are leveraged to store learners; interactions in discussion forum.
<!--![Alt](./ReadMeResources/forummode.png "Title")-->

<div style="text-align: center">
<img src="./ReadMeResources/forummode.png"/ width = "140" height = "300">
</div>

### 3.6 Learner Information

In our schema, we have a mode named learners modes, which contains six tables named courses, course_elements, learner_index, course_learner, learner_demographic and sessions. This mode is used to store information about courses, learners, how well learners perform in each course, etc.


<!--![Alt](./ReadMeResources/learnermode.png "Title")-->

<div style="text-align: center">
<img src="./ReadMeResources/learnermode.png"/ width = "400" height = "400">
</div>

Table courses contains the metainfo of courses. Table global_user represent the relations between users and courses. Table course_user represent users' status and grade in courses. Table user_pii represent course users' demographic data.

### 3.7 Survey Mode

The survey mode stores learners’ responses to survey questions.

<!--![Alt](./ReadMeResources/surveymode.png "Title")-->

<div style="text-align: center">
<img src="./ReadMeResources/surveymode.png"/ width = "120" height = "260">
</div> 

## 4. Data-related problems

### 4.1 Not all the problems in courses are tagged with correct weights.

For example, the only 2 point question in course Functional Programming (FP101x-3T2015) do not have a explicit weight, so we treated its weight as 1.0 at the beginning. It also happens in course_structure data of course Data Analysis(EX101x-3T2015).

Solution: We manually correct the weight of each problems in courses Fuctional Programming and Data Analysis based on the points students got and the current course settings on edx.

### 4.2 The timestamps of submissions may be later than the due.

At the beginning, we filtered all the submissions which submitted later than the due. However, we found that those submissions are counted by manually checking the submission time and the corresponding grades students got.

### 4.3 How to calculate the real grades students got in their submissions?

* In the records of student submissions and assessment of each problem in daily logs, there are two fields named grade and max_grade. max_grade means the number of blanks need to be filled. grade means the number of correct blanks students submitted.
* In the metadata, each problem has their own weights.
* real_grade = weight * ( grade / max_grade )

### 4.4 Not all the passed students have enough records in assessment.

In the course Functional Programming (FP101x_3T2015), 8/1143 passing students have less than 170 points in the final week. In the course Data Analysis (EX101x_3T2015), 11/1156 passing students have less than 105 points in the final week.

By manually checking daily logs of corresponding courses, all the grades of those students in daily logs are correctly loaded into the database. 









