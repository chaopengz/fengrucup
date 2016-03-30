# coding:utf-8
from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
import MySQLdb
import json
from django.http import JsonResponse


def HandleSql(sql, ret):
    db = MySQLdb.connect("buaa.czioyaateeku.ap-northeast-1.rds.amazonaws.com", "chaopengz", "a7641368", "xzbh",
                         charset="utf8")
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
        if ret == 'yes':
            lines = cursor.fetchall()
            return lines
    except:
        db.rollback()
    finally:
        db.close()


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
    lines = HandleSql(sql, 'yes')
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
    lines = HandleSql(sql, 'yes')
    list = []
    for line in lines:
        d = dict(room=line[1], date=line[2], course=line[3])
        list.append(d)

    return HttpResponse(json.dumps(list, ensure_ascii=False, indent=2))


def query(request):
    location = request.GET['location']
    sql = "select * from t_20160220 where location = '" + location + "'" + ";"
    lines = HandleSql(sql, 'yes')
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

    locs = HandleSql(sql, 'yes')

    ret = []
    for loc in locs:
        sql = "select * from t_20160220 where location = '" + loc[0] + "'" + ";"
        lines = HandleSql(sql, 'yes')
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


def getRecommend(username, password):
    sql = '''
        select distinct * from xzbh.librarybook
        where id in
        (
          select bookid from xzbh.libraryrecommend
	      where userid =
		      (SELECT id FROM xzbh.libraryuser where username = '%s'and passwd = '%s'
        ));
        ''' % (username, password)
    list = []
    lines = HandleSql(sql, 'yes')
    length = len(lines)
    if length == 0:
        sql = '''
            select name,author,code, count(*) as count
            from xzbh.librarybook
            group by name
            order by count desc
              limit 5
            '''
        items = HandleSql(sql, "yes")
        for item in items:
            code = item[2]
            name = item[0]
            author = item[1]
            d = dict(code=code, name=name, author=author)
            list.append(d)
    else:
        for line in lines:
            code = line[1]
            name = line[2]
            author = line[3]
            d = dict(code=code, name=name, author=author)
            list.append(d)
    # list.append(length)
    return list


def recommend(request):
    print request.method
    username = request.POST['username']
    password = request.POST['password']
    realname = request.POST['name']
    list = getRecommend(username, password)
    return HttpResponse(json.dumps(list, ensure_ascii=False, indent=2))
