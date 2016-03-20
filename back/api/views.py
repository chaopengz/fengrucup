# coding:utf-8
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
import MySQLdb
import json
from django.http import JsonResponse

#
db = MySQLdb.connect("buaa.czioyaateeku.ap-northeast-1.rds.amazonaws.com", "chaopengz", "a7641368", "xzbh",
                     charset="utf8")
# db = MySQLdb.connect("localhost", "root", "a7641368", "xzbh",
#                      charset="utf8")
cursor = db.cursor()


def index(request):
    return render(request, 'index.html')


def location(request):
    return render(request, 'location.html')


def getWebData(request):
    x = []
    y = []
    loc = request.GET.get('location')
    floor = request.GET.get('floor')
    print type(loc), type(floor), type("层"), type(' - ')
    t = loc + " - " + floor + "层"
    # t = "test"
    sql = r"select * from t_20160220 where location = '" + loc + "' and room like '" + floor + "%' "
    cursor.execute(sql)
    lines = cursor.fetchall()
    for line in lines:
        percent = line[2] * 100 / line[4]
        y.append(percent)
        x.append(line[1])
    print x, y, t
    vdict = {'x': x, 'y': y, 't': t}
    return HttpResponse(json.dumps(vdict), content_type='application/json')


def feedback(request):
    print request.method
    content = request.POST['content']
    contact = request.POST['contact']
    print content, contact
    return HttpResponse("successful")


def getcourseinfo(request):
    location = request.GET['location']
    sql = "select * from course_information_crawler where class_room like  '" + location + "%'" + ";"
    cursor.execute(sql)
    lines = cursor.fetchall()
    list = []
    for line in lines:
        d = dict(room=line[1], date=line[2], course=line[3])
        list.append(d)

    return HttpResponse(json.dumps(list, ensure_ascii=False, indent=2))


def query(request):
    location = request.GET['location']
    sql = "select * from t_20160220 where location = '" + location + "'" + ";"
    cursor.execute(sql)
    lines = cursor.fetchall()
    list = []
    all_total = 0
    per_total = 0
    for line in lines:
        per_total += line[3]
        all_total += line[4]
        percent = float(line[3]) / line[4];
        percent = round(percent, 2)
        d = dict(location=line[0], room=str(line[1]), macnum=str(line[2]), idnum=str(line[3]), maxnum=str(line[4]),
                 time=str(line[5]), percent=str(percent))
        list.append(d)
    # print per_total, all_total
    usage = float(per_total) / all_total
    usage = round(usage, 4)
    # print usage
    u_dict = dict(density=usage)
    list.append(u_dict)
    return HttpResponse(json.dumps(list, ensure_ascii=False, indent=2))


def queryall(request):
    sql = "select distinct location from t_20160220"
    cursor.execute(sql)
    locs = cursor.fetchall()
    ret = []
    for loc in locs:
        sql = "select * from t_20160220 where location = '" + loc[0] + "'" + ";"
        cursor.execute(sql)
        lines = cursor.fetchall()
        all_total = 0
        per_total = 0
        for line in lines:
            per_total += line[3]
            all_total += line[4]
        usage = float(per_total) / all_total
        usage = round(usage, 4)
        u_dict = dict(density=usage, location=loc[0])
        ret.append(u_dict)
    return HttpResponse(json.dumps(ret, ensure_ascii=False, indent=2))
