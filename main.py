'''
Created on Jun 18, 2016

@author: Angus
'''

'''
Update 1: change the organization of course data

Updated on Jun 29, 2016
@author: Yue

1. Zipfile of Daily Logs
The zip file of daily logs are located into a single folder

2. Course Folder
In each course folder, there are two sub-folders. 
One is for course metadata, the other one is for filtered course daily logs

3. Change how data organized
The course data structure shouled be

--  Course_Data_Folder

    --  translated_course_list
    
    --  Daily_Logs
        --  delftx-edx-events-201X-MM-DD.log.gz
    
    --  <Course_1>
        --  filter_folder
        --  metadata
            --  DelftX-XX10Xx-XT201X-auth_user-prod-analytics.sql
            --  ...
    
    --  <Course_2>
        --  filter_folder
        --  metadata
            --  DelftX-XX10Xx-XT201X-auth_user-prod-analytics.sql
            --  ...    

'''

import os,gzip,mysql.connector,json
import sys
import ConfigParser

from translation.LearnerMode import learner_mode, sessions
from translation.ForumMode import forum_interaction, forum_sessions
from translation.VideoMode import video_interaction
from translation.QuizMode import quiz_mode, quiz_sessions


def main(argv):
    
    # Read configs
    config = ConfigParser.ConfigParser()
    config.read(argv[0])

    # All the configs are read as string
    data_path = config.get("data", "path")
    user = config.get("mysqld", "user")
    password = config.get("mysqld", "password")
    host = config.get("mysqld", "host")
    database = config.get("mysqld", "database")
    
    # Database
    connection = mysql.connector.connect(user=user, password=password, host=host, database=database)
    cursor = connection.cursor()
    
    # Gather the list of translated courses
    translated_courses = set()
    
    course_list_path = data_path + "translated_course_list"
    if not os.path.isfile(course_list_path):
        course_list_file = open(course_list_path, "w")
        course_list_file.close()
        
    input_file = open(course_list_path, "r")
    lines = input_file.readlines()
    for line in lines:
        line = line.replace("\n", "")
        translated_courses.add(line)
    input_file.close()

    print str(len(translated_courses)) + "\tcourses have been translated."

    # Keep track of translated courses
    output_file = open(course_list_path, "a") 

    # zip_files is the gzip files of daily logs
    zip_folder_path = data_path + "Daily_Logs/"

    # Search for the courses that have not been translated
    log_folders = os.listdir(data_path)
    for log_folder in log_folders:
        
        if not os.path.isdir(data_path + log_folder):
            continue

        if log_folder == "Daily_Logs":
            continue
        
        if not log_folder in translated_courses:
            try:
                
                print "Start to translating course\t" + log_folder
                
                # metadata is the folder of course metadata
                metadata_path = data_path + log_folder + "/metadata/"
                
                # filter_folder is the filtered daily logs of this course
                filter_folder_path = data_path + log_folder + "/filter_folder/"
                if not os.path.exists(filter_folder_path):
                    os.mkdir(filter_folder_path)
                
                #############################################
                #
                # Filter the daily logs to generated filtered
                # logs which only contain specific course info
                # 
                # This step can be writen in batch-processing,
                # which just scan all daily logs once and 
                # generated filtered logs for all the course.
                # but it is a balance between space and time.
                # So I keep the Guanliang's procedure which 
                # generated daily logs for courses 1 by 1. 
                # 
                #############################################
                
                course_id = ""
                meta_files = os.listdir(metadata_path)
                for file in meta_files:             
                    if "course_structure" in file:
                        course_structure_file = open(metadata_path + file, "r")
                        jsonObject = json.loads(course_structure_file.read())
                        for record in jsonObject:
                            if jsonObject[record]["category"] == "course":
                                # Course ID
                                course_id = record
                                if course_id.startswith("block-"):
                                    course_id = course_id.replace("block-","course-")
                                    course_id = course_id.replace("+type@course+block@course", "")
                                if course_id.startswith("i4x://"):
                                    course_id = course_id.replace("i4x://", "")
                                    course_id = course_id.replace("course/", "")

                                start_time = jsonObject[record]["metadata"]["start"]
                                end_time = jsonObject[record]["metadata"]["end"]
                    
                                # Start & End data
                                start_date = start_time[0:start_time.index("T")]
                                end_date = end_time[0:end_time.index("T")]


                log_files = os.listdir(zip_folder_path)
                for log_file in log_files:
                    if ".gz" in log_file:
                        # check if current log file is in correct date / time range
                        if log_file[18:28] >= start_date and log_file[18:28] <= end_date:
                            
                            print(log_file[18:28])

                            path = filter_folder_path + log_file[0:-3]
                            output_dailylog = open(path, 'wt')

                            with gzip.open(zip_folder_path + log_file, 'rt') as f:
                                for line in f:
                                    jsonObject = json.loads(line)
                                    if course_id in jsonObject["context"]["course_id"]:
                                        output_dailylog.write(line)

                            output_dailylog.close()

                #######################################
                # Filtering process end
                #######################################
                    
                # Translate the log files
                log_path = filter_folder_path
                
                # 1. Learner Mode
                print ("learner_mode")
                learner_mode(metadata_path, cursor)
                print ("sessions")
                sessions(metadata_path, log_path, cursor)
                
                print ("Learner mode finished.")
                
                # 2. Forum Mode
                print ("forum_interaction")
                forum_interaction(metadata_path, cursor)
                print ("forum_sessions")
                forum_sessions(metadata_path, log_path, cursor)
                
                print ("Forum mode finished.")
                
                # 3. Video Mode
                print ("video_interaction")
                video_interaction(metadata_path, log_path, cursor)
                
                print ("Video mode finished.")
                
                # 4. Quiz Mode
                print ("quiz_mode")
                quiz_mode(metadata_path, log_path, cursor)
                print ("quiz_sessions")
                quiz_sessions(metadata_path, log_path, cursor)
                
                print ("Quiz mode finished.")               
                
                # 5. Survey Mode
                # pre_id_index = 13
                # post_id_index = 10
                # survey_mode(metadata_path, survey_path, cursor, pre_id_index, post_id_index)
                
                # print "Survey mode finished."
                
                ##################################
                #
                # The step following can be active if you 
                # need to save space on your computer
                #
                ##################################
                # log_files = os.listdir(log_path)
                # for log_file in log_files:
                #     os.remove(log_path + log_file)
                
                # Record translated course
                output_file.write(log_folder + "\n")
            
            except Exception as e:
            
                print "Error occurs when translating\t" + log_folder
                print e

    output_file.close()


###############################################################################
if __name__ == '__main__':

    main(sys.argv[1:])

    # data_path = "/Volumes/YuePassport/course_log_v2/"
    # daily_log_folder_path = "/Volumes/YuePassport/SurfDrive/Shared/WIS-EdX/logs/"
    # user='root'
    # password='123456'
    # host='127.0.0.1'
    # database='DelftX'
    # main(data_path, daily_log_folder_path, user, password, host, database)
    
    print "All finished."




            
