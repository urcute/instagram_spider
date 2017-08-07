from flask import Flask, request
from flaskext.mysql import MySQL
import json
import random

mysql = MySQL()
app = Flask(__name__)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'inst'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
cursor = mysql.connect().cursor()

_starsql = 'select en_name from star'
cursor.execute(_starsql)
stars = []
for s in cursor.fetchall():
    stars.append(s[0])

cursor.execute('SELECT MAX(id) FROM instagram')
max = cursor.fetchone()


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/test/")
def test():
    name = request.args.get('name')
    choose_star = random.choice(stars)
    cursor.execute('SELECT MAX(id) FROM instagram')
    max = cursor.fetchone()[0]
    cursor.execute('SELECT MIN(id) FROM instagram')
    min = cursor.fetchone()[0]
    target_id = int((max - min) * random.random() + min)
    sql = 'SELECT name,qiniu_url,id FROM `instagram` WHERE id = ' + str(target_id) + ' ORDER BY id LIMIT 1;'
    cursor.execute(sql)
    result = cursor.fetchone()
    j = json.dumps({
        'data': {
            'name': result[0],
            'imgurl': result[1]
        }
    })
    return j


if __name__ == '__main__':
    app.run(debug=True)
