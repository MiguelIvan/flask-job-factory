import simplejson, hashlib, random, uuid, redis, requests
import base64
from flask import Flask, request, redirect, url_for

api = Flask(__name__)
api.debug = True
R_SERVER = redis.Redis('localhost')
IMAGES_KEY = 'images::storage'

def randomizer():
    #unique ID generator
    return hashlib.sha1(str(uuid.uuid1()) + \
            str(random.random()*1000000000) + '-' + \
            str(uuid.uuid4())).hexdigest()

@api.route('/upload', methods=['POST'])
def upload_file():
    image_field = request.files.get('image')
    image_category = request.form.get('category', False)
    try:
        assert image_field
        assert image_category
        imgstring = base64.b64encode(image_field.read())
        uiid = randomizer()
        '''
        # tought to avoid uiid collitions but potentially
        # unnecesary

        while R_SERVER.hget('%s::%s'%(IMAGES_KEY, uiid), 'text'):
            uiid = randomizer()
        '''
        payload = {'queue':'images', 'value':simplejson.dumps({'id': uiid,
            'body':imgstring, 'icat': image_category})}
        r = requests.post('http://localhost:8888', data=payload)

    except (AssertionError):
        return 'missig file or category', 403
    except ValueError, e:
        print e
        return  str(e), 403
    else:
        return simplejson.dumps({'notice':'uploaded', 'url': '/image/%s'%uiid})

@api.route('/image/<uiid>/', methods=['GET', 'POST'])
def poll_file(uiid):
    image = R_SERVER.hget('%s::%s'%(IMAGES_KEY, uiid), 'text')
    if not image:
        return simplejson.dumps({'notice':'uiid not ready'})
    else:
        return simplejson.dumps({'text':file})

if __name__=='__main__':
    api.run()
