# required imports; you may add more in the future; currently, we will only use render_template
import sqlite3
from flask import Flask, render_template, g, request, session, redirect, url_for

# tells Flask that "this" is the current running app
app = Flask(__name__)
app.secret_key=b'smash'

# the database file we are going to communicate with
DATABASE = './assignment3.db'

def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()


@app.route('/index.html')
def index():
    if 'user' in session:
        if session['user'] != "":
            return render_template('index.html')
    
    return redirect(url_for('root_after'))

@app.route('/team.html')
def team():
    if 'user' in session:
        if session['user'] != "":
            return render_template('team.html')
    
    return redirect(url_for('root_after'))    

@app.route('/syllabus.html')
def syllabus():
    if 'user' in session:
        if session['user'] != "":
            return render_template('syllabus.html')
    
    return redirect(url_for('root_after'))    

@app.route('/assignment.html')
def assignment():
    if 'user' in session:
        if session['user'] != "":
            return render_template('assignment.html')
    
    return redirect(url_for('root_after'))    

@app.route('/lecture.html')
def lecture():
    if 'user' in session:
        if session['user'] != "":
            return render_template('lecture.html')
   
    return redirect(url_for('root_after'))    

@app.route('/feedback.html')
def feedback():
    if 'user' in session:
        if session['user'] != "" and session['type'] == "student":
            return render_template('feedback.html')
        elif session['user'] != "" and session['type'] == 'instructor':
            db = get_db()
            db.row_factory = make_dicts
            feeds = []
            for feed in query_db('select * from feedback where instructor= ?', [session['user']]):
                
                feeds.append(feed)
            
            db.close()
            return render_template('feedback-instructor.html', feeds = feeds)            
    
    return redirect(url_for('root_after')) 

@app.route('/feedback.html', methods=["POST", "GET"])
def feedback_after():
    db= get_db()
    db.row_factory = make_dicts
    if 'user' in session:
        if session['user'] == "":
            return redirect(url_for('index'))      
    if request.method == 'POST' and session['type'] == 'student':
        if (request.form['instructor'] =="" or request.form['teaching'] =="" or request.form['teachrecommend'] =="" or request.form['labs'] ==""\
            or request.form['labrecommend'] =="") :
            db.close()
            return redirect(url_for('feedback_after'))  
        else:
            cur = db.cursor()
            a = request.form['instructor']
            check = query_db('select * from Instructor where username = ?', [a], one=True)
            if (a != check['username']):
                return "Please Try Again With The Correct UTORID"
            b = request.form['teaching']
            c = request.form['teachrecommend'] 
            d = request.form['labs']
            e = request.form['labrecommend']           
            cur.execute("insert into feedback (instructor, teaching, recommend, lab, labrecommend) values (?, ?, ?, ?, ?)", \
                        [a,b,c,d,e])
            db.commit()
            cur.close()
            db.close()
            return "Thank you for providing an anonymous feedback"
    elif request.method == 'POST' and session['type'] == 'instructor':
        db = get_db()
        db.row_factory = make_dicts
        feeds = []
        for feed in query_db('select * from feedback where instructor= ?', [session['user']], one=True):
            return feed
            feeds.append(feed)
        db.close()
        return render_template('grades-instructor.html', feeds = feeds)
            
        
            
            
    
@app.route('/new_account.html')
def new_account():
    if 'user' in session:
        if session['user'] != "":
            return redirect(url_for('index'))
    return render_template('new_account.html')

@app.route('/grades.html')
def grade():
    if 'user' in session:
        if session['user'] != "":
            if session['type'] == 'student':
                db = get_db()
                db.row_factory = make_dicts
                student = query_db('select * from Student where username = ?', [session['user']], one=True)
                db.close()                    
                return render_template('grades.html', students = student)
            elif session['type'] == 'instructor':
                db = get_db()
                db.row_factory = make_dicts
                students = [[],[]]
                for student in query_db('select * from Student'):
                    students[0].append(student)
                for request in query_db('select * from Remark'):
                    students[1].append(request)
                db.close()
                return render_template('grades-instructor.html', students = students)
            
    
    return redirect(url_for('root_after'))   


    
    
