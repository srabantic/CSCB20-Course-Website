import sqlite3
from flask import Flask, render_template, redirect, url_for, request, g, session
DATABASE = './assignment3.db'
# connects to the database
def get_db():
    # if there is a database, use it
    db = getattr(g, '_database', None)
    if db is None:
        # otherwise, create a database to use
        db = g._database = sqlite3.connect(DATABASE)
    return db

# converts the tuples from get_db() into dictionaries
# (don't worry if you don't understand this code)
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

# given a query, executes and returns the result
# (don't worry if you don't understand this code)
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

# tells Flask that "this" is the current running app
app = Flask(__name__)
app.secret_key=b'group'


# this function gets called when the Flask app shuts down
# tears down the database connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        # close the database if we are connected to it
        db.close()


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return "You are already logged in"


def valid_login_instructor(username, password):
    instructor_user = query_db('select i_id,i_password from Instructor where i_id = ? and i_password = ?',
                               [username, password], one=True)
    if instructor_user is None:
        return False
    else:
        return True


def valid_login_student(username, password):
    student_user = query_db('select s_id, s_password from Student where s_id = ? and s_password = ?',
                            [username, password], one=True)
    if student_user is None:
        return False
    else:
        return True


def log_the_user_instructor(username):
    user = "instructor"
    name = query_db('select i_firstName from Instructor where i_id = ?', [username])
    return render_template('WelcomePageStudent.html', username=name[0][0], user=user)


def log_the_user_student(username):
    username = username
    name = query_db('select s_firstName from Student where s_id = ?', [username])
    return render_template('WelcomePageStudent.html', username=name[0][0])


