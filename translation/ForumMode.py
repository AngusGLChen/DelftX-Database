'''
Created on Jun 11, 2016

@author: Angus
'''


import os,json,datetime,csv,operator
from time import *
from translation.Functions import ExtractCourseInformation,getNextDay,cmp_datetime

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def forum_interaction(metadata_path, cursor):
    
    forum_interaction_records = []
    
    # Collect course information
    course_metadata_map = ExtractCourseInformation(metadata_path)
    
    # Processing forum data
    files = os.listdir(metadata_path)     
    for file in files:
        if ".mongo" in file:
            forum_file = open(metadata_path + file,"r")   
            for line in forum_file:
                jsonObject = json.loads(line)
                   
                post_id = jsonObject["_id"]["$oid"]                
                course_learner_id = jsonObject["course_id"] + "_" + jsonObject["author_id"]                

                post_type = jsonObject["_type"]
                if post_type == "CommentThread":
                    post_type += "_" + jsonObject["thread_type"]                
                if "parent_id" in jsonObject and jsonObject["parent_id"] != "":
                    post_type = "Comment_Reply"
                
                post_title = ""
                if "title" in jsonObject:
                    post_title=jsonObject["title"]
                
                post_content = jsonObject["body"]
                
                post_timestamp = jsonObject["created_at"]["$date"]
                if type(post_timestamp) == type(100):
                    post_timestamp = strftime("%Y-%m-%d %H:%M:%S",gmtime(post_timestamp/1000))
                    post_timestamp = datetime.datetime.strptime(post_timestamp,"%Y-%m-%d %H:%M:%S")
                if isinstance(post_timestamp, unicode):
                    post_timestamp = post_timestamp[0:19]
                    post_timestamp = post_timestamp.replace("T", " ")
                    post_timestamp = datetime.datetime.strptime(post_timestamp,"%Y-%m-%d %H:%M:%S")
                
                post_parent_id = ""
                if "parent_id" in jsonObject:
                    post_parent_id = jsonObject["parent_id"]["$oid"]
                
                post_thread_id = ""    
                if "comment_thread_id" in jsonObject:
                    post_thread_id = jsonObject["comment_thread_id"]["$oid"]                
                
                post_title = post_title.replace("\n", " ")
                post_title = post_title.replace("\\", "\\\\")
                post_title = post_title.replace("\'", "\\'")
                
                post_content = post_content.replace("\n", " ")
                post_content = post_content.replace("\\", "\\\\")
                post_content = post_content.replace("\'", "\\'")
                
                if post_timestamp < course_metadata_map["end_time"]:
                    
                    array = [post_id, course_learner_id, post_type, post_title, post_content, post_timestamp, post_parent_id, post_thread_id]
                    forum_interaction_records.append(array)
                    
            forum_file.close()
    
    # Database version
    for array in forum_interaction_records:
        post_id = array[0]
        course_learner_id = array[1]
        post_type = array[2]
        post_title = array[3]
        post_content = array[4]
        post_timestamp = array[5]
        post_parent_id = array[6]
        post_thread_id = array[7]
        sql = "insert into forum_interaction(post_id, course_learner_id, post_type, post_title, post_content, post_timestamp, post_parent_id, post_thread_id) values"
        sql += "('%s','%s','%s','%s','%s','%s','%s', '%s');" % (post_id, course_learner_id, post_type, post_title, post_content, post_timestamp, post_parent_id, post_thread_id)  

        cursor.execute(sql)
            
    # File version
    '''
    output_path = "/Users/Angus/Downloads/forum_interaction"
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    for array in forum_interaction_records:
        writer.writerow(array)
    output_file.close()
    '''
    

