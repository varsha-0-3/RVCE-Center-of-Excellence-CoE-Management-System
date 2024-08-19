from flask import Flask,flash, render_template, request, redirect, url_for, session
from flask_login import login_required
from flask_mysqldb import MySQL
import datetime
import MySQLdb.cursors
import re
from flask_mail import Mail, Message


from werkzeug.security import generate_password_hash,check_password_hash
app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['MYSQL_HOST'] = 'mysql-168bd9e5-coe-dbms-24.a.aivencloud.com'
app.config['MYSQL_PORT'] = 22777
app.config['MYSQL_USER'] = 'avnadmin'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'coe_management'

mysql = MySQL(app)

# Initialize Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Add your SMTP server details
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'coecommunityconnect@gmail.com'  # Add your email username
app.config['MAIL_PASSWORD'] = 'ffae uqwl xjzw yzbd'  # Add your email password
mail=Mail(app)


@app.route('/')
@app.route('/home')
def home():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT name FROM coe')
    coe_names = cursor.fetchall()
    cursor.close()

    # Check if a student or faculty member is logged in
    studentloggedin = session.get('studentloggedin', False)
    facultyloggedin = session.get('facultyloggedin', False)

    # Pass a flag indicating whether to display the logout button
    return render_template('home.html', coe_names=coe_names, studentloggedin=studentloggedin, facultyloggedin=facultyloggedin)

@app.route('/student_profile')
def student_profile():
    if 'studentloggedin' in session:
        # Fetch student details from student table
        cursor_student = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_student.execute('SELECT * FROM student WHERE usn = %s', (session['usn'],))
        student_details = cursor_student.fetchone()
        cursor_student.close()

        # Fetch student project details with project details from student_project and project tables
        cursor_project = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_project.execute('''
            SELECT sp.*, p.*
            FROM student_project sp
            INNER JOIN project p ON sp.project_id = p.project_id
            WHERE sp.usn = %s
        ''', (session['usn'],))
        student_projects = cursor_project.fetchall()
        cursor_project.close()

        # Pass student details and projects to the profile template
        return render_template('profile.html', student=student_details, projects=student_projects)

    
from flask import jsonify

@app.route('/faculty_profile')
def faculty_profile():
    # Retrieve faculty details
    cursor_faculty = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor_faculty.execute('SELECT * FROM faculty WHERE faculty_id=%s', (session['faculty_id'],))
    faculty_details = cursor_faculty.fetchone()
    cursor_faculty.close()
    cursor_completed = mysql.connection.cursor()
    cursor_completed.execute('SELECT COUNT(*) FROM project WHERE coe_id=%s AND project_status=%s', (1, "COMPLETED"))
    completed_count = cursor_completed.fetchone()[0]
    cursor_completed.close()

    # Count started projects
    cursor_started = mysql.connection.cursor()
    cursor_started.execute('SELECT COUNT(*) FROM project WHERE coe_id=%s AND project_status=%s', (1, "STARTED"))
    started_count = cursor_started.fetchone()[0]
    cursor_started.close()

    # Count not started projects
    cursor_not_started = mysql.connection.cursor()
    cursor_not_started.execute('SELECT COUNT(*) FROM project WHERE coe_id=%s AND project_status=%s', (1, "NOT STARTED"))
    not_started_count = cursor_not_started.fetchone()[0]
    cursor_not_started.close()
    # Retrieve completed projects
    cursor_completed = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor_completed.execute('SELECT * FROM project WHERE coe_id=%s AND project_status=%s', (1,"COMPLETED"))
    completed_projects = cursor_completed.fetchall()
    cursor_completed.close()

    # Retrieve started projects
    cursor_started = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor_started.execute('SELECT * FROM project WHERE coe_id=%s AND project_status=%s', (1,"STARTED"))
    started_projects = cursor_started.fetchall()
    cursor_started.close()

    # Retrieve not started projects
    cursor_not_started = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor_not_started.execute('SELECT * FROM project WHERE coe_id=%s AND project_status=%s', (1,"NOT STARTED"))
    not_started_projects = cursor_not_started.fetchall()
    cursor_not_started.close()

    # Retrieve internship details
    cursor_internship = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor_internship.execute('SELECT * FROM internship WHERE coe_id=%s', (1,))
    internship_details = cursor_internship.fetchall()
    cursor_internship.close()

    # Retrieve total sanction amount received for the COE
    cursor_sanction = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor_sanction.execute('SELECT SUM(sanction_amount) AS total_sanction FROM project WHERE coe_id=%s', (1,))
    total_sanction = cursor_sanction.fetchone()['total_sanction']
    cursor_sanction.close()

    return render_template('faculty_profile.html', faculty_details=faculty_details, 
                           completed_projects=completed_projects, 
                           started_projects=started_projects, 
                           not_started_projects=not_started_projects,
                           internship_details=internship_details,
                           total_sanction=total_sanction,completed_count=completed_count,started_count=started_count,not_started_count=not_started_count)