@app.route('/login', methods=['GET', 'POST'])
def do_admin_login():
    error = None
    if request.method == 'POST':
        if valid_login_instructor(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            return log_the_user_instructor(request.form['username'])
        elif valid_login_student(request.form['username'], request.form['password']):
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            return log_the_user_student(request.form['username'])
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

@app.route('/new_account')
def new_account():
    return render_template('createAccount.html')

@app.route('/homePage')
def homepage():
    return render_template('Home.html')

@app.route('/calenderPage')
def calender():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('Calendar.html', user=user)
    else:
        return render_template('Calendar.html')

@app.route('/new-newsPage')
def news():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('New_News.html', user=user)
    else:
        return render_template('New_News.html')

@app.route('/discussion-boardPage')
def discussion():
    return render_template('Discussion_Board.html')

@app.route('/lecturesPage')
def lectures():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('Lectures.html', user=user)
    else:
        return render_template('Lectures.html')

@app.route('/labsPage')
def labs():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('LabsPage.html', user=user)
    else:
        return render_template('LabsPage.html')

@app.route('/assignmentsPage')
def assignments():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('AssignmentsPage.html', user=user)
    else:
        return render_template('AssignmentsPage.html')

@app.route('/testsPage')
def tests():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('Tests.html', user=user)
    else:
        return render_template('Tests.html')

@app.route('/courseteamPage')
def courseTeam():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('CourseTeamPage.html', user=user)
    else:
        return render_template('CourseTeamPage.html')

@app.route('/resourcesPage')
def resources():
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        user = "instructor"
        return render_template('ResourcesPage.html', user=user)
    else:
        return render_template('ResourcesPage.html')

@app.route('/enter-marks')
def enter_marks():
    return render_template('Enter_Marks.html')

@app.route('/send-remark-reqs')
def remark_request():
    return render_template('Send_Remark_Requests.html')

@app.route('/create-account', methods=['POST'])
def new_user():
        db = get_db()
        db.row_factory = make_dicts
        cur = db.cursor()
        new_user = request.form
        type_of_user = request.form['options']
        if(type_of_user == "Student"):
            cur.execute('insert into Student(s_id, s_password, s_firstName, s_lastName) values (?, ?, ?, ?)',
                    [new_user['id'],
                     new_user['password'],
                     new_user['firstName'],
                     new_user['lastName']])
            cur.execute('insert into Assignments(s_id) values(?)', [new_user['id']])
            cur.execute('insert into Labs(s_id) values(?)', [new_user['id']])
            cur.execute('insert into Midterms(s_id) values(?)', [new_user['id']])
            cur.execute('insert into Final_Exam(s_id) values(?)', [new_user['id']])
            db.commit()
        elif(type_of_user == "Instructor"):
            cur.execute('insert into Instructor(i_id, i_password, i_firstName, i_lastName) values (?, ?, ?, ?)',
                        [new_user['id'],
                         new_user['password'],
                         new_user['firstName'],
                         new_user['lastName']])
            db.commit()
        cur.close()

        return redirect(url_for('home'))


@app.route('/anon-feedback', methods=['POST'])
def anon_feedback():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()
    i_firstName = request.form['i_firstName']
    i_lastName = request.form['i_lastName']
    i_id = i_firstName + "." + i_lastName + "@mail.utoronto.ca"
    feedback1 = request.form['instructors_teaching_feedback']
    feedback2 = request.form['instructors_recommendation_feedback']
    feedback3 = request.form['labs_experience_feedback']
    feedback4 = request.form['labs_improvement_recommendation']
    feedback5 = request.form['furthur_feedback']

    cur.execute('insert into Anon_Feedback(i_firstName, i_lastName, i_id, instructors_teaching_feedback, instructors_recommendation_feedback,labs_experience_feedback, labs_improvement_recommendation, furthur_feedback) values (?, ?, ?, ?, ?, ?, ?, ?)',
                [i_firstName, i_lastName, i_id, feedback1, feedback2, feedback3, feedback4, feedback5])

    db.commit()
    cur.close()
    return redirect(url_for('discussion'))

@app.route('/instructor-feedback')
def instructors_anon_feedback():
    db = get_db()
    db.row_factory = make_dicts
    anon_feedbacks = []
    id = session['username']
    for anon_feedback in query_db('select i_id, instructors_teaching_feedback,instructors_recommendation_feedback,labs_experience_feedback, labs_improvement_recommendation, furthur_feedback  from Anon_Feedback where i_id = ?', [id]):
        anon_feedbacks.append(anon_feedback)
    db.close()
    return render_template('Instructors_Anon_Feedback.html', anon_feedback=anon_feedbacks)

@app.route('/view-marks-instructor')
def view_marks_instructor():
    db = get_db()
    db.row_factory = make_dicts
    students = []
    for student in query_db(
            'select s_firstName, s_lastName, s_id from Student'):
        students.append(student)
    db.close()
    return render_template('view_mark_instructor.html', student=students)

@app.route('/view-student-mark')
def view_student_marks():
    db = get_db()
    db.row_factory = make_dicts
    username = session['username']
    password = session['password']
    if valid_login_instructor(username, password):
        student_ID = request.args.get('s_id')

    else:
        student_ID = username

    assign_marks = []
    lab_marks = []
    termtest_marks = []
    final_marks = []
    for assign_mark in query_db('select * from Assignments where s_id = ?', [student_ID]):
        assign_marks.append(assign_mark)
    for lab_mark in query_db('select * from Labs where s_id = ?', [student_ID]):
        lab_marks.append(lab_mark)
    for termtest_mark in query_db('select * from Midterms where s_id = ?', [student_ID]):
        termtest_marks.append(termtest_mark)
    for final_mark in query_db('select * from Final_Exam where s_id = ?', [student_ID]):
        final_marks.append(final_mark)
    db.close()
    return render_template('view_marks.html', assign_mark=assign_marks, student_ID=student_ID, lab_mark = lab_marks, termtest_mark=termtest_marks, final_mark=final_marks)


@app.route('/view-mark', methods = ['POST'] )
def view_mark():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()
    s_ID = request.form['s_id']
    s_evaluation = request.form['options']
    mark = request.form['mark']
    if(s_evaluation == "Assignment 1"):
        cur.execute('Update Assignments set a1_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif(s_evaluation == "Assignment 2"):
        cur.execute('Update Assignments set a2_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Assignment 3"):
        cur.execute('Update Assignments set a3_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Term Test 1"):
        cur.execute('Update Midterms set tt1_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Term Test 2"):
        cur.execute('Update Midterms set tt2_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Final Exam"):
        cur.execute('Update Final_Exam set marks = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    labs_helper(s_evaluation, mark, s_ID)
    cur.close()
    return redirect(url_for('enter_marks'))
def labs_helper(s_evaluation, mark, s_ID):
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()
    if (s_evaluation == "Lab 1"):
        cur.execute('Update Labs set Lab1_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 2"):
        cur.execute('Update Labs set Lab2_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 3"):
        cur.execute('Update Labs set Lab3_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 4"):
        cur.execute('Update Labs set Lab4_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 5"):
        cur.execute('Update Labs set Lab5_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 6"):
        cur.execute('Update Labs set Lab6_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 7"):
        cur.execute('Update Labs set Lab7_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 8"):
        cur.execute('Update Labs set Lab8_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 9"):
        cur.execute('Update Labs set Lab9_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    elif (s_evaluation == "Lab 10"):
        cur.execute('Update Labs set Lab10_mark = (?) where s_id = (?)', (mark, s_ID))
        db.commit()
    cur.close()

@app.route('/show-remark-reqs')
def view_remark_request():
    db = get_db()
    db.row_factory = make_dicts
    remarks = []
    for remark in query_db('select *  from Remark_Request'):
        remarks.append(remark)
    db.close()
    return render_template('Show_Remark_Reqs.html', remark=remarks)

@app.route('/send-remark-reqs', methods=['POST'])
def send_remark_request():
    db = get_db()
    db.row_factory = make_dicts
    cur = db.cursor()
    remark_username = request.form['fname']
    remark_worktype = request.form['options']
    remark_reason = request.form['requests']
    cur.execute('insert into Remark_Request(s_id, termwork_type, reason_for_remark) values (?, ?, ?)',
                    [remark_username, remark_worktype, remark_reason])
    db.commit()
    cur.close()
    return redirect(url_for('remark_request'))



if __name__ == '__main__':
    app.run(debug=True)
