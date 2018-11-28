import requests
import json
import time
from lxml import etree
import redis
import pymongo
import re
import math
import zmail


class WeChatPublicPush:
    def __init__(self,keyword,to_addrlist):
        self.keyword = keyword
        self.pagename = 'wechatPublic{}page'.format(self.keyword)
        self.tmp_info = 'wechatPublic{}tmpInfo'.format(self.keyword)
        self.old_id = 'wechatPublic{}oldid'.format(self.keyword)
        self.rdb = redis.Redis(host='192.168.1.60',password='***',db=0)
        con = pymongo.MongoClient('192.168.1.60',27017)
        wechat_puhlic = con.wechat_public
        self.mdb = wechat_puhlic.mdb
        self.base_url = 'https://weixin.sogou.com/weixin'
        self.headers ={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, br',
                        'Accept-Language': 'zh-CN,zh;q=0.9',
                        'Connection': 'keep-alive',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'}
        self.to_addrlist = to_addrlist

    def sender(self,titel,content):
        server = zmail.server('1***3@qq.com','***')
        mail = {
            'from':'微公众号推送',
            'subject': titel,
            'content_text':content,

        }
        server.send_mail(self.to_addrlist,mail)


    # def wechat_reop(self,url,payload):
    #     try:
    #         reop = requests.get(url=url,headers=self.headers,params=payload)
    #     except:
    #         return False
    #     else:
    #         return reop.content.decode('utf-8')


    def get_pagenum(self):
        print('getpage')
        self.headers['Host'] = 'weixin.sogou.com'
        while True:
            if not self.rdb.exists(self.pagename):
                payload = {'type': '2',
                           'query': self.keyword,
                           'ie': 'utf8',
                           's_from': 'input',
                           '_sug_': 'n',
                           '_sug_type_': '1',
                           'w': '01015002',
                           'oq': '',
                           'ri': '1',
                           'sourceid': 'sugg',
                           'sut': '0',
                           'sst0': str(time.time()).replace('.', '')[:13],
                           'lkt': '0,0,0',
                           'p': '40040108'}
                try:
                    reop = requests.get(url=self.base_url,headers = self.headers, params=payload)
                    # print(reop.url)
                    doc = reop.content.decode('utf-8')
                    print(doc)
                    pagenum = int((re.findall(r'找到约(.+)条结果',doc)[0]).replace(',',''))
                except Exception as a:
                    print('请求页码发生{}重新请求'.format(a))
                else:
                    if pagenum > 100:
                        pagenum=100
                    pagenum = math.ceil(pagenum/10)
                    print('共{}页'.format(pagenum))
                    for i in  range(1,pagenum+1):
                        self.rdb.lpush(self.pagename, json.dumps(i))
                    print('页码写入redis数据库完毕等待爬取')
                    print('页码爬取完毕等待一小时再爬取')
            else:
                print('已有页码进行断点爬取，爬取完成等待一个小时继续爬')
            time.sleep(3600)


    def get_all_page(self):
        print('getallinfo')
        self.headers['Host'] = 'weixin.sogou.com'
        session = requests.session()
        while True:
            pagenum = self.rdb.rpop(self.pagename)
            # print(pagenum)
            if pagenum:
                pagenum=json.loads(pagenum)
                if pagenum == 1:
                    # print(pagenum)
                    payload = {'type': '2',
                               'query': self.keyword,
                               'ie': 'utf8',
                               's_from': 'input',
                               '_sug_': 'n',
                               '_sug_type_': '1',
                               'w': '01015002',
                               'oq': '',
                               'ri': '1',
                               'sourceid': 'sugg',
                               'sut': '0',
                               'sst0': str(time.time()).replace('.', '')[:13],
                               'lkt': '0,0,0',
                               'p': '40040108'}
                else:
                    print(pagenum)
                    payload = {'type': '2',
                            'dp':'1',
                            'dr':'1',
                            'page':pagenum,
                            'query': self.keyword,
                            'ie': 'utf8',
                            's_from': 'input',
                            '_sug_': 'n',
                            '_sug_type_': '1',
                            'w': '01015002',
                            'oq':'',
                            'ri': '1',
                            'sut': '0',
                            'sst0': str(time.time()).replace('.','')[:13],
                            'lkt': '0,0,0',
                            'p': '40040108'}
                    self.headers['Referer'] = reop.url
                try:
                    reop = session.get(url=self.base_url,headers=self.headers,params=payload)
                    reop_text = reop.content.decode('utf-8')
                    html = etree.HTML(reop_text)
                    all_data = html.xpath('//ul[@class="news-list"]//li')
                    all_news_id = html.xpath('//div[@class="s-p"]/@t')
                    news_index = 0
                    for i in all_data:
                        each_info = dict()
                        each_info['news_id'] = all_news_id[news_index]
                        news_index+=1
                        each_info['news_title'] = i.xpath('.//h3//a[@data-share]/text()')[0]
                        each_info['news_url'] = i.xpath('.//h3//a//@data-share')[0]
                        if self.rdb.sadd(self.old_id,json.dumps(each_info['news_id'])):
                            self.rdb.lpush(self.tmp_info,json.dumps(each_info))
                except Exception as a:
                    print('第{}页发生{}'.format(pagenum,a))
                    self.rdb.lpush(self.pagename,pagenum)
                    print('失败页码回写redis')
                time.sleep(2)
            time.sleep(0.1)


    def get_detail(self):
        print('detail')
        while True:
            each_info = self.rdb.lpop(self.tmp_info)
            if each_info:
                info = json.loads(each_info)
                url = info['news_url']
                doc = requests.get(url=url,headers = self.headers).content.decode('utf-8')
                # print(doc)
                if doc:
                    html = etree.HTML(doc)
                    page_content_list = html.xpath('//div[@id="page-content"]//*//text()') #获取页面文字list
                    s = str()
                    for i in page_content_list:
                        s = s+i
                    for i in range(10):
                        s = s.replace('\n\n','\n').replace('                                ','')
                    page_content = s
                    print(page_content)
                    info['detail'] = page_content
                    info['time'] = time.time()
                    news_id = info['news_id']
                    self.mdb.insert(info)
                    print(type(news_id))
                    print('{}写入mongodb'.format(news_id))
                    titel = info['news_title']+time.strftime('%Y-%m-%d',time.localtime(int(news_id)))
                    content = page_content
                    self.sender(titel=titel, content=content)
                    print('邮件发送成功')
                else:
                    self.rdb.rpush(self.tmp_info,each_info)
                    print('{}页面访问失败tmp_info返回redis')
            time.sleep(0.1)


