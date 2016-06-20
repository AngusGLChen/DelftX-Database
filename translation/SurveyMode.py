'''
Created on Jun 16, 2016

@author: Angus
'''

import os,csv,mysql.connector
from translation.Functions import ExtractCourseInformation

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def survey_mode(metadata_path, survey_path, cursor, pre_id_index, post_id_index):
    
    description_records = []
    response_records = []
    
    # Collect course information
    course_metadata_map = ExtractCourseInformation(metadata_path)
    course_id = course_metadata_map["course_id"]
    
    files = os.listdir(survey_path)
    
    learner_id_map = {}
    
    # Processing ID information
    for file in files:
        if "anon-ids.csv" in file:
            id_file = open(survey_path + file, "r")
            id_reader = csv.reader(id_file)
            id_reader.next()
            for row in id_reader:
                global_id = row[0].replace("\"","")
                anonymized_id = row[1].replace("\"","")
                learner_id_map[anonymized_id] = global_id
    
    # Processing Pre-survey information      
    for file in files:    
        if "pre-survey" in file:
            pre_file = open(survey_path + file, "r")
            pre_reader = csv.reader(pre_file)
            
            question_id_row = pre_reader.next()
            question_description_row = pre_reader.next()
                                               
            for i in range(len(list(question_id_row))):
                question_id = course_id + "_pre_" + question_id_row[i].replace("\"","")
                question_description = question_description_row[i].replace("\'", "\\'")
                array = [question_id, course_id, "pre", question_description]
                description_records.append(array)
                
            for row in pre_reader:
                learner_id = row[pre_id_index]
                print learner_id
                if learner_id in learner_id_map.keys():
                    course_learner_id = course_id + "_" + learner_id_map[learner_id]
                    
                    for i in range(len(list(question_id_row))):
                        question_id = course_id + "_pre_" + question_id_row[i].replace("\"","")
                        response_id = course_learner_id + "_" + "pre" + "_" + question_id_row[i].replace("\"","")
                        answer = row[i]
                        
                        array = [response_id, course_learner_id, question_id, answer]
                        response_records.append(array)           
            pre_file.close()

    # Processing Post-survey information      
    for file in files:    
        if "post-survey" in file:
            post_file = open(survey_path + file, "r")
            post_reader = csv.reader(post_file)
            
            question_id_row = post_reader.next()
            question_description_row = post_reader.next()
                                               
            for i in range(len(list(question_id_row))):
                question_id = course_id + "_post_" + question_id_row[i].replace("\"","")
                question_description = question_description_row[i].replace("\'", "\\'")
                array = [question_id, course_id, "post", question_description]
                description_records.append(array)
                
            for row in post_reader:
                learner_id = row[post_id_index]
                if learner_id in learner_id_map.keys():
                    course_learner_id = course_id + "_" + learner_id_map[learner_id]
                    
                    for i in range(len(list(question_id_row))):
                        question_id = course_id + "_post_" + question_id_row[i].replace("\"","")
                        response_id = course_learner_id + "_post_" + question_id_row[i].replace("\"","")
                        answer = row[i]
                        
                        array = [response_id, course_learner_id, question_id, answer]
                        response_records.append(array)
            post_file.close()
    
    # Database version
    for array in description_records:
        question_id = array[0]
        course_id = array[1]
        question_type = array[2]
        question_description = array[3]
        sql = "insert into survey_descriptions (question_id, course_id, question_type, question_description) values"
        sql += "('%s','%s','%s','%s');\r\n" % (question_id, course_id, question_type, question_description) 
        cursor.execute(sql)
        
    for array in response_records:
        response_id = array[0]
        course_learner_id = array[1]
        question_id = array[2]
        answer = array[3]
        sql = "insert into survey_responses (response_id, course_learner_id, question_id, answer) values"
        sql += "('%s','%s','%s','%s');\r\n" % (response_id, course_learner_id, question_id, answer)
        cursor.execute(sql)
    '''               
    # File version
    output_path = "/Users/Angus/Downloads/survey_descriptions"
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    for array in description_records:
        writer.writerow(array)
    output_file.close()
    
    output_path = "/Users/Angus/Downloads/survey_responses"
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    for array in response_records:
        writer.writerow(array)
    output_file.close()
    '''