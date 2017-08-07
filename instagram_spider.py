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


class Instagram_Spider():
    def __init__(self, url, name):
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
            try:
                self.browser.get(url)
                self.mainurl_queue.task_done()
                htmlsource = self.browser.page_source
                soup = BeautifulSoup(htmlsource, 'lxml')
                urls = soup.find_all('a')
                for i in range(len(urls)):
                    url = self.domain + urls[i]['href']
                    if re.findall('/p/.*/', url):
                        print 'imgurl', url
                        if not self.is_exist(url):
                            self.imgurl_queue.put(url)
                            # with open('imgurl.txt','a+') as f:
                            #     f.write(url+'\n')
                        else:
                            print '图片已存在，跳过~~~~~~~~~~~~'
                    if re.findall('max_id', url):
                        print 'mainurl', url
                        # with open('mainurl.txt','a+') as f:
                        #     f.write(url+'\n')
                        self.mainurl_queue.put(url)
            except TimeoutException as e:
                print '出现异常：', e
            except WebDriverException as e:
                print '出现异常：', e
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
                divs1 = soup.find_all('div', class_='_jjzlb')
                divs2 = soup.find_all('div', class_='_2tomm')
                if len(divs1):
                    imgs = divs1[0].find_all('img')
                    for i in range(len(imgs)):
                        imgurl = imgs[i]['src']
                        # self.img_queue.put(url)
                        # print url
                elif len(divs2):
                    videos = divs2[0].find_all('video')
                    for i in range(len(videos)):
                        imgurl = videos[i]['src']
                        # self.img_queue.put(url)
                        # print url
                print imgurl
                with requests.session() as s:
                    s.keep_alive = False
                    print '正在下载图片========', url
                    r = s.get(imgurl, proxies=self.proxies)
                    file_name = imgurl.split('/')[-1]
                    path = self.cur_path + file_name
                    with open(path, 'wb') as f:
                        f.write(r.content)
                votes1 = soup.find_all('span', class_='_tf9x3')
                if len(votes1):
                    vote = votes1[0].find_all('span')[0].text or ''
                votes2 = soup.find_all('span', class_='_9jphp')
                if len(votes2):
                    vote = votes2[0].find_all('span')[0].text or ''
                dates = soup.find_all('time', class_='_9gcwa _379kp')
                if len(dates):
                    date = dates[0].get('title') or ''
                # 上传图片到七牛云
                self.up.upload(self.name + '/' + file_name, path)
                print "====上传到七牛云成功"
                qiniu_url = 'http://ou43h7cjd.bkt.clouddn.com/' + self.name + '/' + file_name
                sql = 'insert into instagram (name,content_url,img_url,qiniu_url,vote,date) values (%s,%s,%s,%s,%s,%s)'
                values = (self.name, url, imgurl, qiniu_url, vote, date)
                self.cursor.execute(sql, values)
                self.db.commit()
                print "====插入数据库成功，七牛云url:", qiniu_url
            except TimeoutException as e:
                print '出现异常：', e
            except WebDriverException as e:
                print '出现异常：', e
            except Exception as e:
                print '出现异常：', e

    def is_exist(self, url):
        sql = 'select * from instagram where name = ' + '"' + self.name + '" and' + ' content_url = "' + url + '"'
        self.cursor.execute(sql)
        self.db.commit()
        return self.cursor.fetchall()

    # def thread_download(self):
    #     threads = []
    #     for i in range(5):
    #         th = threading.Thread(target=self.download_img)
    #         threads.append(th)
    #     for t in threads:
    #         t.run()
    #         t.join()
    #
    # def download_img(self):
    #     while not self.img_queue.empty():
    #         print '剩余', self.img_queue.qsize(), '张图片'
    #         url = self.img_queue.get()
    #         with requests.session() as s:
    #             s.keep_alive = False
    #             print '正在下载图片========', url
    #             r = s.get(url, proxies=self.proxies)
    #             path = self.cur_path + url.split('/')[-1]
    #             with open(path, 'wb') as f:
    #                 f.write(r.content)
    #                 self.img_queue.task_done()

    def main(self):
        self.mainurl_queue.put(self.url)
        self.parse_main_url()
        self.browser.close()
        self.db.close()