def forum_sessions(metadata_path, log_path, cursor):
    
    # Collect course information
    course_metadata_map = ExtractCourseInformation(metadata_path)
    
    start_date = course_metadata_map["start_date"]
    end_date = course_metadata_map["end_date"]

    current_date = start_date   
    end_next_date = getNextDay(end_date)
    
    forum_event_types = []
    forum_event_types.append("edx.forum.comment.created")
    forum_event_types.append("edx.forum.response.created")
    forum_event_types.append("edx.forum.response.voted")
    forum_event_types.append("edx.forum.thread.created")
    forum_event_types.append("edx.forum.thread.voted")
    forum_event_types.append("edx.forum.searched")
        
    learner_all_event_logs = {}
    updated_learner_all_event_logs = {}
    
    forum_sessions_record = []
    
    log_files = os.listdir(log_path)
    
    while True:
        
        if current_date == end_next_date:
            break;
        
        for log_file in log_files:
            
            if current_date in log_file:                
                
                print log_file 
                learner_all_event_logs.clear()
                learner_all_event_logs = updated_learner_all_event_logs.copy()
                updated_learner_all_event_logs.clear()
                
                # Course_learner_id set
                course_learner_id_set = set()
                for course_learner_id in learner_all_event_logs.keys():
                    course_learner_id_set.add(course_learner_id)

                log_file = open(log_path + log_file,"r")
                lines = log_file.readlines()
                        
                for line in lines:
                    
                    jsonObject = json.loads(line)
                    
                    # For forum session separation
                    global_learner_id = jsonObject["context"]["user_id"]
                    event_type = str(jsonObject["event_type"])
                    
                    if "/discussion/" in event_type or event_type in forum_event_types:
                        if event_type != "edx.forum.searched":
                            event_type = "forum_activity"
                                            
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
                            
                # For forum session separation
                for learner in learner_all_event_logs.keys():
                    
                    course_learner_id = learner                    
                    event_logs = learner_all_event_logs[learner]
                    
                    # Sorting
                    event_logs.sort(cmp=cmp_datetime, key=operator.itemgetter('event_time'))
                    
                    session_id = ""
                    start_time = ""
                    end_time = ""                    
                    times_search = 0
                    
                    final_time = ""
                    
                    for i in range(len(event_logs)):
                        
                        if session_id =="":                            
                            
                            if event_logs[i]["event_type"] in ["forum_activity", "edx.forum.searched"]:
                                # Initialization
                                session_id = "forum_session_" + course_learner_id
                                start_time = event_logs[i]["event_time"]
                                end_time = event_logs[i]["event_time"]
                                if event_logs[i]["event_type"] == "edx.forum.searched":
                                    times_search += 1                                                        
                        else:
                            
                            if event_logs[i]["event_type"] in ["forum_activity", "edx.forum.searched"]:

                                if event_logs[i]["event_time"] > end_time + datetime.timedelta(hours=0.5):
                                    
                                    session_id = session_id + "_" + str(start_time) + "_" + str(end_time)
                                    duration = (end_time - start_time).days * 24 * 60 * 60 + (end_time - start_time).seconds
                                    
                                    if duration > 5:
                                        array = [session_id, course_learner_id, times_search, start_time, end_time, duration]
                                        forum_sessions_record.append(array)
                                    
                                    final_time = event_logs[i]["event_time"]
                                    
                                    # Re-initialization
                                    session_id = "forum_session_" + course_learner_id
                                    start_time = event_logs[i]["event_time"]
                                    end_time = event_logs[i]["event_time"]
                                    if event_logs[i]["event_type"] == "edx.forum.searched":
                                        times_search = 1
                                        
                                else:
                                    
                                    end_time = event_logs[i]["event_time"]
                                    if event_logs[i]["event_type"] == "edx.forum.searched":
                                        times_search += 1
                                                        
                            else:
                                
                                end_time = event_logs[i]["event_time"]
                                session_id = session_id + "_" + str(start_time) + "_" + str(end_time)
                                duration = (end_time - start_time).days * 24 * 60 * 60 + (end_time - start_time).seconds
                                
                                if duration > 5:     
                                    array = [session_id, course_learner_id, times_search, start_time, end_time, duration]
                                    forum_sessions_record.append(array)
                                    
                                final_time = event_logs[i]["event_time"]
                                    
                                # Re-initialization
                                session_id = ""
                                start_time = ""
                                end_time = ""
                                times_search = 0
  
                    if final_time != "":
                        new_logs = []                
                        for log in event_logs:                 
                            if log["event_time"] >= final_time:
                                new_logs.append(log)
                                
                        updated_learner_all_event_logs[course_learner_id] = new_logs
                
                log_file.close()
                
        current_date = getNextDay(current_date)
    
    # Database version
    for array in forum_sessions_record:
        session_id = array[0]
        course_learner_id = array[1]
        times_search = array[2]
        start_time = array[3]
        end_time = array[4]
        duration = array[5]
        sql = "insert into forum_sessions (session_id, course_learner_id, times_search, start_time, end_time, duration) values"
        sql += "('%s','%s','%s','%s', '%s','%s');" % (session_id, course_learner_id, times_search, start_time, end_time, duration)
        cursor.execute(sql)
            
    # File version
    '''
    output_path = "/Users/Angus/Downloads/forum_sessions"
    output_file = open(output_path, "w")
    writer = csv.writer(output_file)
    for array in forum_sessions_record:
        writer.writerow(array)
    output_file.close()
    '''