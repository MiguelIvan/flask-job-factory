import json
import requests
from random import randint
import random
import uuid
import hashlib

#unique ID generator
randomizer = hashlib.sha1(str(uuid.uuid1()) + \
                str(random.random()*1000000000) + '-' + \
                str(uuid.uuid4())).hexdigest()

def fill_queue():
    while True:
        payload = {'queue':'files', 'value':json.dumps({'id': randint(0, 9999),
            'body':'fkdjdffdduckfdjk'})}
        r = requests.post('http://localhost:8888', data=payload)

fill_queue()
