#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading
import time
import datetime
import beanstalkc
import simplejson
import redis
import memcache
import requests
from hashlib import sha1

DUPES_KEY = 'images::duplicates'
DUPES_DAILY_SOLVED_KEY = 'images::duplicates::counter::daily'
DUPES_WEEKLY_SOLVED_KEY = 'images::duplicates::counter::weekly'
OCR_DAILY_SOLVED_KEY = 'images::ocr::counter::daily'
OCR_WEEKLY_SOLVED_KEY = 'images::ocr::counter::weekly'
IMAGES_KEY = 'images::storage'

R_SERVER = redis.Redis('localhost')
M_SERVER = memcache.Client(['localhost:11211'], debug=0)


def solve_and_publish(id, body, category):
    #verify the sha1sum against a duplicate image from a redis key
    text = R_SERVER.get('%s::%s'%(DUPES_KEY,sha1(body).hexdigest()))
    if not text:
        text = '%s time and %s'%(time.time(),body) # <------ Ocr work here!
        '''
        Counter stuff bellow
        '''
        if not (M_SERVER.get(OCR_DAILY_SOLVED_KEY)):
            M_SERVER.set(OCR_DAILY_SOLVED_KEY, 0, 3600*24)
        if not (M_SERVER.get(OCR_WEEKLY_SOLVED_KEY)):
            M_SERVER.set(OCR_WEEKLY_SOLVED_KEY, 0, 3600*24*7)
        M_SERVER.incr(OCR_DAILY_SOLVED_KEY)
        M_SERVER.incr(OCR_WEEKLY_SOLVED_KEY)
        #
        R_SERVER.set('%s::%s'%(DUPES_KEY,sha1(body).hexdigest()), text)
    else:
        if not (M_SERVER.get(DUPES_DAILY_SOLVED_KEY)):
            M_SERVER.set(DUPES_DAILY_SOLVED_KEY, 0, 3600*24)
        if not (M_SERVER.get(DUPES_WEEKLY_SOLVED_KEY)):
            M_SERVER.set(DUPES_WEEKLY_SOLVED_KEY, 0, 3600*24*7)
        M_SERVER.incr(DUPES_DAILY_SOLVED_KEY)
        M_SERVER.incr(DUPES_WEEKLY_SOLVED_KEY)

    R_SERVER.hset('%s::%s'%(IMAGES_KEY, id), 'date', datetime.datetime.now())
    R_SERVER.hset('%s::%s'%(IMAGES_KEY, id), 'text', text)

def poll():
    while True:
        try:
            element = requests.get('http://localhost:8888/q/images')
        except Exception, e:
            break
        else:
            if not element.text:
                time.sleep(5)
            else:
                try:
                    element = simplejson.loads(element.text)
                    composite_image = simplejson.loads(element['value'])
                    id = composite_image['id']
                    body = composite_image['body']
                    category = composite_image['icat']
                    threading.Thread(target=solve_and_publish, args=(id, body,\
                        category)).start()
                except Exception, e:
                    print e
                    pass

if '__main__' == __name__:
    threads = []
    for n in range(30):
        t = threading.Thread(target=poll)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
