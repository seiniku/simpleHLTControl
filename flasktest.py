from flask import *
import MySQLdb as mdb
import simplejson as json
import datetime,time
app = Flask(__name__)
# configuration
app.config['SECRET_KEY'] = 'F34TF$($e34D';

def getConn():
    conn = mdb.connect('chop.bad.wolf','brew','brewit','brewery');
    return conn

@app.route('/hlt')
def hlt():
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("SELECT id from brewday")
    brewlist = cursor.fetchall()
    conn.close()
    return render_template('hltgraph.html',brewid=brewlist)

@app.route('/changehlttemp', methods=['POST'])
def changehlttemp():
    session['hlttemp'] = request.form['hlttemp']
    session['brewid'] = request.form['brewid']
    brewid = session['brewid']
    temp = session['hlttemp']
    print "update temp to " + temp
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("UPDATE tempconfig SET target=%s WHERE brewid=%s",[temp,brewid])
    conn.commit()
    conn.close()
    return redirect(url_for('hlt'))

def getcurrentdata():
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("SELECT time,temp FROM templog where time = (select max(time) from templog)")
    conn.close()
    return cursor.fetchone()


@app.route('/hlt.json')
def latest_json():
    data = list(getcurrentdata())
    data[0] = int(time.mktime(data[0].timetuple()) * 1000)
    print type(data[0])

    #return json.dumps(data)
    thetime = data[0]
    thetemp = data[1]
    return jsonify(time=thetime, temp=thetemp)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
