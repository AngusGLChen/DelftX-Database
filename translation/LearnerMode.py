'''
Created on Jun 16, 2016

@author: Angus
'''

import os, json, csv, datetime, operator
from translation.Functions import ExtractCourseInformation, cmp_datetime, getDayDiff, getNextDay, process_null

    
def learner_mode(metadata_path, cursor):
    
    course_record = []
    course_element_record = []
    learner_index_record = []
    course_learner_record = []
    learner_demographic_record = []
    
    # Collect course information
    course_metadata_map = ExtractCourseInformation(metadata_path)
    course_record.append([course_metadata_map["course_id"], course_metadata_map["course_name"], course_metadata_map["start_time"], course_metadata_map["end_time"]])
    
    # Course_element table     
    for element_id in course_metadata_map["element_time_map"].keys():
                
        element_start_time = course_metadata_map["element_time_map"][element_id]
        # Some contents released just one hour earlier than the hour of start time.
        # For example, start time is 2015-10-15 09:00:00, while 2nd week contents' release time is 2015-10-22 08:00:00.
        # However, those 2nd week contents are count as 1st week.
        # In order to avoid above situation, I use date to replace datetime here.
        week = getDayDiff(course_metadata_map["start_time"].date(), element_start_time.date()) / 7 + 1
        
        array = [element_id, course_metadata_map["element_type_map"][element_id], week, course_metadata_map["course_id"]]
        course_element_record.append(array)
    
    files = os.listdir(metadata_path)
    
    # Learner_demographic table
    learner_mail_map = {}
    
    # Course_learner table
    course_learner_map = {}
    
    # Enrolled learners set
    enrolled_learner_set = set()
    
    course_id = ""
    
    # Processing student_courseenrollment data  
    for file in files:       
        if "student_courseenrollment" in file:
            input_file = open(metadata_path + file, "r")
            input_file.readline()
            lines = input_file.readlines()
                        
            for line in lines:
                record = line.split("\t")
                global_learner_id = record[1]
                course_id = record[2]
                time = datetime.datetime.strptime(record[3],"%Y-%m-%d %H:%M:%S")
                course_learner_id = course_id + "_" + global_learner_id
                    
                if cmp_datetime(course_metadata_map["end_time"], time):           
                    enrolled_learner_set.add(global_learner_id)
                    
                    array = [global_learner_id, course_id, course_learner_id]
                    learner_index_record.append(array)

                    course_learner_map[global_learner_id] = course_learner_id
                    
            input_file.close()  
        
            print "The number of enrolled learners is: " + str(len(enrolled_learner_set)) + "\n"
  
    # Processing auth_user data  
    for file in files:               
        if "auth_user-" in file:
            input_file = open(metadata_path + file, "r")
            input_file.readline()
            lines = input_file.readlines()
            for line in lines:
                record = line.split("\t")
                if record[0] in enrolled_learner_set:
                    learner_mail_map[record[0]] = record[4]
            input_file.close()
                    
    # Processing certificates_generatedcertificate data
    num_uncertifiedLearners = 0
    num_certifiedLearners = 0    
    for file in files:       
        if "certificates_generatedcertificate" in file:
            input_file = open(metadata_path + file, "r")
            input_file.readline()
            lines = input_file.readlines()
            
            for line in lines:
                record = line.split("\t")
                global_learner_id = record[1]
                final_grade = record[3]
                enrollment_mode = record[14].replace("\n", "")
                certificate_status = record[7]                         
                
                if course_learner_map.has_key(global_learner_id):
                    num_certifiedLearners += 1
                    array = [course_learner_map[global_learner_id], final_grade, enrollment_mode, certificate_status]
                    course_learner_record.append(array)
                else:
                    num_uncertifiedLearners += 1
            
            input_file.close()

            print "The number of uncertified & certified learners is: " + str(num_uncertifiedLearners) + "\t" + str(num_certifiedLearners) + "\n"    
    
    # Processing auth_userprofile data                    
    for file in files:       
        if "auth_userprofile" in file:
            input_file = open(metadata_path + file, "r")
            input_file.readline()
            lines = input_file.readlines()
                        
            for line in lines:
                record = line.split("\t")
                global_learner_id = record[1]
                gender = record[7]
                year_of_birth = record[9]
                level_of_education = record[10]
                country = record[13]
                
                course_learner_id = course_id + "_" + global_learner_id
                                
                if global_learner_id in enrolled_learner_set:
                    array = [course_learner_id, gender, year_of_birth, level_of_education, country, learner_mail_map[global_learner_id]]
                    learner_demographic_record.append(array)            
            
            input_file.close()
            
    # Database version
    # Course table
    for array in course_record:
        course_id = course_metadata_map["course_id"]
        course_name = course_metadata_map["course_name"]
        start_time = course_metadata_map["start_time"]
        end_time = course_metadata_map["end_time"]
        sql = "insert into courses(course_id, course_name, start_time, end_time) values (%s,%s,%s,%s)" 
        data = (course_id, course_name, start_time, end_time)
        cursor.execute(sql, data)
        
    for array in course_element_record:
        element_id = array[0]
        element_type = array[1]
        week = process_null(array[2])
        course_id = array[3]
        sql = "insert into course_elements(element_id, element_type, week, course_id) values (%s,%s,%s,%s)" 
        data = (element_id, element_type, week, course_id)
        cursor.execute(sql, data)
    
    # Learner_index table
    for array in learner_index_record:
        global_learner_id = array[0]
        course_id = array[1]
        course_learner_id = array[2]
        sql = "insert into learner_index(global_learner_id, course_id, course_learner_id) values (%s,%s,%s)"
        data = (global_learner_id, course_id, course_learner_id)
        cursor.execute(sql, data)
    
    # Course_learner table
    for array in course_learner_record:
        course_learner_id = array[0]
        final_grade = process_null(array[1])
        enrollment_mode = array[2]
        certificate_status = array[3]
        sql = "insert into course_learner(course_learner_id, final_grade, enrollment_mode, certificate_status) values (%s,%s,%s,%s)"
        data = (course_learner_id, final_grade, enrollment_mode, certificate_status)
        cursor.execute(sql, data)
    
    # Learner_demographic table
    for array in learner_demographic_record:
        course_learner_id = process_null(array[0])
        gender = array[1]
        year_of_birth = process_null(process_null(array[2]))
        level_of_education = array[3]
        country = array[4]
        email = array[5]
        email = email.replace("\'", "")
        sql = "insert into learner_demographic(course_learner_id, gender, year_of_birth, level_of_education, country, email) values (%s,%s,%s,%s,%s,%s)"
        data = (course_learner_id, gender, year_of_birth, level_of_education, country, email)
        cursor.execute(sql, data)
    
    # File version
    '''
    pairs = [["courses", course_record], ["course_element", course_element_record], ["learner_index", learner_index_record], ["course_learner", course_learner_record], ["learner_demographic", learner_demographic_record]]
    for pair in pairs:
        output_path = "/Users/Angus/Downloads/" + pair[0]
        output_file = open(output_path, "w")
        writer = csv.writer(output_file)
        for array in pair[1]:
            writer.writerow(array)
        output_file.close()
    '''
        
