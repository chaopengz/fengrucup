# coding:utf-8
import httplib, urllib, json

subkey = '18b4d8841991409db20951209fb275da'


def createPerson(name):
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subkey,
    }
    params = urllib.urlencode({
    })
    body = '''
          {"name":"''' + name + '''"}
          '''
    print body
    try:
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        conn.request("POST", "/face/v1.0/persongroups/group1/persons?%s" % params, body,
                     headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    s = json.loads(data)
    if s:
        return s["personId"]


def getFaceId(url):
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subkey,
    }

    params = urllib.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false',
    })
    body = '{"url":" ' + url + '"  }'
    try:
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    s = json.loads(data)
    if s:
        return s[0]["faceId"]
    else:
        return "none"


def identify(faceid):
    if faceid == 'none':
        return "none"
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subkey,
    }

    params = urllib.urlencode({
    })
    body = r'''
        {
            "personGroupId":"group1",
            "faceIds":[
                "''' + faceid + '''",
            ],
            "maxNumOfCandidatesReturned":1
        }
    '''
    try:
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        conn.request("POST", "/face/v1.0/identify?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    s = json.loads(data)
    if s[0]["candidates"]:
        return s[0]["candidates"][0]["personId"]
    else:
        return "none"


def getPersonName(personid):
    if personid == 'none':
        return '陌生人'
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': subkey,
    }

    params = urllib.urlencode({
    })
    body = '''

         '''
    try:
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        conn.request("GET", "/face/v1.0/persongroups/group1/persons/" + personid + "?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))
    s = json.loads(data)
    return s["name"]


def addPersonFace(personid, url):
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subkey,
    }

    params = urllib.urlencode({
        # Request parameters
    })
    body = '''
            {
                "url":"''' + url + '''"
            }
        '''
    try:
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        conn.request("POST", "/face/v1.0/persongroups/group1/persons/" + personid + "/persistedFaces?%s" % params, body,
                     headers)
        response = conn.getresponse()
        data = response.read()
        print(data)
        conn.close()
        return "successful"
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


def getWho(url):
    faceId = getFaceId(url)
    personId = identify(faceId)
    name = getPersonName(personId)
    print name
    return name


def train():
    headers = {
        # Request headers
        'Ocp-Apim-Subscription-Key': subkey,
    }

    params = urllib.urlencode({
    })

    try:
        conn = httplib.HTTPSConnection('api.projectoxford.ai')
        conn.request("POST", "/face/v1.0/persongroups/group1/train?%s" % params, "{body}", headers)
        response = conn.getresponse()
        data = response.read()
        print response.status
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))


def createPeople(name, url):
    pid = createPerson(name)
    if addPersonFace(pid, url) == "successful":
        train()
        return "createSuccess"

# createPerson("思哲")
# getFaceId('http://7xrc7y.com1.z0.glb.clouddn.com/image2016-03-08%2C07%3A52%3A32_small.jpeg')
# identify("19794ca9-167b-4c7e-9ad1-418b957e5599")
# getPersonName("6468a4d8-5767-42b3-98e3-1382e5e0241f")
# addPersonFace("61a5143b-706e-49f5-909b-b56f618b9b04", "http://7xrc7y.com1.z0.glb.clouddn.com/sizhe_small.jpeg")
# getWho("http://www.managerreads.com/wp-content/uploads/2015/08/2012221134143451.jpg")
# createPeople("扎克伯格","http://a4.att.hudong.com/11/91/19300323245025134665910422704.jpg")
# createPeople("殷春草", "http://a4.att.hudong.com/11/91/19300323245025134665910422704.jpg")
# createPeople("兵长","http://xlock.chaopengz.com/2016-05-07,14:56:50.jpg")
# train()