@app.route('/grades.html', methods=["POST", "GET"])
def grade_after():
    db= get_db()
    db.row_factory = make_dicts
    if 'user' in session:
        if session['user'] == "":
            return redirect(url_for('index'))      
    if request.method == 'POST' and session['type'] == 'student':
        if session['type'] == 'student':
            concern = request.form['Concern']
            if request.form['remark'] == "":
                db.close()
                return redirect(url_for('grade_after'))
            remark = request.form['remark']
            cur = db.cursor()
            cur.execute("insert into Remark (username, message, assignment) values (?, ?, ?)", \
                       [session['user'], remark, concern])
            db.commit()
            cur.close()
            db.close()
            return "Your Request Has Successfully Been Sent To The Instructors"
    elif request.method == 'POST' and session['type'] == 'instructor':
        user = request.form['studentid']
        mark = request.form['newgrade']
        assign = request.form['Select']
        student = query_db('select * from Student where username= ?', [user], one=True)
        if student['username'] != user:
            return "Student Does Not Exist, Try Again"
        else:
            cur = db.cursor()
            command = "update Student SET \'" + assign + "\'=\'" + mark + "\' where username=\'"+ user+ "\'"
           
            cur.execute(command)  
            db.commit()
            cur.close()
            db.close()
            return "Mark has successfull been changed"
           
                
    
def check_not_empty():
    for i in session:
        if session[i] == "":
            return False
    return True

def check_not_in_database():
    for instructor in query_db('select * from Instructor'):
        if session['user'] == instructor['username']:
            return True
    for student in query_db('select * from Student'):
        if session['user'] == student['username']:
            return True    
    return False

@app.route('/logout.html')
def logout():
    session.clear()
    return redirect(url_for('root_after'))

@app.route('/new_account.html', methods=['POST', 'GET'])
def new_account_after():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()
    
    
    if request.method == 'POST':
        if (request.form['user'] =="" or request.form['password'] =="" or request.form['firstName'] =="" or request.form['lastName'] ==""\
            or request.form['email'] =="" or "Select" not in request.form):
            db.close()
            return redirect(url_for('new_account_after'))
            
        
        user = request.form['user']
        password = request.form['password']
        fname = request.form['firstName']
        lname = request.form['lastName']
        email= request.form['email']
        typeof = request.form['Select']
        
        if (check_not_in_database()):
            db.close()
            return "The username used already exists as Student/Instructor, Please refer back to the login page."
        
        elif session['type'] == "student" and check_not_empty():
            cur.execute("insert into Student (fname, lname, email, password, username) values (?, ?, ?, ?, ?)", \
                        [fname, lname, email, password, user])
            session['user'] = user
            session['password'] = password
            session['fname'] = fname
            session['lname'] = lname
            session['email'] = email
            session['type'] = typeof         
            db.commit()
            cur.close()
            db.close()
            return redirect(url_for('index'))
        
        elif session['type'] == "instructor" and check_not_empty():
            cur.execute("insert into Instructor (fname, lname, email, password, username) values (?, ?, ?, ?, ?)", \
                        [fname, lname, email, password, user])
            session['user'] = user
            session['password'] = password
            session['fname'] = fname
            session['lname'] = lname
            session['email'] = email
            session['type'] = typeof         
            db.commit()         
            cur.close()
            db.close()
            return redirect(url_for('index'))      
        
        else:
            db.close()
            return redirect(url_for('new_account_after'))
            
        
    
  

@app.route('/')
def root():
    if 'user' in session:
        if session['user'] != "":
            return redirect(url_for('index'))   
    return render_template('login.html')

def check_user_pass(typeof, username, password):

    if typeof == 'instructor':
        for user in query_db('select * from Instructor'):
            if username == user['username'] and user['password'] == password:
                return True
    elif typeof == 'student':
        for user in query_db('select * from Student'):
            if username == user['username'] and user['password'] == password:
                return True
    return False




@app.route('/', methods=['POST','GET'])
def root_after():
    db= get_db()
    db.row_factory = make_dicts
    if 'user' in session:
        if session['user'] != "":
            return redirect(url_for('index'))      
  
    if request.method == 'POST':
 
        user = request.form['username']
        password = request.form['password']
        if 'sign' in request.form:
            session['type'] = request.form['sign']
        else:
            return redirect(url_for('root_after'))
        
       
        if check_user_pass(session['type'], user, password):
            session['user'] = user
            session['password'] = password
            db.close()
            return redirect(url_for('index'))
    db.close()
    return redirect(url_for('root_after'))
            
    
        
      
        

        











# run the app when app.py is run
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug='True')