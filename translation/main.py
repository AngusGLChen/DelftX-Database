'''
Created on Jun 18, 2016

@author: Angus
'''

import os,gzip,mysql.connector,json

from translation.LearnerMode import learner_mode, sessions
from translation.ForumMode import forum_interaction, forum_sessions
from translation.VideoMode import video_interaction
from translation.QuizMode import quiz_mode, quiz_sessions


def main(data_path, user, password, host, database):
    
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

    # Search for the courses that have not been translated
    log_folders = os.listdir(data_path)
    for log_folder in log_folders:
        
        if not os.path.isdir(data_path + log_folder):
            continue
        
        if not log_folder in translated_courses:
            try:
                
                print "Start to translating course\t" + log_folder
            
                # zip_files & unzip_files folder path
                zip_folder_path = data_path + log_folder + "/zip_files/"
                unzip_folder_path = data_path + log_folder + "/unzip_files/"
                metadata_path = data_path + log_folder + "/metadata/"
                
                if not os.path.exists(unzip_folder_path):
                    os.mkdir(unzip_folder_path)
                
                # Uncompress the log files
                log_files = os.listdir(zip_folder_path)
                for log_file in log_files:                
                    if ".gz" in log_file:
                        gz_file = gzip.GzipFile(zip_folder_path + log_file)
                        log_file = log_file.replace(".gz", "")
                        open(unzip_folder_path + log_file, "w+").write(gz_file.read())
                        gz_file.close()
                    
                # Filter out irrelevant records
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
                                    
                filter_folder_path = data_path + "filter_folder/"
                if not os.path.exists(filter_folder_path):
                    os.mkdir(filter_folder_path)
                
                log_files = os.listdir(unzip_folder_path)
                for file in log_files:
                    
                    filter_file_path = filter_folder_path + file
                    filter_file = open(filter_file_path, 'wb')
                    
                    unfilter_file_path = unzip_folder_path + file
                    input_file = open(unfilter_file_path,"r")   
                    for line in input_file:
                        jsonObject = json.loads(line)
                        if course_id in jsonObject["context"]["course_id"]:
                            filter_file.write(line)        
                    filter_file.close()
                    input_file.close()
                
                # Remove unzip files
                for file in log_files:
                    os.remove(unzip_folder_path + log_file)
                    
                # Translate the log files
                log_path = filter_file_path
                
                # 1. Learner Mode
                learner_mode(metadata_path, cursor)
                sessions(metadata_path, log_path, cursor)
                
                print "Learner mode finished."
                
                # 2. Forum Mode
                forum_interaction(metadata_path, cursor)
                forum_sessions(metadata_path, log_path, cursor)
                
                print "Forum mode finished."
                
                # 3. Video Mode
                video_interaction(metadata_path, log_path, cursor)
                
                print "Video mode finished."
                
                # 4. Quiz Mode
                quiz_mode(metadata_path, log_path, cursor)
                quiz_sessions(metadata_path, log_path, cursor)
                
                print "Quiz mode finished."
                
                # 5. Survey Mode
                # pre_id_index = 13
                # post_id_index = 10
                # survey_mode(metadata_path, survey_path, cursor, pre_id_index, post_id_index)
                
                print "Survey mode finished."
                
                log_files = os.listdir(log_path)
                for log_file in log_files:
                    os.remove(log_path + log_file)
                
                # Record translated course
                output_file.write(log_folder + "\n")
            
            except Exception as e:
            
                print "Error occurs when translating\t" + log_folder
                print e

    output_file.close()


###############################################################################
if __name__ == '__main__':
    
    data_path = ""
    user='root'
    password=''
    host='127.0.0.1'
    database='DelftX'
    main(data_path, user, password, host, database)
    
    print "All finished."




            
