from edsby import Edsby
import requests, json, random

edsby = Edsby(host='your_edsbyhost.edsby.com', username='your_username', password='your_password')

print("Your grades:")
courses = edsby.getAllClassAverages()
for entry in courses:
    print('\t' + courses[entry]['human_name'] + " : " + str(courses[entry]['average']) + "%")

# Randomly selects a course and prints all graded assignments from it
randomCourse = random.sample(courses, 1)
courseNID = randomCourse[0]
courseRID = courses[randomCourse[0]]['rid']

print('\nAssignment summary for ' + courses[randomCourse[0]]['human_name'] + ':')
assignmentSummary = edsby.getClassAssignmentList(courseNID, courseRID)
for entry in assignmentSummary['assignments']:
    assignment = assignmentSummary['assignments'][entry]

    score = assignment['scorePercentage'] if 'scorePercentage' in assignment else assignment['score'].upper()
    print('\t' + assignment['name'] + " : " + str(score))

print('Your grade in ' + courses[randomCourse[0]]['human_name'] + ' is currently ' + str(
    courses[randomCourse[0]]['average']) + '%.')
