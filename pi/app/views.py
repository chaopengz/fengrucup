from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
from sevencow import Cow
from PIL import Image
import os
import led

baseurl = 'http://xlock.chaopengz.com/'


def index(request):
    return HttpResponse("Hello World!")


def takephoto():
    os.system('raspistill -o image.jpg -t 200')


def upload(filename):
    ACCESS_KEY = 'AHXhPwOlX2Qjn1tAa8e463dJV_o7a2yFsq5SwlOL'
    SECRET_KEY = 'ld18GpYNWJnIeOSq_WJsUbu4pIfepyRVf7huOAzk'
    BUCKET = 'smartlock'
    cow = Cow(ACCESS_KEY, SECRET_KEY)
    b = cow.get_bucket(BUCKET)
    compress(filename)
    filename = filename[0:-4] + '_small.jpeg'
    print filename
    b.put(filename, keep_name=True)
    print 'successful'


def compress(filename):
    img = Image.open(filename)
    w, h = img.size
    print w, h
    img.resize((w / 2, h / 2)).save(filename[0:-4] + '_small.jpeg')


def query(request):
    location = request.GET['location']
    if location == 'yes':
        # takephoto()
        compress('image.jpg')
        upload('image.jpeg')
        return HttpResponse('successful')
    else:
        return HttpResponse('error')


def open(request):
    if request.method == 'POST':
        instruction = request.POST['instruction']
        if instruction == 'yes':
            led.opendoor()
            return HttpResponse("open door!")
        else:
            return HttpResponse("not open!")
    else:
        return HttpResponse("no post data!")
