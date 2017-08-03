# coding:utf-8

from selenium import webdriver
from bs4 import BeautifulSoup
import re
import os
import Queue
import requests
from selenium.common.exceptions import TimeoutException, WebDriverException
import threading,time


class Instagram_Spider():
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.browser = webdriver.PhantomJS()
        self.domain = 'https://www.instagram.com'
        # 三层队列
        self.mainurl_queue = Queue.Queue()
        self.imgurl_queue = Queue.Queue()
        self.img_queue = Queue.Queue()
        #
        self.cur_path = os.path.abspath(os.curdir).replace('\\', '/') + '/' + self.name + '/'
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
                        self.imgurl_queue.put(url)
                        # with open('imgurl.txt','a+') as f:
                        #     f.write(url+'\n')
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
                        url = imgs[i]['src']
                        self.img_queue.put(url)
                        print url
                elif len(divs2):
                    videos = divs2[0].find_all('video')
                    for i in range(len(videos)):
                        url = videos[i]['src']
                        self.img_queue.put(url)
                        print url
            except TimeoutException as e:
                print '出现异常：', e
            except WebDriverException as e:
                print '出现异常：', e
        self.download_img()

    def thread_download(self):
        threads = []
        for i in range(5):
            th = threading.Thread(target=self.download_img)
            threads.append(th)
        for t in threads:
            t.run()
            t.join()

    def download_img(self):
        while not self.img_queue.empty():
            print '剩余', self.img_queue.qsize(), '张图片'
            url = self.img_queue.get()
            with requests.session() as s:
                s.keep_alive = False
                print '正在下载图片========', url
                r = s.get(url,proxies=self.proxies)
                path = self.cur_path + url.split('/')[-1]
                with open(path, 'wb') as f:
                    f.write(r.content)
                    self.img_queue.task_done()

    def main(self):
        self.mainurl_queue.put(self.url)
        self.parse_main_url()
        self.browser.close()
