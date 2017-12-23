# coding:utf-8

from selenium import webdriver
from bs4 import BeautifulSoup
import re
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
            print '111'
            self.mainurl_queue.task_done()
            sleep(1)
            try:
                print '正在浏览：',url
                self.browser.get(url)
                print '正在浏览：',url
                htmlsource = self.browser.page_source
                soup = BeautifulSoup(htmlsource, 'lxml')
                urls = soup.find_all('a')
                print htmlsource.encode('utf-8')
                for i in range(len(urls)):
                    url = self.domain + urls[i]['href']
                    if re.findall('/p/.*/', url):
                        print 'imgurl', url
                        if not self.is_exist(url):
                            self.imgurl_queue.put(url)
                        else:
                            print '图片已存在，跳过~~~~~~~~~~~~'
                    if re.findall('max_id', url):
#                         print 'mainurl', url
                        self.mainurl_queue.put(url)
            except TimeoutException as e:
                print '出现异常1：', e
            except WebDriverException as e:
                print '出现异常2：', e
        self.parse_img_url()

    def parse_img_url(self):
        while not self.imgurl_queue.empty():
            print '正在保存图片url,剩余', self.imgurl_queue.qsize(), '条'
            url = self.imgurl_queue.get()
            try:
                self.browser.get(url)
                self.imgurl_queue.task_done()
                htmlsource = self.browser.page_source
                soup = BeautifulSoup(htmlsource, 'lxml')
                
                res_type = soup.find('meta', attrs={"name": "medium"})['content']
                if(not res_type):
                    continue
                elif res_type == 'image':
                    imgurl = soup.find('meta', property='og:image')['content']
                elif res_type == 'video':
                    imgurl = soup.find('meta', property='og:video')['content']
                votes = soup.find('meta', property='og:description')['content'].encode('utf-8')
                votes = votes.split('-')[0].replace('次赞', '').replace('条评论', '').split('、')
                vote = (votes[0] + '#' + votes[1]).replace(',', '').replace(' ', '')
                post_date = soup.find('meta', property='og:title')['content'].encode('utf-8')
                date = post_date.split('UTC')[1].split('日')[0].replace(' ', '').replace('年', '-').replace('月', '-')
                
                with requests.session() as s:
                    s.keep_alive = False
                    print '正在下载图片========', url
                    r = s.get(imgurl, proxies=self.proxies)
                    file_name = imgurl.split('/')[-1]
                    path = self.cur_path + file_name
                    with open(path, 'wb') as f:
                        f.write(r.content)
                # 上传图片到七牛云 暂停上传
                # self.up.upload(self.name + '/' + file_name, path)
                print "ceshiiiiiiiiiiiiiiiiii====上传到七牛云成功"
                qiniu_url = 'http://ou43h7cjd.bkt.clouddn.com/' + self.name + '/' + file_name
                sql = 'insert into instagram (name,content_url,img_url,qiniu_url,vote,date) values (%s,%s,%s,%s,%s,%s)'
                values = (self.name, url, imgurl, qiniu_url, vote, date)
                self.cursor.execute(sql, values)
                # 暂停插入表
                self.db.commit()
                print "====插入数据库成功，七牛云url:", qiniu_url
            except TimeoutException as e:
                print '出现异常1：', e
            except WebDriverException as e:
                print '出现异常2：', e
            except Exception as e:
                print '出现异常3：', e

    def is_exist(self, url):
        sql = 'select * from instagram where name = ' + '"' + self.name + '" and' + ' content_url = "' + url + '"'
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()

    def main(self):
        self.mainurl_queue.put(self.url)
        self.parse_main_url()
        self.browser.close()
        self.db.close()
