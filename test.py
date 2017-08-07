#coding: utf-8

from selenium import webdriver
from bs4 import BeautifulSoup
import MySQLdb

url = 'https://www.instagram.com/p/BRVx1nuhcsq/'

browser = webdriver.PhantomJS('phantomjs.exe')
hs = browser.get(url)
print browser.page_source
soup = BeautifulSoup(browser.page_source,'lxml')
votes1 = soup.find_all('span',class_='_tf9x3')
if len(votes1):
    vote = votes1[0].find_all('span')[0].text
votes2 = soup.find_all('span',class_='_9jphp')
if len(votes2):
    vote = votes2[0].find_all('span')[0].text
print vote
dates = soup.find_all('time',class_='_9gcwa _379kp')
if len(dates):
    date = dates[0].get('title')
print date
# print vote
# print ti
#
# db = MySQLdb.connect(host='localhost',user='root',passwd='root',db='inst',charset='utf8')
# cursor = db.cursor()
# t = '2017-08-03'
# sql = 'insert into instagram (name,content_url,img_url,vote,date) values (%s,%s,%s,%s,%s)'
# print sql
# cursor.execute(sql,('1','2','2','2',t))
# db.commit()
# print cursor.fetchall()
# db.close()