def sessions(metadata_path, log_path, cursor):
    
    # Collect course information
    course_metadata_map = ExtractCourseInformation(metadata_path)
    
    current_date = course_metadata_map["start_date"]   
    end_next_date = getNextDay(course_metadata_map["end_date"])
    
    learner_all_event_logs = {}
    updated_learner_all_event_logs = {}
    session_record = []
    
    log_files = os.listdir(log_path)
    
    while True:
        
        if current_date == end_next_date:
            break;
        
        for file in log_files:           
            
            if current_date in file:
                
                print file

                learner_all_event_logs.clear()
                learner_all_event_logs = updated_learner_all_event_logs.copy()
                updated_learner_all_event_logs.clear()
                
                # Course_learner_id set
                course_learner_id_set = set()
                for course_learner_id in learner_all_event_logs.keys():
                    course_learner_id_set.add(course_learner_id)
                
                input_file = open(log_path + file,"r")
                lines = input_file.readlines()
                        
                for line in lines:
                    
                    jsonObject = json.loads(line)
                    
                    global_learner_id = jsonObject["context"]["user_id"]
                    event_type = str(jsonObject["event_type"])
                    
                    if global_learner_id != "":
                        course_id = jsonObject["context"]["course_id"]
                        course_learner_id = course_id + "_" + str(global_learner_id)
                        
                        event_time = jsonObject["time"]
                        event_time = event_time[0:19]
                        event_time = event_time.replace("T", " ")
                        event_time = datetime.datetime.strptime(event_time,"%Y-%m-%d %H:%M:%S")
                        
                        if course_learner_id in course_learner_id_set:
                            learner_all_event_logs[course_learner_id].append({"event_time":event_time, "event_type":event_type})
                        else:
                            learner_all_event_logs[course_learner_id] = [{"event_time":event_time, "event_type":event_type}]
                            course_learner_id_set.add(course_learner_id)
                     
                for course_learner_id in learner_all_event_logs.keys():
                                 
                    event_logs = learner_all_event_logs[course_learner_id]
                    
                    # Sorting
                    event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))
                      
                    session_id = ""
                    start_time = ""
                    end_time = ""
                    
                    final_time = ""
                    
                    for i in range(len(event_logs)):
                        
                        if start_time == "":
                            
                            # Initialization
                            start_time = event_logs[i]["event_time"]
                            end_time = event_logs[i]["event_time"]
                            
                        else:
                            
                            if event_logs[i]["event_time"] > end_time + datetime.timedelta(hours=0.5):
                                
                                session_id = course_learner_id + "_" + str(start_time) + "_" + str(end_time)
                                duration = (end_time - start_time).days * 24 * 60 * 60 + (end_time - start_time).seconds
                                
                                if duration > 5:
                                    array = [session_id, course_learner_id, start_time, end_time, duration]
                                    session_record.append(array)
                                    
                                final_time = event_logs[i]["event_time"]
                                    
                                # Re-initialization
                                session_id = ""
                                start_time = event_logs[i]["event_time"]
                                end_time = event_logs[i]["event_time"]
                            
                            else:
                                
                                if event_logs[i]["event_type"] == "page_close":
                                    
                                    end_time = event_logs[i]["event_time"]
                                    
                                    session_id = course_learner_id + "_" + str(start_time) + "_" + str(end_time)
                                    duration = (end_time - start_time).days * 24 * 60 * 60 + (end_time - start_time).seconds
                                
                                    if duration > 5:
                                        array = [session_id, course_learner_id, start_time, end_time, duration]
                                        session_record.append(array)
                                        
                                    # Re-initialization
                                    session_id = ""
                                    start_time = ""
                                    end_time = ""
                                    
                                    final_time = event_logs[i]["event_time"]
                                    
                                else:
                                    
                                    end_time = event_logs[i]["event_time"]
                        
                    if final_time != "":
                        new_logs = []                
                        for log in event_logs:                 
                            if log["event_time"] >= final_time:
                                new_logs.append(log)
                                
                        updated_learner_all_event_logs[course_learner_id] = new_logs
                        
        current_date = getNextDay(current_date)
    
    # Filter duplicated records
    updated_session_record = []
    session_id_set = set()
    for array in session_record:
        session_id = array[0]
        if session_id not in session_id_set:
            session_id_set.add(session_id)
            updated_session_record.append(array)
            
    session_record = updated_session_record
    
    # Database version
    for array in session_record:
        session_id = array[0]
        course_learner_id = array[1]
        start_time = array[2]
        end_time = array[3]
        duration = process_null(array[4])
        sql = "insert into sessions(session_id, course_learner_id, start_time, end_time, duration) values (%s,%s,%s,%s,%s)"
        data = (session_id, course_learner_id, start_time, end_time, duration)
        cursor.execute(sql, data)
        
            
    # File version
    '''
    output_path = "/Users/Angus/Downloads/sessions"
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    for array in session_record:
        writer.writerow(array)
    output_file.close()
    '''