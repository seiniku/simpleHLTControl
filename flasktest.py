from flask import *
from decimal import *
import sqlite3
import simplejson as json
import datetime,time
app = Flask(__name__)
# configuration
app.config['SECRET_KEY'] = 'F34TF$($e34D';

DATABASE = '/home/jkeppers/simpleHLT/db_simple.db'
def adapt_decimal(d):
    return str(d)

def convert_decimal(s):
    return Decimal(s) 
def getConn():
    sqlite3.register_adapter(Decimal, adapt_decimal)
    sqlite3.register_converter("decimal", convert_decimal)
    conn = sqlite3.connect('/home/jkeppers/simpleHLTControl/db_simple.db', detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
    return conn            

@app.route('/hlt')
def hlt():
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("SELECT id from brewday") 
    brewlist = cursor.fetchall()
    return render_template('hltgraph.html',brewid=brewlist)
    
@app.route('/changehlttemp', methods=['POST'])
def changehlttemp():
    session['hlttemp'] = request.form['hlttemp']
    session['brewid'] = request.form['brewid']
    brewid = session['brewid']
    temp = session['hlttemp']
    print "update temp to " + temp
    sqlite3.register_adapter(Decimal, adapt_decimal)
    sqlite3.register_converter("decimal", convert_decimal)
    conn = sqlite3.connect('/home/jkeppers/simpleHLTControl/db_simple.db', detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)
    cursor = conn.cursor()
    cursor.execute("UPDATE tempconfig SET target=? WHERE brewid=?",[temp,brewid])
    
    return redirect(url_for('hlt'))

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
