from flask import Flask, request
from flaskext.mysql import MySQL
import json
import random, time, copy
import threading

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '199358fgm'
app.config['MYSQL_DATABASE_DB'] = 'inst'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

data_size = 20
random_star_size = 10


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/wximg/")
def wximg():
    global data_size
    cursor = mysql.connect().cursor()
    random_stars = get_random_star(cursor)
    datas = []
    for i in range(len(random_stars)):
        en_name = random_stars[i][0]
        cn_name = random_stars[i][1]
        main_page = random_stars[i][2]
        sql = 'select name,qiniu_url from instagram where name = "' + en_name + '" order by rand() limit 2'
        cursor.execute(sql)
        results = cursor.fetchall()
        for j in range(len(results)):
            star_name = results[j][0]
            imgurl = results[j][1]
            url_type = 'mp4' if ('.mp4' in imgurl) else 'jpg'
            datas.append({
                'name': cn_name,
                'main_page': main_page,
                'imgurl': imgurl,
                'type': url_type
                })
    random.shuffle(datas)
    j = json.dumps({
        'data': datas
    })
    cursor.close()
    return j

def get_random_star(cursor):
    global random_star_size
    sql = 'select en_name,cn_name,main_page from star  order by rand() limit ' + str(random_star_size)
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


if __name__ == '__main__':
    app.run(debug=True)