@app.route('/VC')
def VC():
    # Check if session variables exist before accessing them
    studentloggedin = session.get('studentloggedin', False)
    facultyloggedin = session.get('facultyloggedin', False)

    # Assuming you have some logic to fetch COE data here
    # You can also fetch subscribed status here if needed
    subscribed = False  # Default to False if subscribed status is not retrieved properly

    # Check the subscription status for the current user
    if 'usn' in session:  # Assuming 'usn' is set upon login
        usn = session['usn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM subscribe WHERE usn = %s AND coe_id = %s', (usn, 1))
        subscription = cursor.fetchone()
        if subscription:
            subscribed = True

    # Render VC.html with session variables and subscription status
    return render_template('VC.html', studentloggedin=studentloggedin, facultyloggedin=facultyloggedin, subscribed=subscribed)
    # Render VC.html with session variables and subscription status
    return render_template('VC.html', studentloggedin=studentloggedin, facultyloggedin=facultyloggedin, subscribed=subscribed)

@app.route('/WIC')
def WIC():
    # Check if session variables exist before accessing them
    studentloggedin = session.get('studentloggedin', False)
    facultyloggedin = session.get('facultyloggedin', False)
    print(studentloggedin)
    # Render VC.html with session variables
    return render_template('WIC.html', studentloggedin=studentloggedin, facultyloggedin=facultyloggedin)
# @app.route('/layout.html')
# def layout():
#     return render_template('layout.html')

@app.route('/internship_form')
def internship_form():
    # Render the page with the form to add internship details
    return render_template('internship_form.html')

@app.route("/project_form")
def project_form():
    return render_template('add_project.html')

@app.route("/VC_project_view")
def VC_project_view():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM project WHERE coe_id=1')
    projects = cursor.fetchall()
    return render_template('VC_teacher_project_view.html',projects=projects)


@app.route("/teacher_update_project",methods=["GET"])
def teacher_update_project():
    if request.method=="GET":
            project_id = request.args.get('project_id')
            return render_template('teacher_update_project.html', project_id=project_id)

from flask import redirect

@app.route("/update_project_new",methods=["GET","POST"])
def update_project_new():
    if request.method=="POST":
        project_id=request.form['project_id']
        project_status = request.form.get('project_status')
        duration=request.form.get('duration')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE project SET project_status = %s, duration = %s WHERE project_id = %s', (project_status, duration, project_id))
        mysql.connection.commit()
        cursor.close()

        # Redirect to VC_project_view route after updating
        return redirect('/VC_project_view')


from flask import render_template, request

