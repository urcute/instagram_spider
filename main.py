# coding:utf-8

from instagram_spider import Instagram_Spider
import MySQLdb


def get_start_urls():
    start_urls = []
    db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='inst', charset='utf8')
    cursor = db.cursor()
    sql = 'select * from star'
    cursor.execute(sql)
    db.commit()
    stars = cursor.fetchall()
    for star in stars:
        start_urls.append({
            'url': star[4],
            'name': star[1]
        })
    db.close()
    return start_urls


def main():
    start_urls = get_start_urls()
    for i in range(len(start_urls)):
        url = start_urls[i]['url']
        name = start_urls[i]['name']
        print url,name
        ins = Instagram_Spider(url, name)
        ins.main()


main()
