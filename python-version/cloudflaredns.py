# coding:utf-8

import base64
import urllib
import hmac
import datetime
import random
import string
import json
import sys
import os

from urllib.parse import quote
from urllib.parse import urlencode
from urllib import request

class CloudflareDns:
    def __init__(self, access_key_id, domain_name):
        self.access_key_id = access_key_id
        self.domain_name = domain_name

    @staticmethod
    def getDomain(domain):
        domain_parts = domain.split('.')

        if len(domain_parts) > 2:
            dirpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            domainfile = dirpath + "/domain.ini"
            domainarr = []
            with open(domainfile) as f:
                for line in f:
                    val = line.strip()
                    domainarr.append(val)

            rootdomain = '.'.join(domain_parts[-(2 if domain_parts[-1] in
                                                 domainarr else 3):])
            selfdomain = domain.split(rootdomain)[0]
            return (selfdomain[0:len(selfdomain)-1], rootdomain)
        return ("", domain)

    @staticmethod
    def access_url(url):
        headers = {'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'}
        req = request.Request(url=url, headers=headers)
        proxy = request.ProxyHandler({'http': '127.0.0.1:7890'})
        opener = request.build_opener(proxy, request.HTTPHandler)
        request.install_opener(opener)
        with request.urlopen(req) as f:
            result = f.read().decode('utf-8')
            return json.loads(result)

    def visit_url(self, url, action_param):
        common_param = {
            'type': 'json',
            'version': 1,
            'key': self.access_key_id,
            'domain': self.domain_name,
        }
        url_param = dict(common_param, **action_param)

        url = url + '?' + urlencode(url_param)
        #print(url)
        return CloudflareDns.access_url(url)

    # 显示所有
    def describe_domain_records(self):
        headers = {
            'Authorization': 'Bearer UfyP9-_1WLPs3HoNqHQpkneYlgyYytqQorI9HQdq',
            'Content-Type': 'application/json', 
        }
        req = request.Request(url='https://api.cloudflare.com/client/v4/zones/ce8de033ef08f2d7b0a9ff90df8105f7/dns_records', 
                              headers=headers,
                              method='GET'
                              )
        #proxy = request.ProxyHandler({'http': '127.0.0.1:7890'})
        #opener = request.build_opener(proxy, request.HTTPHandler)
        #request.install_opener(opener)
        try:
            with request.urlopen(req) as f:
                result = f.read().decode('utf-8')
                return json.loads(result)
        except urllib.error.HTTPError as e:
            print('HTTP Error:', e.code, e.reason)
        except urllib.error.URLError as e:
            print('URL Error:', e.reason)

    # 增加解析
    def add_domain_record(self, type, rr, value):
        headers = {
            'Authorization': 'Bearer UfyP9-_1WLPs3HoNqHQpkneYlgyYytqQorI9HQdq',
            'Content-Type': 'application/json', 
        }
        data = {
            "comment": "",
            "name": rr,
            "proxied": False,
            "settings": {},
            "tags": [],
            "ttl": 60,
            "content": value,
            "type": type
        }
        json_data = json.dumps(data).encode('utf-8')
        req = request.Request(url='https://api.cloudflare.com/client/v4/zones/ce8de033ef08f2d7b0a9ff90df8105f7/dns_records', 
                              headers=headers,
                              data=json_data,
                              method='POST'
                              )
        #proxy = request.ProxyHandler({'http': '127.0.0.1:7890'})
        #opener = request.build_opener(proxy, request.HTTPHandler)
        #request.install_opener(opener)
        try:
            with request.urlopen(req) as f:
                result = f.read().decode('utf-8')
                return json.loads(result)
        except urllib.error.HTTPError as e:
            print('HTTP Error:', e.code, e.reason)
        except urllib.error.URLError as e:
            print('URL Error:', e.reason)

    # 删除解析
    def delete_domain_record(self, id):
        headers = {
            'Authorization': 'Bearer UfyP9-_1WLPs3HoNqHQpkneYlgyYytqQorI9HQdq',
            'Content-Type': 'application/json', 
        }
        req = request.Request(url='https://api.cloudflare.com/client/v4/zones/ce8de033ef08f2d7b0a9ff90df8105f7/dns_records/'+id, 
                              headers=headers,
                              method='DELETE'
                              )
        #proxy = request.ProxyHandler({'http': '127.0.0.1:7890'})
        #opener = request.build_opener(proxy, request.HTTPHandler)
        #request.install_opener(opener)
        try:
            with request.urlopen(req) as f:
                result = f.read().decode('utf-8')
                return json.loads(result)
        except urllib.error.HTTPError as e:
            print('HTTP Error:', e.code, e.reason)
        except urllib.error.URLError as e:
            print('URL Error:', e.reason)


if __name__ == '__main__':
	# 第一个参数是 action，代表 (add/clean)
	# 第二个参数是域名
	# 第三个参数是主机名（第三个参数+第二个参数组合起来就是要添加的 TXT 记录）
	# 第四个参数是 TXT 记录值
	# 第五个参数是 APPKEY
    #sys.exit(0)

    print("域名 API 调用开始")
    print("-".join(sys.argv))
    file_name, cmd, certbot_domain, acme_challenge, certbot_validation, ACCESS_KEY_ID = sys.argv

    certbot_domain = CloudflareDns.getDomain(certbot_domain)
    print (certbot_domain)
    if certbot_domain[0] == "":
            selfdomain = acme_challenge
    else:
            selfdomain = acme_challenge + "." + certbot_domain[0]

    domain = CloudflareDns(ACCESS_KEY_ID, certbot_domain[1])

    if cmd == "add":
        result = (domain.add_domain_record(
            "TXT", selfdomain, certbot_validation))
        print(result)
        if result is not None and 'success' in result:
            if result['success'] != True:
                print("cloudflare dns 域名增加失败-" +
                    str(result['errors']) + ":" + str(result['messages']))
                sys.exit(0)
    elif cmd == "clean":
        result = domain.describe_domain_records()
        print(result)
        if result is not None and 'success' in result:
            if result['success'] != True:
                print("cloudflare dns 获取域名失败-" +
                    str(result['errors']) + ":" + str(result['messages']))
                sys.exit(0)
        if "result" not in result:
            print('records is empty')
            sys.exit(0)
        record_list = result["result"]
        print(record_list)
        if record_list:
            for item in record_list:
                if (item['name'] == selfdomain + '.' + certbot_domain[1]):
                    domain.delete_domain_record(item['id'])

print("域名 API 调用结束")
