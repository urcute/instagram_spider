# coding:utf-8
import sys,os
from selenium import webdriver
import requests

url = 'http://hkapp-test.noahwm.com/resources/banner/da6ff6ffd67547ea82e37ea51473d9a3.jpg'
r = requests.get(url)
with open('F:/test.jpg','wb') as f:
    f.write(r.content)
print r.content