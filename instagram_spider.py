# coding=utf-8
'''
Created on 2017年12月23日

@author: kist
'''

from selenium import webdriver
from bs4 import BeautifulSoup
import re, json
import os
import Queue
import requests
from selenium.common.exceptions import TimeoutException, WebDriverException
import threading, time
from upload_qiniu import upload_qiniu
import MySQLdb
from time import sleep


class Instagram_Spider():
    def __init__(self, url, name):
        # instagram策略，定期更换div的id
        self.jpg_div = '_4rbun'
        self.jpg_vote = '_nzn1h'
        self.mp4_div = '_qzesf'
        self.mp4_vote = '_m5zti'
        self.date_div = '_p29ma _6g6t5'
        #
        self.url = url
        self.name = name
        self.browser = webdriver.PhantomJS()
        self.domain = 'https://www.instagram.com'
        # 三层队列
        self.mainurl_queue = Queue.Queue()
        self.imgurl_queue = Queue.Queue()
        # self.img_queue = Queue.Queue()
        #
        self.up = upload_qiniu()
        self.db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='inst', charset='utf8')
        self.cursor = self.db.cursor()
        # self.cur_path = os.path.abspath(os.curdir).replace('\\', '/') + '/' + self.name + '/'
        self.cur_path = 'F:/instagram/' + self.name + '/'
        if not os.path.exists(self.cur_path):
            os.makedirs(self.cur_path)
        self.proxies = {'https': '127.0.0.1:1080'}

    def parse_main_url(self):
        while not self.mainurl_queue.empty():
            print '正在翻页扫描图片,剩余', self.mainurl_queue.qsize(), '页'
            url = self.mainurl_queue.get()
            self.mainurl_queue.task_done()
            try:
                print '正在浏览：', url
                self.browser.get(url)
                htmlsource = self.browser.page_source
                soup = BeautifulSoup(htmlsource, 'lxml')
#                 urls = soup.find_all('a')
#                 for i in range(len(urls)):
#                     url = self.domain + urls[i]['href']
#                     if re.findall('max_id', url):
#                         self.mainurl_queue.put(url)
                
                scriptss = soup.find_all('script', attrs={'type':'text/javascript'})
                json_str = ''
                for i in range(len(scriptss)):
                    if not (scriptss[i].string == None):
                        if ('window._sharedData' in scriptss[i].string):
                            json_str = scriptss[i].string.replace('window._sharedData = ', '').replace(';', '').replace('\'', '')
                json_data = json.loads(json_str)
                name = json_data['entry_data']['ProfilePage'][0]['user']['username']
                users = json_data['entry_data']['ProfilePage'][0]['user']['media']['nodes']
                if(len(users) == 0):
                    continue
                url = self.domain + '/' + name + '/?max_id=' + users[len(users) - 1]['id']
                avatar_url = json_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url_hd']
                self.save_avatar(avatar_url)
                self.mainurl_queue.put(url)
                for i in range(len(users)):
                    imgurl = users[i]['display_src']
                    if not self.is_exist(imgurl):
                        page_url = self.domain + '/p/' + users[i]['code'] + '/'
                        vote = users[i]['likes']['count']
                        date = time.strftime('%Y-%m-%d', time.localtime(users[i]['date']))
                        queue_data = (imgurl, page_url, vote, date)
                        self.imgurl_queue.put(queue_data)
                    else:
                        print '图片已存在'
            except TimeoutException as e:
                print '出现异常1：', e
            except WebDriverException as e:
                print '出现异常2：', e
        self.parse_img_url()

    def parse_img_url(self):
        while not self.imgurl_queue.empty():
            print '正在保存图片url,剩余', self.imgurl_queue.qsize(), '条'
            queue_data = self.imgurl_queue.get()
            imgurl = queue_data[0]
            page_url = queue_data[1]
            vote = queue_data[2]
            date = queue_data[3]
            try:
                with requests.session() as s:
                    s.keep_alive = False
                    print '正在下载图片========', page_url, '\n', imgurl
                    r = s.get(imgurl, proxies=self.proxies)
                    file_name = imgurl.split('/')[-1]
                    path = self.cur_path + file_name
                    with open(path, 'wb') as f:
                        f.write(r.content)
                # 上传图片到七牛云 暂停上传
                self.up.upload(self.name + '/' + file_name, path)
                print "上传到七牛云成功"
                qiniu_url = 'http://ou43h7cjd.bkt.clouddn.com/' + self.name + '/' + file_name
                sql = 'insert into instagram (name,content_url,img_url,qiniu_url,vote,date) values (%s,%s,%s,%s,%s,%s)'
                values = (self.name, page_url, imgurl, qiniu_url, vote, date)
                self.cursor.execute(sql, values)
                self.db.commit()
                print "====插入数据库成功，七牛云url:", qiniu_url
            except TimeoutException as e:
                print '出现异常1：', e
            except WebDriverException as e:
                print '出现异常2：', e
            except Exception as e:
                print '出现异常3：', e

    def save_avatar(self,url):
        sql = 'select avatar_url from star where en_name = %s'
        values = (self.name)
        self.cursor.execute(sql,values)
        self.db.commit()
        avatar_url = self.cursor.fetchone()
        if avatar_url[0] == url:
            return
        with requests.session() as s:
            s.keep_alive = False
            print '正在下载头像========', url
            r = s.get(url, proxies=self.proxies)
            file_name = url.split('/')[-1]
            path = self.cur_path + file_name
            with open(path, 'wb') as f:
                f.write(r.content)
        # 上传图片到七牛云 暂停上传
        self.up.upload(self.name + '/' + file_name, path)
        print "上传到七牛云成功"
        qiniu_url = 'http://ou43h7cjd.bkt.clouddn.com/' + self.name + '/' + file_name
        sql_update = 'update star set avatar_url = %s , qiniu_avatar_url = %s where en_name = %s'
        values_update = (url,qiniu_url,self.name)
        self.cursor.execute(sql_update, values_update)
        self.db.commit()
        
    def is_exist(self, url):
        sql = 'select * from instagram where name = ' + '"' + self.name + '" and' + ' img_url = "' + url + '"'
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()

    def main(self):
        self.mainurl_queue.put(self.url)
        self.parse_main_url()
        self.browser.close()
        self.db.close()
