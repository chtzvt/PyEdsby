"""
 commonClassmates.py - Find people you have multiple classes with, via Edsby
 (c) 2017 Charlton Trezevant - MIT License
 Enjoy!
"""

import requests, json
from edsby import Edsby

# Given the value of getAllClassRosters, this function returns a dict of students filtered by
# commonality- that is, the students returned have multiple classes with you.
def filterCommonClassmates(classData):
    # These loops prepare each class for search by creating an array of student NIDs for each class
    # We can then find common students by searching for their NIDs in this array
    for classEntry in classData:
      classData[classEntry]['studentNIDs'] = list()

      for student in classData[classEntry]['classmates']:
        classData[classEntry]['studentNIDs'].append(classData[classEntry]['classmates'][student]['nid'])

    # This will be the dict of common classmates returned.
    commonClassmates = dict()

    for classEntry in classData:  # For each class NID
      for student in classData[classEntry]['classmates']:  # For each student in the roster of the current class
        if classData[classEntry]['classmates'][student]['nid'] in classData[classEntry]['studentNIDs']: # If the current student NID is in the list of all NIDs for the current class
            studentNID = classData[classEntry]['classmates'][student]['nid'] # Makes the student ID index much easier to read

            if studentNID not in commonClassmates: # If we haven't made a dict for a classmate we've found in other classes
              commonClassmates[studentNID] = dict()

            if 'class_nids' not in commonClassmates[studentNID]: # If the class_nids prop does not exist in the classmate's dict
              commonClassmates[studentNID]['class_nids'] = list()

            if 'human_names' not in commonClassmates[studentNID]: # if the human course names array does not exist in the classmate's dict
              commonClassmates[studentNID]['human_names'] = list()

            if 'name' not in commonClassmates[studentNID]: # if the classmate's name array does not exist
              commonClassmates[studentNID]['name'] = list()

            if classEntry not in commonClassmates[studentNID]['class_nids']: # If we haven't appended the common class NIDs to the student's dict entry yet
              commonClassmates[studentNID]['class_nids'].append(classEntry) # Add to common classmates dict

            if classData[classEntry]['human_name'] not in commonClassmates[studentNID]['human_names']: # If we haven't added the human readable class name yet
              commonClassmates[studentNID]['human_names'].append(classData[classEntry]['human_name']) # Add to common classmates dict

            if classData[classEntry]['classmates'][student]['FirstName'] not in commonClassmates[studentNID]['name']: # If we haven't added the student's name data yet
              # Tuple of available name data. Sometimes MName is not present, so there's a ternary expression for the middle name
              studentName = (classData[classEntry]['classmates'][student]['FirstName'], (classData[classEntry]['classmates'][student]['MName'] if 'MName' in classData[classEntry]['classmates'][student] else ''), classData[classEntry]['classmates'][student]['LastName'])
              commonClassmates[studentNID]['name'].extend(studentName) # Add to common classmates dict

    return commonClassmates

# Given the commonClassmates dict, this function prints a quick, formatted summary.
def printStudentList(commonClassmates):
    for student in commonClassmates:
      if len(commonClassmates[student]['class_nids']) > 1 and notPrinted:
        print ' '.join(commonClassmates[student]['name']) +': '+ ','.join(commonClassmates[student]['human_names'])

edsby = Edsby(host='your_host.edsby.com', username='your_username', password='your_password')

# Retrieve the full rosters of students, in each one of your classes
classData = edsby.getAllClassRosters()

# Filter the list of all classmates by only students who are members of multiple classes that you, the user, have.
filtered = filterCommonClassmates(classData)

# Print a summary of the filtered classmate data
printStudentList(filtered)
