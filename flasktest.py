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
    cursor.execute("SELECT id from brewlog ORDER BY id DESC")
    brewlist = cursor.fetchall()
    conn.close()
    return render_template('hltgraph.html',brewid=brewlist)

@app.route('/changehlttemp', methods=['POST'])
def changehlttemp():
    session['hlttemp'] = request.form['hlttemp']
    session['brewid'] = request.form['brewdown']
    brewid = session['brewid']
    temp = session['hlttemp']
    print "update temp to " + temp
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("UPDATE tempconfig SET target=%s WHERE brewid=%s",[temp,brewid])
    conn.commit()
    conn.close()
    return redirect(url_for('hlt'))

def getcurrentdata(brewid):
    conn = getConn()
    cursor = conn.cursor()
#    cursor.execute("SELECT time,temp FROM templog where brewid = %s AND time = (select max(time) from templog)",[brewid])


    cursor.execute("SELECT time, temp FROM templog WHERE brewid = %s ORDER BY time DESC LIMIT 1",[brewid])
    conn.close()
    return cursor.fetchone()

def getalldata(brewid):
    conn = getConn()
    cursor = conn.cursor()
    cursor.execute("Select time,temp from templog where brewid=%s order by time",[brewid])
    conn.close()
    return cursor.fetchall()

@app.route('/hlt_full/<int:B_id>')
def full_json(B_id):
    data = list(getalldata(B_id))
    newdata = list()
    for entry in data:
        newdate = int(time.mktime(entry[0].timetuple()) * 1000)
        newentry = [newdate, entry[1]]
        newdata.append(newentry)
    return Response(json.dumps(newdata), mimetype='application/json')

@app.route('/hlt_new/<int:B_id>')
def latest_json(B_id):
    data = list(getcurrentdata(B_id))
    data[0] = int(time.mktime(data[0].timetuple()) * 1000)
    thetime = data[0]
    thetemp = data[1]
    return jsonify(time=thetime, temp=thetemp)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)
