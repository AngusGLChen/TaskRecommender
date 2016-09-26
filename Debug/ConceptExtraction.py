'''
Created on Aug 22, 2016

@author: Angus
'''

import os, operator
from sklearn.feature_extraction.text import CountVectorizer 

def FindFrequentTerms(array, k):    
    
    terms_map = {}
    terms_set = set()
    
    for term in array:
        if term not in terms_set:
            terms_map[term] = 0
            terms_set.add(term)
        terms_map[term] += 1
    
    sorted_terms_map = sorted(terms_map.items(), key=operator.itemgetter(1), reverse=True)
    
    frequent_terms = []
    for i in range(k):
        frequent_terms.append([sorted_terms_map[i][0], sorted_terms_map[i][1]])        
    return frequent_terms
    

def ExtractConcepts(path):
    
    week_script_map = {}
    
    folders = os.listdir(path)
    for folder in folders:
        
        if folder == ".DS_Store":
            continue    
        
        if folder not in week_script_map.keys():
            week_script_map[folder] = ""
        
        files = os.listdir(path + folder + "/")
        
        for file in files:            
            input_file = open(path + folder + "/" + file)
            lines = input_file.readlines()
            
            script = ""
            start_index = 1
            
            for line in lines:
                if line != "\n" and " --> " not in line:
                    line = line.replace("\n", "")
                    if str(start_index) == line:
                        start_index += 1
                    else:
                        script += line + " "
                        
            week_script_map[folder] += script + " "
            
    for week in week_script_map.keys():
        script = week_script_map[week]
        vectorizer = CountVectorizer(ngram_range=(1,2), stop_words="english")
        analyzer = vectorizer.build_analyzer()
        array = analyzer(script)
        
        frequent_terms = FindFrequentTerms(array, 20)
        
        print week
        for term in frequent_terms:
            print term
        print

path = "/Users/Angus/Downloads/video_scripts/"
ExtractConcepts(path)
print "Finished."



