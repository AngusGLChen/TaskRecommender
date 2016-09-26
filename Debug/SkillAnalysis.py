'''
Created on Sep 23, 2016

@author: Angus
'''

import mysql.connector, operator


def AnalyzeSkills():
    
    connection = mysql.connector.connect(user="dan", password="QgPLI26qLuWrffDy", host="145.100.59.133", database="UpworkTasks")
    cursor = connection.cursor()
    
    sql = "SELECT tasks.skills FROM tasks where tasks.suitable_mark = True;"
    cursor.execute(sql)
    results = cursor.fetchall()
    
    skill_frequency_map = {}
    skill_set = set()
    
    for result in results:
        skills = result[0]
        skills = skills.split(",")
        for skill in skills:
            if skill not in skill_set:
                skill_set.add(skill)
                skill_frequency_map[skill] = 0
                
            skill_frequency_map[skill] += 1
            
    sorted_skill_map = sorted(skill_frequency_map.items(), key=operator.itemgetter(1), reverse=True)
    
    for i in range(200):
        print sorted_skill_map[i][0] + "\t" + str(sorted_skill_map[i][1])
        

AnalyzeSkills()

            
            
        
        
        