@app.route("/view_applications_project_VC", methods=["POST"])
def view_applications():
    # Retrieve project_id from the form data
    project_id = request.form.get('project_id')

    # Query the student_project database to fetch records associated with the project_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT student_project.*, student.name AS student_name, student.dept AS student_dept
        FROM student_project
        JOIN student ON student_project.usn = student.usn
        WHERE student_project.project_id = %s
        AND student_project.approval_status= %s
    ''', (project_id,"NO"))
    applications = cursor.fetchall()
    cursor.close()

    # Render the view_application_projects_VC.html template passing the fetched records
    return render_template('view_applications_projects_VC.html', applications=applications)




@app.route("/approve_application_project_VC", methods=["POST"])
def approve_application():
    # Retrieve project_id and usn from the form data
    project_id = request.form.get('project_id')
    usn = request.form.get('usn')

    # Update the student_project table to set the approval status to "YES" for the specified project and student
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        UPDATE student_project
        SET approval_status = 'YES'
        WHERE project_id = %s AND usn = %s
    ''', (project_id, usn))
    mysql.connection.commit()
    cursor.close()

    # Redirect to the page displaying the updated list of applications
    return redirect('/VC_project_view')




@app.route('/update_project', methods=['GET', 'POST'])
def update_project():
    if request.method == "POST":
        title = request.form['title']
        start_date = request.form['start_date']
        duration = request.form['duration']
        last_apply_date = request.form['last_apply_date']
        sponsored_by = request.form['sponsored_by']
        sanctioned_amount = request.form['sanctioned_amount']
        coe_id = session['coe_id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO project (title, start_date, last_apply_date, company_name, sanction_amount, coe_id, project_status, duration) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                       (title, start_date, last_apply_date, sponsored_by, sanctioned_amount, coe_id, "NOT STARTED", duration))
        mysql.connection.commit()
        flash("Project updated successfully!", "success")  # Flash success message

        # Retrieve COE name from the database
        cursor.execute('SELECT name FROM coe WHERE coe_id = %s', (coe_id,))
        coe_data = cursor.fetchone()
        if coe_data:
            coe_name = coe_data['name']
        else:
            coe_name = 'Your COE Name'  # Default value if COE name not found

        # Retrieve the list of subscribed students and their emails from the subscribe and student tables
        cursor.execute('''
            SELECT s.email_id
            FROM subscribe AS sub
            INNER JOIN student AS s ON sub.usn = s.usn
            WHERE sub.coe_id = %s
        ''', (coe_id,))
        subscribed_students = cursor.fetchall()
        cursor.close()

        # Compose email message
        subject = f'New Project Added in {coe_name} COE'
        body = f'Dear student,\n\nA new project has been added to {coe_name} Center of Excellence.\n\nProject Title: {title}\nLast Date to Apply: {last_apply_date}'
        
        for student in subscribed_students:
            recipient = student['email_id']
            msg = Message(subject, sender='coecommunityconnect@gmail.com', recipients=[recipient])
            msg.body = body

            # Send the email
            mail.send(msg)

        return redirect(url_for('VC'))  # Redirect to VC.html page
    else:
        return "Unauthorized access!"  # You can customize this response for non-faculty users


@app.route('/add_internship_VC', methods=['GET', 'POST'])
def add_internship_VC():
    if request.method == "POST":
        title = request.form['title']
        start_date = request.form['start_date']
        duration = request.form['duration']
        last_apply_date = request.form['last_apply_date']
        fees = request.form['fees']
        coe_id = session['coe_id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO internship (title, start_date, duration,fees,coe_id,last_apply_date) VALUES (%s, %s, %s, %s, %s, %s)',
                       (title, start_date, duration, fees, coe_id,last_apply_date))
        mysql.connection.commit()
        flash("Internship updated successfully!", "success")  # Flash success message

        # Retrieve COE name from the database
        cursor.execute('SELECT name FROM coe WHERE coe_id = %s', (coe_id,))
        coe_data = cursor.fetchone()
        if coe_data:
            coe_name = coe_data['name']
        else:
            coe_name = 'Your COE Name'  # Default value if COE name not found

        # Retrieve the list of subscribed students and their emails from the subscribe and student tables
        cursor.execute('''
            SELECT s.email_id
            FROM subscribe AS sub
            INNER JOIN student AS s ON sub.usn = s.usn
            WHERE sub.coe_id = %s
        ''', (coe_id,))
        subscribed_students = cursor.fetchall()
        cursor.close()

        # Compose email message
        subject = f'New Internship Added in {coe_name} COE'
        body = f'Dear student,\n\nA new internship oppurtunity has been added to {coe_name} Center of Excellence.\n\nInternship Title: {title}\nLast Date to Apply: {last_apply_date}'
        
        for student in subscribed_students:
            recipient = student['email_id']
            msg = Message(subject, sender='coecommunityconnect@gmail.com', recipients=[recipient])
            msg.body = body

            # Send the email
            mail.send(msg)

        return redirect('/VC') # Redirect to VC.html page
    else:
        return "Unauthorized access!"  # You can customize this response for non-faculty users


@app.route("/apply_internship_VC")
def apply_internship_VC():
    current_date = datetime.date.today()  # Get the current date
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM internship WHERE coe_id=1 AND DATE(last_apply_date) >= %s', (current_date,))
    internships = cursor.fetchall()
    
    return render_template('apply_internship_VC.html', internships=internships)

@app.route("/VC_internship_view")
def VC_internship_view():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM internship WHERE coe_id=1')
    internships = cursor.fetchall()
    return render_template('VC_teacher_internship_view.html',internships=internships)

@app.route("/view_applications_internship_VC", methods=["POST"])
def view_applications_internship_VC():
    # Retrieve project_id from the form data
    internship_id = request.form.get('internship_id')

    # Query the student_project database to fetch records associated with the project_id
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT student_internship.*, student.name AS student_name, student.dept AS student_dept
        FROM student_internship
        JOIN student ON student_internship.usn = student.usn
        WHERE student_internship.internship_id = %s
    ''', (internship_id))
    applications = cursor.fetchall()
    cursor.close()

    # Render the view_application_projects_VC.html template passing the fetched records
    return render_template('view_applications_internships_VC.html', applications=applications)

@app.route("/student_internship_update", methods=["GET", "POST"])
def student_update_internship():
    if request.method == "POST":
        internship_id = request.form['internship_id']
        usn = request.form['usn']
        
        # Check if the USN exists in the student table
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE usn = %s', (usn,))
        student = cursor.fetchone()
        
        if student is None:
            flash("User does not exist.")
            return render_template('home.html')  # Assuming 'home.html' is your home template
        if session['usn'] !=usn:
            flash("USN doesnt match")
            return redirect('/VC')
        cursor.execute('SELECT * FROM student_internship WHERE usn = %s AND internship_id=%s', (usn,internship_id))
        applied_project=cursor.fetchone()
        if applied_project is not None:
            flash("You have already applied to this internship")
            return redirect('/VC')
        

        # If the user exists, proceed with inserting into the student_internship table
        cursor.execute('INSERT INTO student_internship(usn, internship_id) VALUES (%s, %s)', (usn, internship_id))
        mysql.connection.commit()
        flash("Applied to internship successfully.")
        return redirect('/VC')  # Redirect to some other endpoint after successful application

    return render_template('student_internship_form.html')  # Assuming 'student_internship_form.html' is your form template



@app.route("/apply_project_VC")
def apply_project_VC():
    current_date = datetime.date.today()  # Get the current date
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM project WHERE coe_id=1 AND DATE(last_apply_date) >= %s', (current_date,))
    projects = cursor.fetchall()
    
    return render_template('apply_project_VC.html', projects=projects)


@app.route("/student_project_update",methods=["GET","POST"])
def student_update_project():
    if request.method=="POST" and 'project_id' in request.form and 'usn' in request.form and 'resume_link' in request.form:
        project_id=request.form['project_id']
        usn=request.form['usn']
        resume_link=request.form['resume_link']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE usn = %s', (usn,))
        student = cursor.fetchone()
        if student is None:
            flash("User does not exist.")
            return render_template('home.html')
        if session['usn'] !=usn:
            flash("USN doesnt match")
            return redirect('/VC')
        cursor.execute('SELECT * FROM student_project WHERE usn = %s AND project_id=%s', (usn,project_id))
        applied_project=cursor.fetchone()
        if applied_project is not None:
            flash("You have already applied to this project")
            return redirect('/VC')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO student_project(usn,project_id,approval_status,resume_link) VALUES (%s, %s, %s,%s)',(usn,project_id,"NO",resume_link) )
        mysql.connection.commit()
        flash("Applied to project successfully. Wait for your application to be reviewed")
        return redirect(url_for('apply_project_VC'))



@app.route('/subscribe/<int:coe_id>')
def subscribe_to_coe(coe_id):
    # Ensure the user is logged in as a student
    if 'studentloggedin' in session and session['studentloggedin']:
        usn = session['usn']  # Assuming the USN is stored in session upon login
        
        # Check if the user is already subscribed
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM subscribe WHERE usn = %s AND coe_id = %s', (usn, coe_id))
        subscription = cursor.fetchone()

        if subscription:
            # If already subscribed, unsubscribe by deleting the subscription record
            cursor.execute('DELETE FROM subscribe WHERE usn = %s AND coe_id = %s', (usn, coe_id))
            mysql.connection.commit()
            flash('You have unsubscribed from updates for this COE.', 'info')
            subscribed = False
            cursor.close()
            return redirect(url_for('VC', subscribed=False))
        else:
            # If not subscribed, subscribe by inserting a new record
            cursor.execute('INSERT INTO subscribe (usn, coe_id) VALUES (%s, %s)', (usn, coe_id))
            mysql.connection.commit()
            flash('You have subscribed to updates for this COE.', 'info')
            subscribed = True
            cursor.close()
            return redirect(url_for('VC', subscribed=True))


    else:
        # If not logged in, redirect to login page
        flash('Please log in to subscribe.', 'danger')
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email_id' in request.form and 'password' in request.form:
        email_id = request.form['email_id']
        password = request.form['password']

        # Check student accounts
        cursor_student = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_student.execute('SELECT * FROM student WHERE email_id = %s', (email_id,))
        student_account = cursor_student.fetchone()

        if student_account and check_password_hash(student_account['password'], password):
            session['studentloggedin'] = True
            session['usn'] = student_account['usn']
            session['email_id'] = student_account['email_id']
            session['name'] = student_account['name']
            flash('Student logged in successfully!')
            return redirect(url_for('home'))
        
        # Check faculty accounts
        cursor_faculty = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor_faculty.execute('SELECT * FROM faculty WHERE email_id = %s', (email_id,))
        faculty_account = cursor_faculty.fetchone()

        if faculty_account and check_password_hash(faculty_account['password'], password):
            session['facultyloggedin'] = True
            session['faculty_id'] = faculty_account['faculty_id']
            session['email_id'] = faculty_account['email_id']
            session['name'] = faculty_account['name']
            session['coe_id'] = faculty_account['coe_id']
            flash('Faculty logged in successfully!')
            return redirect(url_for('home'))
        
        msg = 'Incorrect username / password!'

    return render_template('login.html', msg=msg)
@app.route('/logout')
def logout():
    if 'studentloggedin' in session:
        session.pop('studentloggedin', None)
        session.pop('user_type', None)
    elif 'facultyloggedin' in session:
        session.pop('facultyloggedin', None)
    
    session.pop('ID', None)
    session.pop('name', None)
    print(session)
    
    return redirect(url_for('home'))





@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'dept' in request.form and 'coe_id' in request.form and 'email_id' in request.form and 'phone_no' in request.form:
        # Retrieve faculty registration data
        name = request.form['name']
        password = request.form['password']
        hashed_password1 = generate_password_hash(password)
        email_id = request.form['email_id']
        phone_no = request.form['phone_no']
        dept= request.form['dept']
        coe_id=request.form['coe_id']
        # Perform validation and database insertion (similar to student registration)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO faculty(name, password,email_id, phone_no,dept,coe_id) VALUES (%s, %s, %s, %s, %s, %s)',
                       (name,hashed_password1, email_id, phone_no,dept,coe_id))
        mysql.connection.commit()

        msg = 'Faculty registration successful!'
    
    return render_template('faculty_register.html', msg=msg)



@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email_id' in request.form:
        
        name = request.form['name']
        college=request.form['college']
        password = request.form['password']
        hashed_password = generate_password_hash(password)  # Hash the password

        email_id = request.form['email_id']
        dept = request.form['dept']
        usn = request.form['usn']
        phone_no = request.form['phone_no']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM student WHERE email_id = %s', (email_id,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists!'
        elif not name or not password or not email_id:
            msg = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO student(usn,name, password,phone_no,email_id,dept,College) VALUES (%s,%s, %s, %s, %s, %s,%s)',
                           (usn, name, hashed_password, phone_no, email_id, dept,college))  # Store hashed password
            mysql.connection.commit()
            msg = 'Student registration successful!'
            return render_template("home.html")
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)



@app.route('/WomenIC')
def WomenIC():
    # Check if session variables exist before accessing them
    studentloggedin = session.get('studentloggedin', False)
    facultyloggedin = session.get('facultyloggedin', False)

    # Assuming you have some logic to fetch COE data here
    # You can also fetch subscribed status here if needed
    subscribed = False  # Default to False if subscribed status is not retrieved properly

    # Check the subscription status for the current user
    if 'usn' in session:  # Assuming 'usn' is set upon login
        usn = session['usn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM subscribe WHERE usn = %s AND coe_id = %s', (usn, 2))
        subscription = cursor.fetchone()
        if subscription:
            subscribed = True

    # Render VC.html with session variables and subscription status
    return render_template('WIC.html', studentloggedin=studentloggedin, facultyloggedin=facultyloggedin, subscribed=subscribed)
    # Render VC.html with session variables and subscription status
    return render_template('WIC.html', studentloggedin=studentloggedin, facultyloggedin=facultyloggedin, subscribed=subscribed)




@app.route("/internship_WiC")
def internship_WiC():
  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM internship WHERE coe_id=2')
    internships = cursor.fetchall()
    
    return render_template('internship_WiC.html', internships = internships)



@app.route('/CompGenomics')
def CompGenomics():
    # Check if session variables exist before accessing them
    studentloggedin = session.get('studentloggedin', False)
    facultyloggedin = session.get('facultyloggedin', False)

    # Assuming you have some logic to fetch COE data here
    # You can also fetch subscribed status here if needed
    subscribed = False  # Default to False if subscribed status is not retrieved properly

    # Check the subscription status for the current user
    if 'usn' in session:  # Assuming 'usn' is set upon login
        usn = session['usn']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM subscribe WHERE usn = %s AND coe_id = %s', (usn, 3))
        subscription = cursor.fetchone()
        if subscription:
            subscribed = True

    # Render VC.html with session variables and subscription status
    return render_template('CompGenomics.html', studentloggedin=studentloggedin, facultyloggedin=facultyloggedin, subscribed=subscribed)
    # Render VC.html with session variables and subscription status
    return render_template('CompGenomics.html', studentloggedin=studentloggedin, facultyloggedin=facultyloggedin, subscribed=subscribed)




@app.route("/internship_CG")
def internship_CG():
  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM internship WHERE coe_id=3')
    internships = cursor.fetchall()
    
    return render_template('internship_CG.html', internships = internships)

@app.route("/internship_VC")
def internship_VC():
  
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM internship WHERE coe_id=1')
    internships = cursor.fetchall()
    
    return render_template('internship_CG.html', internships = internships)


if __name__ == '__main__':
    app.run(debug=True)


