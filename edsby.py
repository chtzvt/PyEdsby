import requests, json

"""
    Edsby.py: An API wrapper/library for Python - v0.2
    https://github.com/ctrezevant/PyEdsby/

    (c) 2017 Charlton Trezevant - www.ctis.me
    MIT License

    The Edsby trademark and brand are property of CoreFour, Inc.
    This software is unofficial and not supported by CoreFour in any way.
"""

class Edsby(object):
    def __init__(self, **kwargs):
        self.edsbyHost = kwargs['host']

        if 'headers' in kwargs:
            self.globalHeaders = kwargs['headers']
        else:
            self.globalHeaders = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0 Safari/601.1',
                'referer': 'https://'+self.edsbyHost+'/',
                'accept': '*/*',
                'accept-language':'en-US,en',
                'dnt': '1',
                'x-requested-with':'XMLHttpRequest'
            }

        if 'username' in kwargs and 'password' in kwargs:
            self.login(username=kwargs['username'], password=kwargs['password'])

        if 'cookies' in kwargs:
            self.setCookies(kwargs['cookies'])

        if 'headers' in kwargs:
            self.setHeaders(kwargs['headers'])

        if 'studentData' in kwargs:
            self.setStudentData(kwargs['studentData'])

    """
        Authenticates the session, retrieves student metadata, and
        hits required API endpoints (the Edsby API is stateful, so some things must
        be done in a certain order, before others)
    """
    def login(self, **kwargs):
        self.session = self.getSession()
        self.authData = self.getauthData((kwargs['username'], kwargs['password']))
        self.studentData = self.sendAuthenticationData()
        self.getBaseStudentData()  # Seems like I have to hit this endpoint before calling many of the methods available
        return True

    """
        Allows headers to be changed after instantiation (for imitating a mobile device, for example)
    """
    def setHeaders(self, headers):
        self.globalHeaders = headers

    """
        Returns the HTTP headers currently in use for all API calls
    """
    def getHeaders(self, headers):
        return self.globalHeaders

    """
        Allows cookies to be manually set or modified (initially set automatically by
        the getSession method)
    """
    def setCookies(self, cookies):
        self.session.cookies = cookies

    """
        Allows retrieval of cookies currently in use for all API calls
    """
    def getCookies(self):
        return self.session.cookies.get_dict()

    """
        May be used to retrieve student metadata (nid, unid, name, and so on)
    """
    def getStudentData(self):
        return self.studentData

    """
        Can be used to modify the internally held student metadata
    """
    def setStudentData(self, studentData):
        self.studentData = studentData

    """
        This begins a session, retrieving cookies that we'll use later. Don't call this if you've already called
        login, as it will overwrite the cookies.
    """
    def getSession(self):
        return requests.Session().get('https://'+self.edsbyHost+"/core/login/3472?xds=loginform&editable=true",headers=self.globalHeaders)

    """
        Retrieves a variety of authentication data from Edsby (server nonces, keys, etc)
        Which are then used by sendAuthenticationData to complete user authentication.
    """
    def getauthData(self, loginData):
        self.authData = requests.get('https://'+self.edsbyHost+"/core/node.json/3472?xds=fetchcryptdata&type=Plaintext-LeapLDAP",cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()["slices"][0]
        return {
            '_formkey': self.authData["_formkey"],
            'sauthdata': self.authData['data']["sauthdata"],
            'crypttype': 'LeapLDAP',
            'login-userid': loginData[0],
            'login-password': loginData[1],
            'login-host': self.edsbyHost,
            'remember': ''
        }

    """
        This is the final step in the authentication process, which completes user login and returns
        student metadata returned by Edsby
    """
    def sendAuthenticationData(self):
        studentData = requests.post('https://'+self.edsbyHost+'/core/login/3472?xds=loginform&editable=true',data=self.authData,cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()
        return {
          'unid': studentData['unid'],
          'compiled': studentData['compiled'],
          'nid': studentData['slices'][0]['nid'],
          'name': studentData['slices'][0]['data']['name'],
          'guid' : studentData['slices'][0]['data']['guid'],
          'formkey' : studentData['slices'][0]['data']['formkey']
        }

    """
        In a browser, this API call would bootstrap the web app. Here, however, we need only
        call it update our session state from Edsby's point of view. This has a lot of UI related metadata,
        though I haven't explored it in detail.
    """
    def getBootstrapData(self):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/?xds=bootstrap',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()

    """
        This is another required API call, which returns a wealth of metadata about the student as a whole,
        including classes. This is yet another thing I haven't explored in great detail.
    """
    def getBaseStudentData(self):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(self.studentData['unid'])+'?xds=BaseStudent',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()


    """
        Returns raw class data, which looks like:
            "r<course RID>": {
                "nodetype": 3,
                "Title": "<human readable name>",
                "reltype": 12,
                "value": someValue,
                "nodesubtype": 2,
                "course": {
                    "class": {
                        "text": {
                            "line2": {
                                "code": "<course code>",
                                "name": "<teacher name>"
                            },
                            "line1": "<human readable name>"
                        }
                    },
                    "basic": {
                        "text": {
                            "line1": "<course code>"
                        }
                    }
                },
                "nid": <course NID>,
                "rid": <course RID>
            }
    """
    def getRawClassData(self):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(self.studentData['nid'])+'?xds=ClassPicker&match=multi',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['class']

    """
        Returns a parsed list of all available classes, like so:
        "Class NID": {
            "human_name": "Class Name",
            "rid": Class RID,
        },
    """
    def getClassIDList(self):
        rawClassData = requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(self.studentData['nid'])+'?xds=ClassPicker&match=multi',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['class']
        classDict = {}
        for className in rawClassData:
            humanName = rawClassData[className]['course']['class']['text']['line1']
            NID = rawClassData[className]['nid']
            RID = rawClassData[className]['rid']
            classDict[NID] = dict()
            classDict[NID]['human_name'] = humanName
            classDict[NID]['rid'] = RID

        return classDict

    """
        Returns your current average for the given class NID (e.g. 97.4)
    """
    def getClassAverage(self, classNID):
        classData = requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'?xds=MyWork&student='+str(self.studentData['unid']),cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']
        if 'loaddata' in classData and 'average' in classData['loaddata']:
            return classData['loaddata']['average']
        else:
            return ''

    """
        Retrieves all available classes, then retrieves all available averages for those classes.
        Returns a dict of classes that looks like:
        "<Class NID>": {
            "human_name": "<Class Name>",
            "rid": <Class RID>,
            "average": <Current Average>
        },
    """
    def getAllClassAverages(self):
        classes = self.getClassIDList()
        for key in classes:
            classes[key]['average'] = self.getClassAverage(key)
        return classes

    """
        Returns an object containing all assignment metadata for a specified course, ordered by RID
        This includes the NID, RID, and weighting (points possible) of the assignments, but not your score.
    """
    def getClassAssignmentMetadata(self, classNID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'?xds=MyWork&student='+str(self.studentData['unid']),cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['loaddata']['gradebook']['terms']

    """
        Returns an object containing all assignment scores for a specified course, ordered by NID
        This includes the NID and points earned on the assignment, but nothing else.
    """
    def getClassAssignmentScores(self, classNID, classRID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'/'+str(classRID)+'/'+str(classNID)+'?xds=MyWorkAssessmentPane&unit=all&student='+str(self.studentData['unid'])+'&model=24605449',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()["slices"][0]["data"]['grades']

    """
        Returns an object containing all assignment scores for a specified course, ordered by NID
        This includes the NID and points earned on the assignment, but nothing else.
        This is different from getClassAssignmentScores in that it does not return all scores, and does so in a mixed
        format where score might be a letter grade, or it could be a JSON string that we have to parse into a string
        before reading. getClassAssignmentList can handle and process data returned from both of these endpoints
    """
    def getMixedFormatClassAssignmentScores(self, classNID, classRID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'/'+str(classRID)+'/'+str(classNID)+'?xds=MyWorkChart&student='+str(self.studentData['unid']),cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['loaddata']['grades']

    """
        Returns an array of NIDs for assignments that have been published (e.g. are visible) for a
        given course
    """
    def getClassPublishedAssignments(self, classNID, classRID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'/'+str(classRID)+'/'+str(classNID)+'?xds=MyWorkChart&student='+str(self.studentData['unid']),cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['bubbles']['publishedAssessments'].split(',')

    """
        Gathers all available, published assignment data from a specified class, and computes scores for each. Returns an object
        with all available data about the assignments (including a computed percentage), ordered by NID.
        "<NID>": {
            "sdate": "<guess: share date(?)>",
            "graded": <1 or 0, whether assignment was graded>,
            "weighting": <maximum possible points for assignment>,
            "rid": <assignment RID>,
            "state": "0", <- dunno what this is for
            "score": <number of points earned on an assignment>,
            "noavg": false, <whether or not the score was averaged?>
            "scheme": "gs_outof",  <maybe if assignments are points possible/max score?>
            "type": "0", <- dunno what this is for
            "columns": "{\"0\":80}",  <- dunno what this is for
            "fraction": "number/1", <- dunno what this is for. number looks like an NID(?)
            "summative": "1", <- dunno what this is for
            "nid": <assignment NID>,
            "cdate": "<guess: created date(?)>",
            "date": "<guess: date grade was entered(?)>",
            "esubmit": <0 or 1, guess: whether assignment was electronically submitted(?)>,
            "nodetype": 6, <- dunno what this is for
            "name": "<human name>",
            "thread": <same as NID>,
            "nodesubtype": 3, <- dunno what this is for
            "scorePercentage": <computed score percentage>,
            "published": "<1 or 0: true or false if assignment was published>"
        }
    """
    def getClassAssignmentList(self, classNID, classRID):
        self.getClassIDList() # Ensure the Edsby API is ready to return class data. This call is required before the next calls are made
        self.getClassFeed(classNID)
        scores = self.getClassAssignmentScores(classNID, classRID) # Fetch assignment scores
        metadata = self.getClassAssignmentMetadata(classNID) # Fetch assignment metadata
        assignmentData = {
            'assignments': dict(), # Assignments that have all applicable metadata present
            'no_scores_found': dict(), # Assignments that we haven't found scores for
            'no_weights_found': list() # Assignments we haven't found weights for
        }
        for nid in scores: # Populates assignmentData with NIDs and available assignment scores
            if 'cols' in scores[nid]:
                assignmentData['assignments'][nid] = {'score': scores[nid]['cols']['0']}

        # Copy all available assignment metadata to assignmentData dict
        for assg in metadata:
            assignmentNID = str(metadata[assg]['nid'])

            # Copy other keys from metadata obj to compiled assignment data obj
            for key in metadata['r'+str(metadata[assg]['rid'])]:
                if assignmentNID in assignmentData['assignments']: # If we've found metadata for an asssignment that we've also found scores for
                    assignmentData['assignments'][assignmentNID][key] = metadata[assg][key] # Copy metadata to that entry
                else:
                    assignmentData['no_scores_found'][assignmentNID] = dict() # Otherwise, place this metadata in the no_scores_found dict
                    for meta in metadata[assg]:
                        assignmentData['no_scores_found'][assignmentNID][meta] = metadata[assg][meta]

        # Copy weighting data, sort assignments without it, calculate percentage scores if possible
        for assg in assignmentData['assignments']:
            assignmentNID = str(assg)

            if 'weighting' in assignmentData['assignments'][assg]: # If weighting data is present in the metadata we retrieved
                # API sometimes returns a dict, other times returns a JSON string. Figure out which one it is and parse appropriately.
                if isinstance(assignmentData['assignments'][assg]['weighting'], dict): # If dict access weighting prop as a dict
                    assignmentData['assignments'][assignmentNID]['weighting'] = assignmentData['assignments'][assg]['weighting']['0']

                elif isinstance(assignmentData['assignments'][assg]['weighting'], basestring): # If string access weighting prop as a dict after running through a JSON parser
                    assignmentData['assignments'][assignmentNID]['weighting'] = json.loads(assignmentData['assignments'][assg]['weighting'])['0']
            else:
                assignmentData['no_weights_found'].push(assignmentNID) # No weighting data available for this entry, file it away

            # Calculate score percentage for assignment
            if 'weighting' in assignmentData['assignments'][assg]: # If valid weighting data is present
                if isinstance(assignmentData['assignments'][assg]['score'], basestring) is False: # If the score is NOT a letter grade (e.g. is numeric), calculate percentage score.
                    assignmentData['assignments'][assg]['scorePercentage'] = (float(assignmentData['assignments'][assg]['score'])/float(assignmentData['assignments'][assg]['weighting'])) * 100

        return assignmentData



    """
        Returns a dict with a basic summary of assignments and their grades for a
        given course (e.g "human name": "percentage")
    """
    def getHumanReadableAssignmentSummary(self, classNID, classRID):
        assignments = self.getClassAssignmentList(classNID, classRID)
        humanList = dict()
        for key in assignments['assignments']:
            if 'scorePercentage' in assignments['assignments'][key]:
                humanList[assignments['assignments'][key]['name']] = assignments['assignments'][key]['scorePercentage']
            else:
                humanList[assignments['assignments'][key]['name']] = assignments['assignments'][key]['score'].upper()
        return humanList

    """
        Retrieves raw, unformatted attendance records from the specified class. I haven't tried to
        parse these yet.
    """
    def getRawClassAttendenceRecords(self, classID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classID)+'?xds=MyWorkChart&student='+str(self.studentData['unid']),cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['data']['chartContainer']['chart']['attendanceRecords']['data']['right']['records']['incident']

    """
        Returns a list of all member students of a class
        Say hi to your classmates!
    """
    def getClassmates(self, classNID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'?xds=ClassStudentList',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['places']['item']

    """
        Retrieves the feed of all assignments and messages posted in the class
    """
    def getClassFeed(self, classNID):
        feed = requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'?xds=CourseFeed',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()
        return feed if 'item' in feed['slices'][0]['data'] else ''

    """
        Course calendar- returns calendar entries for the specified course
    """
    def getClassCalendar(self, classNID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'?xds=CalendarPanel_Class',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']

    """
        Course assignment outline, shows upcoming and historical assignments for the course
    """
    def getClassPlan(self, classNID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(classNID)+'?xds=Course&_context=1',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['col1']['outline']['plan']['tree']

    """
        Retrieves all current/pending notifications for the student
    """
    def getStudentNotifications(self):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(self.studentData['unid'])+'?xds=notifications',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']

    """
        Returns all available calendar data (due/overdue assignments, events, schedules)
    """
    def getCalendarData(self):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(self.studentData['unid'])+'?xds=Calendar',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()["slices"][0]["data"]["caldata"]

    """
        Get calendar entries for all upcoming due assignments
    """
    def getCalendarDueAssignments(self):
        return self.getCalendarData()['due']

    """
        Get calendar entries for currently overdue assignments
    """
    def getCalendarOverdueAssignments(self):
        return self.getCalendarData()['overdue']

    """
        Get all available calendar events
    """
    def getCalendarEvents(self):
        calendar = self.getCalendarData()
        for key in calendar['common'].keys:
            calendar['common'][str(key)] = calendar['events'][str(key)]
        return calendar['common']

    """
        Returns calendar entries containing school scheduling information
    """
    def getCalendarSchedules(self):
        return self.getCalendarData()['schedules']

    """
        Returns ALL direct Edsby messages from your inbox
    """
    def getDirectMessages(self):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(self.studentData['unid'])+'?xds=Messages&_context=1',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()["slices"][0]["data"]["body"]["left"]["items"]["item"]

    """
        Sends a direct message to a specified user
        the message dict passed to this method should be structured like so:
        {
            'nodetype': 4.0,
            'to': NID of user,
            'body': message text,
            'media-fill-include-integrations-integrationfiledata': file data(?),
            'media-fill-include-integrations-integrationfiles': more file data?
        }
    """
    def sendDirectMessage(self, message):
        payload = {
            '_formkey':self.studentData['formkey'],
            'nodetype': message['nodetype'],
            'to': message['to'],
            'body': message['text'],
            'media-fill-include-integrations-integrationfiledata': message['filedata'],
            'media-fill-include-integrations-integrationfiles': message['files']
        }
        return requests.post('https://'+self.edsbyHost+'/core/create/38089?xds=MessagesCompose&permaLinkKey=false&_processed=true',data=payload,cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()

    """
        Allows you to search for any higher level user (teacher, administrator)
        whose name matches or contains a particular string
    """
    def lookUpMessageRecipient(self, query):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(self.studentData['unid'])+'?xds=msgUserPicker&pattern='+query+'&noForm=true',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()["slices"][0]["data"]["item"]

    """
        Posts a message in the class feed. This takes a dict called message, which looks like this:
        {
            'text': '<the message text>',
            'url': '<an optional URL, shows up as a hyperlink in Edsby>',
            'pin': 8,
            'nodetype': 4,
            'node_subtype': 0,
            'filedata': '',
            'files': '',
        }
    """
    def postMessageInClassFeed(self, classNID, message):
        messageSubmission = {
            '_formkey': self.studentData['formkey'],
            'social-pin': message['pin'], # 8
            'social-shmart-nodetype': message['nodetype'], # 4
            'social-shmart-nodesubtype': message['node_subtype'], # 0
            'social-shmart-body': message['text'],
            'social-shmart-url': message['url'],
            'social-shmart-file-integrations-integrationfiledata': message['filedata'],
            'social-shmart-file-integrations-integrationfiles': message['files']
        }
        return requests.post('https://'+self.edsbyHost+'/core/create/'+str(classNID)+'?xds=CourseFeedMsg&xdsr=CourseFeed&rxdstype=ref&merge=merge',data=messageSubmission,cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slice']['slices'][0]['data']['item']

    """
        Posts a reply to a message in the class feed. This takes a dict called message, which looks like this:
        {
            'text': '<the message text>',
            'url': '<an optional URL, shows up as a hyperlink in Edsby>',
            'pin': 8,
            'nodetype': 4,
            'node_subtype': 23,
            'filedata': '',
            'files': '',
            'parent_nid': <parent feed item NID>,
            'parent_rid': <parent feed item RID>
        }
    """
    def postReplyInClassFeed(self, classNID, message):
        messageSubmission = {
            '_formkey': self.studentData['formkey'],
            'body-pin': message['pin'], # 8
            'body-shmart-nodetype': message['nodetype'], # 4
            'body-shmart-nodesubtype': message['node_subtype'], # 23
            'body-shmart-body': message['text'],
            'body-shmart-url': message['url'],
            'body-shmart-file-integrations-integrationfiledata': message['filedata'],
            'body-shmart-file-integrations-integrationfiles': message['files'],
            'replyTo': '',
            'thread': message['parent_nid']
        }
        return requests.post('https://'+self.edsbyHost+'/core/create/'+str(classNID)+'/'+str(message['parent_rid'])+'/'+str(classNID)+'?xds=feedreply&xdsr=CourseFeed&__delegated=CourseFeed',data=messageSubmission,cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slice']['slices'][0]['data']['item']

    """
        Posts a message with an accompanying file in the class feed. This takes a dict called message,
        which looks like this:
        {
            'text': '<the message text>',
            'url': '<an optional URL, shows up as a hyperlink in Edsby>',
            'pin': 8,
            'nodetype': 4,
            'node_subtype': 0,
            'filedata': '',
            'files': '',
        }
            TODO - Edsby complains of an invalid key when attempting to upload. Suspect form data formatting in POST.
    """
    def postFileInClassFeed(self, classNID, message, fileName, filePath):
        messageSubmission = {
            '_formkey': self.studentData['formkey'],
            'social-pin': message['pin'], # 10
            'social-shmart-nodetype': message['nodetype'], # 4
            'social-shmart-nodesubtype': message['node_subtype'], # 0
            'social-shmart-body': message['text'],
            'social-shmart-url': message['url'],
            'social-shmart-file-integrations-integrationfiledata': message['filedata'],
            'social-shmart-file-integrations-integrationfiles': message['files']
        }
        postMetadata = requests.post('https://'+self.edsbyHost+'/core/create/'+str(classNID)+'?xds=CourseFeedMsg&xdsr=CourseFeed&rxdstype=ref&merge=merge',data=messageSubmission,cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slice']['slices'][0]['data']['item']
        parentRID = next(iter(postMetadata))
        cookies = self.session.cookies.get_dict()

        uploadData = {
            'name': fileName,
            'nodetype': '5.0',
            'pin': '2',
            '_formkey': self.studentData['formkey'],
        }

        for key in cookies:
            uploadData[key] = cookies[key]

        uploadData['files'] = (fileName, open(filePath, 'rb'))

        return requests.post('https://'+self.edsbyHost+'/core/create/'+str(classNID)+'/'+str(postMetadata[parentRID]['rid'])+'/'+str(postMetadata[parentRID]['nid'])+'?xds=MultiFileUploader',files=uploadData,cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()

    """
        Likes an item in the feed for a class
    """
    def likeItemInFeed(self, classNID, feedItemNID, feedItemRID):
        likeData = {
            'likes': 1,
            '_formkey': self.studentData['formkey']
        }
        return requests.post('https://'+self.edsbyHost+'/core/node/'+str(classNID)+'/'+str(feedItemRID)+'/'+str(feedItemNID)+'?xds=doLike',data=likeData,cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()

    """
        Retrieves metadata about files attached to feed items, should they be present
        If Edsby complains, call getClassFeed before using this function
    """
    def getAttachmentMetadata(self, feedItemNID, attachmentNID):
        return requests.get('https://'+self.edsbyHost+'/core/node.json/'+str(feedItemNID)+'/'+str(attachmentNID)+'?xds=AlbumFileView',cookies=self.session.cookies.get_dict(),headers=self.globalHeaders).json()['slices'][0]['data']['item']

    """
        Generates the URL to download a particular file from Edsby, as such URLs are long and verbose.
        Helper function to downloadAttachment. Useful if you want to handle file downloading in another
        application (If you do, make sure you also take the session cookies with you).
    """
    def getAttachmentDownloadURL(self, classNID, feedItemNID, feedItemRID, attachmentNID):
        return 'https://'+self.edsbyHost+'/core/nodedl/classNID/'+str(feedItemRID)+'/'+str(feedItemNID)+'/'+str(feedItemRID)+'/'+str(attachmentNID)+'?field=file&attach=1&xds=fileThumbnail'

    """
        Downloads an attachment from Edsby to the specified local path.
        You could, for example, check a courses' feed at a regular interval, and then download
        any new files attached to new posts.
    """
    def downloadAttachment(self, classNID, feedItemNID, feedItemRID, attachmentNID, filePath):
        self.getClassFeed(classNID)  # Must call these before attempting to download, otherwise API denies access
        self.getAttachmentMetadata(feedItemNID, feedItemRID) # Another prerequisite call
        attachment = requests.get(self.getAttachmentDownloadURL(classNID, feedItemNID, feedItemRID, attachmentNID),cookies=self.session.cookies.get_dict(),headers=self.globalHeaders,stream=True)
        with open(filePath, 'wb') as localFile:
            for attachmentPart in attachment.iter_content(chunk_size=1024):
                if attachmentPart:
                    localFile.write(attachmentPart)
        return filePath
