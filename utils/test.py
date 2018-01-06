#coding=utf-8
'''
Created on 2018年1月4日

@author: kist
'''

from selenium import webdriver
from bs4 import BeautifulSoup
import json
from upload_qiniu import upload_qiniu

# url = 'https://www.instagram.com/zhaoliyingofficial/'
# browse = webdriver.PhantomJS()
# browse.get(url)
# htmlsource = browse.page_source
# soup = BeautifulSoup(htmlsource, 'lxml')
# scriptss = soup.find_all('script', attrs={'type':'text/javascript'})
# scr = ''
# for i in range(len(scriptss)):
#     if not (scriptss[i].string == None):
#         if ('window._sharedData' in scriptss[i].string):
#             scr = scriptss[i].string.replace('window._sharedData = ', '').replace(';', '').replace('\'', '')
# json_data = json.loads(scr)
# 
# print json_data['entry_data']['ProfilePage'][0]['user']['profile_pic_url_hd']

uq = upload_qiniu()
uq.uploadOnline("tttt.png", 'https://scontent-hkg3-1.cdninstagram.com/t51.2885-19/11821321_476362769201491_2127571054_a.jpg')