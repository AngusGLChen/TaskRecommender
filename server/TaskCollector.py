'''
Created on Aug 17, 2016

@author: Angus
'''

import os, upwork, time, mysql.connector, json
from sklearn.feature_extraction.text import CountVectorizer 

    
def CollectTaskWithKeywords(client, data, cursor, course_content_map):
    
    page_num = 1
    page_size = 100
    
    num_retrieve_tasks = ""
    
    while num_retrieve_tasks != 0:
        
        tasks = client.provider_v2.search_jobs(data=data, page_offset=page_num*page_size, page_size=page_size)
        num_retrieve_tasks = len(tasks)
       
        for task in tasks:                
            job_status = task["job_status"]
            
            if job_status == "Open":
                job_status = True
            else:
                job_status = False
            
            category2 = task["category2"]
            
            title = task["title"]
            if title != None:
                title = title.encode( "utf-8" )
                title = title.replace("'", "\'")
            
            skills = task["skills"]
            
            
            job_type = task["job_type"]
            budget = task["budget"]
            
            snippet = task["snippet"]
            if snippet != None:
                snippet = snippet.encode( "utf-8" )
                snippet = snippet.replace("'", "\'")
            
            url = task["url"]
            workload = task["workload"]
            subcategory2 = task["subcategory2"]
            duration = task["duration"]
            date_created = task["date_created"]
            task_id = task["id"]
               
            suitable_mark = True
            times_recommended = 0
            
            # Task filtering
            if job_type == "Hourly" or budget > 100:
                suitable_mark = False
                
            # Task relevance estimation
            relevance_array = []
            for week in range(1,9):
                keywords = course_content_map[str(week)]
                
                keywords.append("excel")
                keywords.append("spreadsheet")
                keywords.append("vba")
                keywords.append("python")                           
                
                # Skill relevance
                skill_relevance = 0
                '''
                for keyword in keywords:
                    for skill in skills:
                        if keyword in skill:
                            skill_relevance += 1
                '''
                skill_array = ["microsoft-excel", "excel-vba", "google-spreadsheet", "spreadsheets", "data-analysis", "vba", "python", "microsoft-excel-powerpivot", "data-science", "microsoft-office"]
                for skill in skills:
                    if skill in skill_array:
                        skill_relevance += 1
                skill_relevance = skill_relevance/float(len(skill_array))
                                
                vectorizer = CountVectorizer(ngram_range=(1,1), stop_words="english")
                analyzer = vectorizer.build_analyzer()
                
                # Title relevance
                title_relevance = 0
                if title != None:
                    terms = analyzer(title)                    
                    for term in terms:
                        if term in keywords:
                            title_relevance += 1
                title_relevance = title_relevance/float(len(keywords))
                
                # Snippet relevance
                snippet_relevance = 0
                if snippet != None:
                    terms = analyzer(snippet)
                    for term in terms:
                        if term in keywords:
                            snippet_relevance += 1
                snippet_relevance = snippet_relevance/float(len(keywords))
                
                            
                overall_relevance = 0.5*skill_relevance + 0.25*title_relevance + 0.25*snippet_relevance                
                relevance_array.append(overall_relevance)
                
            skills = ','.join(skills)
            
            array = (job_status, category2, title, skills, job_type, 
                     budget, snippet, url, workload, 
                     subcategory2, duration, date_created, task_id, suitable_mark, 
                     relevance_array[0], relevance_array[1], relevance_array[2], relevance_array[3], relevance_array[4], 
                     relevance_array[5], relevance_array[6], relevance_array[7], times_recommended)
            sql = "insert into tasks (job_status, category2, title, skills, job_type, \
                                      budget, snippet, url, workload, \
                                      subcategory2, duration, date_created, id, suitable_mark, \
                                      relevance_week_1, relevance_week_2, relevance_week_3, relevance_week_4, relevance_week_5, \
                                      relevance_week_6, relevance_week_7, relevance_week_8, times_recommended) \
                                      values (%s, %s, %s, %s, %s,\
                                              %s, %s, %s, %s,\
                                              %s, %s, %s, %s, %s,\
                                              %s, %s, %s, %s, %s,\
                                              %s, %s, %s, %s)"                                              
            
            try:
                cursor.execute(sql, array)
            except Exception as e:                
                pass
                    
        page_num += 1                
        time.sleep(15)


def CollectTasks(public_key, secret_key, certificate_path, mysql_profile, course_content_path):
    
    # Set HTTP certificate
    os.environ['HTTPLIB_CA_CERTS_PATH'] = certificate_path
    
    # Read course content
    input_file = open(course_content_path, "r")
    course_content_map = json.loads(input_file.read())

    client = upwork.Client(public_key, secret_key)
    print client.auth.get_authorize_url()    
    verifier = raw_input('Enter oauth_verifier: ')    
    oauth_access_token, oauth_access_token_secret = client.auth.get_access_token(verifier)    
    client = upwork.Client(public_key, secret_key, oauth_access_token=oauth_access_token, oauth_access_token_secret=oauth_access_token_secret)
    
    while True:
        
        # Connect database
        connection = mysql.connector.connect(user=mysql_profile["user"], password=mysql_profile["password"], host=mysql_profile["host"], database=mysql_profile["database"])
        cursor = connection.cursor()
        
        # Keyword "excel"   
        data = {'q': 'excel'}    
        CollectTaskWithKeywords(client, data, cursor, course_content_map)
        
        # Keyword "spreadsheet"   
        data = {'q': 'spreadsheet'}
        CollectTaskWithKeywords(client, data, cursor, course_content_map)
        
        print "Finish crawlling...\t"
        
        connection.close()
        
        time.sleep(15*60)
        
        # Check tasks' availability
        print "Start checking tasks' status..."
        
        # Connect database
        connection = mysql.connector.connect(user=mysql_profile["user"], password=mysql_profile["password"], host=mysql_profile["host"], database=mysql_profile["database"])
        cursor = connection.cursor()
        
        sql = "select tasks.id from tasks where tasks.job_status = True"
        cursor.execute(sql)
        results = cursor.fetchall()
        for result in results:
            task_id = str(result[0])
            
            job_status = ""
            
            try:
                job_profile = client.job.get_job_profile(task_id)
                job_status = job_profile["ui_opening_status"]
            except Exception as e:
                job_status = "Closed"
                
            if job_status == "Closed":
                sql = "update tasks set tasks.job_status=False where tasks.id = '" + task_id + "'"
                cursor.execute(sql)
                print "Update\t" + str(task_id)
                print     

            time.sleep(10)
        
        connection.close()
          
        time.sleep(6*60*60)



public_key = "e33d7ea25cc6f485ab9205875771ae42"
secret_key = "a715e615e810696d"
certificate_path = '/root/cacert.pem'
course_content_path = "/root/course_content"

mysql_profile = {"user": "root",
                 "password": "",
                 "host": "127.0.0.1",
                 "database": "UpworkTasks"}

CollectTasks(public_key, secret_key, certificate_path, mysql_profile, course_content_path)












