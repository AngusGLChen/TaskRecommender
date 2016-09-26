#!/usr/bin/python3

# Turn on debug mode.
import cgitb
cgitb.enable()

import math, random, pymysql, json, cgi

form = cgi.FieldStorage()
    
# Print necessary headers.
print("Content-Type: text/html")
print()


connection = pymysql.connect(user="root", password="glchenmorepapers", host="localhost", database="UpworkTasks")
cursor = connection.cursor()

week = form["week"]
print(week)
tasks = {}    
sql = "SELECT tasks.id, tasks.title, tasks.snippet, tasks.budget, tasks.url, tasks.skills, tasks.relevance_week_" + str(week) + ", tasks.times_recommended FROM UpworkTasks.tasks where tasks.job_status = true and tasks.suitable_mark = True;"
cursor.execute(sql)
results = cursor.fetchall()

task_array = []

for result in results:        
    task_id = result[0]
    title = result[1]
    snippet = result[2]
    budget = result[3]
    url = result[4]
    skills = result[5]
    relevance = result[6]
    times_recommended = result[7]
    
    score = math.log(relevance + 1) + math.log(times_recommended + 1)
    score = score * random.random()

    task_array.append({"task_id": task_id, "title": title, "snippet": snippet, "budget": budget, "url": url, "score": score, "skills":skills})
    
sorted_task_array = sorted(task_array, key = lambda x:x['score'], reverse=True)

retrieved_tasks = []

'''
for i in range(3):
    retrieved_tasks.append(sorted_task_array[i])
'''

for i in range(len(sorted_task_array)):
    budget = float(sorted_task_array[i]["budget"])
    if budget <= 50:
        retrieved_tasks.append(sorted_task_array[i])
        break

for i in range(len(sorted_task_array)):
    budget = float(sorted_task_array[i]["budget"])
    if budget <= 100 and budget > 50:
        retrieved_tasks.append(sorted_task_array[i])
        break


# Update time_recommendation
for task in retrieved_tasks:        
    task_id = task["task_id"]
    sql = "select tasks.times_recommended from tasks where tasks.id = '" + task_id + "';"
    cursor.execute(sql)
    value = cursor.fetchone()[0] + 1
    
    sql = "update tasks set tasks.times_recommended=" + str(value) + " where tasks.id = '" + task_id + "'"
    cursor.execute(sql)        
    
body = json.JSONEncoder().encode(retrieved_tasks)
#print("Status: 200 OK")
#print("Content-Type: application/json")
#print("Length:", str(len(body)))
#print("")
print(body)