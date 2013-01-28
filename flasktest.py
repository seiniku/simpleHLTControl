from flask import *
from decimal import *
import sqlite3
import simplejson as json
import datetime,time
app = Flask(__name__)
# configuration
DATABASE = '/home/jkeppers/simpleHLT/db_simple.db'

def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return Decimal(s) 

@app.route('/hlt')
def hlt():
    return render_template('hltgraph.html')


def getcurrentdata():
    sqlite3.register_adapter(Decimal, adapt_decimal)
    sqlite3.register_converter("decimal", convert_decimal)
    conn = sqlite3.connect('/home/jkeppers/simpleHLTControl/db_simple.db', detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("SELECT time,temp FROM templog where time = (select max(time) from templog)")
    return cursor.fetchone()


@app.route('/hlt.json')
def hello_world():
    data = list(getcurrentdata())
    data[0] = int(time.mktime(data[0].timetuple()) * 1000)
    print type(data[0])

    #return json.dumps(data) 
    thetime = data[0]
    thetemp = data[1]
    return jsonify(time=thetime, temp=thetemp)

if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
