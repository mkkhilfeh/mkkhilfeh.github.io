"""create flask page for keeping track of homework assignment"""
import flask
import time
import sqlite3
import datetime
con = sqlite3.connect("homework.sqlite")
con.execute(
        """
    CREATE TABLE IF NOT EXISTS hwork (
        id INTEGER PRIMARY KEY,
        assignment_name TEXT,
        class TEXT,
        assigned_time TEXT,
        due_date TEXT,
        complete_time REAL DEFAULT NULL,
        status INTEGER DEFAULT 0);
    """)#creates data base if does not exist
con.commit()
con.close()
app = flask.Flask("Homework")

@app.route("/")
def Home():
    """brings to main page"""
    return flask.redirect("/list/")

@app.route("/list/")  
def message():
    """main page with incomplete assignmets and buttons to take to other pages"""              
    con = sqlite3.connect("homework.sqlite")
    assignments=con.execute("SELECT assignment_name,class,assigned_time,due_date,id FROM hwork WHERE status=0 ORDER BY id ASC")
    assi=assignments.fetchall()
    con.commit()
    con.close()
    return flask.render_template('main_homework_temp.html', assi=assi)

@app.route("/complete/<ass>/")
def comp(ass):
    """complete button, changes status and addes complete time"""
    com_time=datetime.datetime.fromtimestamp(time.time()).strftime("%I:%M%p on %B %d, %Y")
    con = sqlite3.connect("homework.sqlite")
    con.execute("UPDATE hwork SET status=1,complete_time=? WHERE id=?;",(com_time,ass))
    con.commit()
    con.close()
    return flask.redirect("/list/")

@app.route("/cancel/<ass>/")
def canc(ass):
    """cancel button, changes status"""
    con = sqlite3.connect("homework.sqlite")
    con.execute("UPDATE hwork SET status=2 WHERE id=?;",[ass])
    con.commit()
    con.close()
    return flask.redirect("/list/")

@app.route("/list/canceled-complete/")
def ComAndCan():    
    """list of complete and canceled assignments"""          
    con = sqlite3.connect("homework.sqlite")
    assignments=con.execute("SELECT assignment_name,class,assigned_time,due_date,id,complete_time FROM hwork WHERE status=1 or status=2 ORDER BY  id ASC")
    assi=assignments.fetchall()
    con.commit()
    con.close()
    return flask.render_template("comp_canc_temp.html", assi=assi)

@app.route("/redo/<ass>/")
def redo(ass):
    """moves complete and canceled assignments to incomplete"""
    con = sqlite3.connect("homework.sqlite")
    con.execute("UPDATE hwork SET status=0,complete_time=NULL WHERE id=?;",[ass])
    con.commit()
    con.close()
    return flask.redirect("/list/canceled-complete/")

@app.route("/delete/<ass>/")
def delete(ass):
    """delete assignmet permently"""
    con = sqlite3.connect("homework.sqlite")
    con.execute("DELETE FROM hwork WHERE id=?",[ass])
    con.commit()
    con.close()
    return flask.redirect("/list/canceled-complete/")
@app.route("/new/")
def new():
    """new assignment page"""
    return flask.render_template("hwk_input.html")

@app.route("/new/submit/",methods=["GET", "POST"])
def newsub():
    """submit new assignment"""
    assignment_name = flask.request.values.get("assignment_name")
    clas= flask.request.values.get("class")
    due_date =flask.request.values.get("due_date")
    due_date=datetime.datetime.fromisoformat(due_date).strftime("%I:%M%p on %B %d, %Y") #time formating
    con = sqlite3.connect("homework.sqlite")
    con.execute("INSERT INTO hwork (assignment_name,class,due_date,assigned_time) VALUES (?,?,?,?)",(assignment_name,clas,due_date,datetime.datetime.fromtimestamp(time.time()).strftime("%I:%M%p on %B %d, %Y")))
    assignments=con.execute("SELECT id FROM hwork WHERE assignment_name=? and class=? and due_date=?",(assignment_name,clas,due_date))
    assi=assignments.fetchall()
    con.commit()
    con.close()
    return flask.redirect("/list/{}".format(assi[0][0]))

@app.route("/list/class/<classs>/")  
def classs(classs):
    """shows list of assignment in a class"""              
    con = sqlite3.connect("homework.sqlite")
    assignments=con.execute("SELECT assignment_name,class,assigned_time,due_date,id,complete_time FROM hwork WHERE class=? ORDER BY  id ASC",[classs])
    assi=assignments.fetchall()
    con.commit()
    con.close()
    return flask.render_template("class_templateste.html",assi=assi,classs=classs)

@app.route("/list/class/")  
def listc():    
    "list of classes of all assignmets"          
    con = sqlite3.connect("homework.sqlite")
    assignments=con.execute("SELECT DISTINCT class FROM hwork")
    assi=assignments.fetchall()
    con.commit()
    con.close()
    return flask.render_template("list_classes_temp.html", assi=assi)

@app.route("/list/<assgin>/")
def indass(assgin):
    """page for just assignment"""
    con = sqlite3.connect("homework.sqlite")
    assignments=con.execute("SELECT assignment_name,class,assigned_time,due_date,id,complete_time,status FROM hwork WHERE id=?",[assgin])
    assi=assignments.fetchall()
    con.commit()
    con.close()
    print(assi)
    if assi[0][6]==0: #incomplete assignment
        return flask.render_template("main_homework_temp.html", assi=assi)
    else: #complete assignment
        return flask.render_template("comp_canc_temp.html", assi=assi)

app.run()