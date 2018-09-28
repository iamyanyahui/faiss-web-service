# -*- coding: utf-8 -*-
# @Time    : 2018/9/17 下午7:28
# @Author  : yahui yan
import datetime
import json
import os
import requests
import time

if __name__ == '__main__':
    # os.system('curl -X POST 0.0.0.0:5000/faiss/search -d \'{"ids": [3,4,7,10], "k": 300}\'')
    f = open('time.log', 'a')
    for i in xrange(1000000):
        start = datetime.datetime.now()
        data = {'ids': [1], 'k': 300}
        url = 'http://0.0.0.0:5000/faiss/search'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url=url, headers=headers, data=json.dumps(data))
        print response.content
        end = datetime.datetime.now()
        f.write(str((end - start).microseconds / 1000))
        f.write('\n')
        # time.sleep(1)
    f.close()
