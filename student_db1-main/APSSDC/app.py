from flask import Flask,render_template,request,url_for,session,redirect
from pymysql import connections
import boto3
from config import *

app=Flask(__name__)
app.secret_key = 'AP21110011'

db_conn=connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
S3 = boto3.resource('s3',
                    region_name='',
                    aws_access_key_id="",
                    aws_secret_access_key="")


@app.route("/",methods=['GET','POST'])
def home():
    return  render_template("index.html")
    


@app.route("/admin_login")
def admin_login():
    session.pop('user', None)
    return  render_template("admin_login.html")

@app.route("/admin_page",methods=['GET','POST'])
def admin_page():
    if request.method=='POST':
        user_name=request.form.get('username')
        passw=request.form.get('pass')
        
        if(user_name==admin_name and passw==admin_pass):
            user = {
                'User': user_name,
                'Password': passw
            }
            session['user'] = user
            return redirect('/protected')
    return  f"Access Denied"


@app.route("/protected")
def protected():
    try:
        user = session.get('user')
        if user:
            return render_template("admin_page.html")
        else:
            return "Access denied."
    except Exception as e:
        return str(e)

@app.route("/update_pass")
def update_pass():
    try:
        user = session.get('user')
        if user:
            return render_template("update_password.html")
        else:
            return "Access denied."
    except Exception as e:
        return str(e)
    

@app.route("/updatePassPage",methods=['GET','POST'])
def new_password():
    try:
        if request.method=='POST':
            user = session.get('user')
            if user:
                Roll=request.form.get('Roll')
                passw=request.form.get('pass')
                new_passw=request.form.get('new_pass')
                if(passw==new_passw):
                    cursor=db_conn.cursor()
                    query = "UPDATE data SET password = %s WHERE Roll = %s"
                    cursor.execute(query, (passw, Roll))
                    db_conn.commit()
                    return f"Updated the password of {Roll}"
                else:
                    return "Access denied."
    except Exception as e:
        return str(e)
    
        

    
@app.route("/addstudent")
def addstudent():
    try:
        user = session.get('user')
        if user:
            return  render_template("addstudent.html")
        else:
            return "Access denied."
    except Exception as e:
        return str(e)
    

@app.route("/student_register")
def student_register():
    try:
        user = session.get('user')
        if user:
            return  render_template("addstudent.html")
        else:
            return f"access denied"
    except Exception as e:
        return str(e)

@app.route("/admin_logout")
def admin_logout():
    session.pop('user', None)
    return  render_template("index.html")

@app.route("/student_login")
def student_login():
    return  render_template("student_login.html")


@app.route("/change_pass")
def change_pass():
    return  render_template("change_pass.html")

@app.route("/changing_pass",methods=['GET','POST'])
def changing_pass():
    try:
        if request.method=='POST':
            Roll=request.form.get('Roll')
            curr_pass=request.form.get('current_pass')
            passw=request.form.get('pass')
            new_passw=request.form.get('new_pass')
            query = "SELECT password FROM data WHERE Roll = %s"
            cursor=db_conn.cursor()
            cursor.execute(query, (Roll))
            original_pass = cursor.fetchone()
            if curr_pass==original_pass[0]:
                if(passw==new_passw):
                    query = "UPDATE data SET password = %s WHERE Roll = %s"
                    cursor.execute(query, (passw, Roll))
                    db_conn.commit()
            return render_template("student_login.html")
    except Exception as e:
        return str(e)
    
        
@app.route("/student_page",methods=['GET','POST'])
def student_page():
    try:
        if request.method=='POST':
            student_user_name=request.form.get('username')
            passw=request.form.get('pass')
            cursor=db_conn.cursor()
            query = "SELECT Roll FROM data WHERE Roll = %s"
            cursor.execute(query, (student_user_name,))
            result = cursor.fetchone()
            if result:
                query = "SELECT password FROM data WHERE Roll = %s"
                cursor.execute(query, (student_user_name))
                original_pass = cursor.fetchone()[0]
                if passw==original_pass:
                    user = {
                    'User': student_user_name,
                    'Password': passw
                    }
                    session['user'] = user
                    return redirect('/protected_student')
    except Exception as e:
        return str(e)
    return  render_template("student_login.html")


@app.route("/protected_student")
def protected_student():
    try:
        user = session.get('user')
        if user:
            cursor=db_conn.cursor()
            query = "SELECT * FROM data WHERE Roll = %s"
            cursor.execute(query, (user['User']))
            result = cursor.fetchone()
            return render_template("student_page.html",roll=result[0],name=result[1],gname=result[2],dob=result[3],address=result[5],tenth=result[6],inter=result[7],mobile=result[8],image_url=result[9])
        else:
            return "Access denied."
    except Exception as e:
        return str(e)


@app.route("/student_logout")
def student_logout():
    session.pop('user', None)
    return  render_template("index.html")


@app.route("/add",methods=['GET','POST'])
def displayaddemp():
    try:
        if request.method=='POST':
            user = session.get('user')
            if user:
                name=request.form.get('name')
                gname=request.form.get('G-name')
                dob=request.form.get('dob')
                password =str(dob)
                address=request.form.get('address')
                tenth=request.form.get('10th')
                inter=request.form.get('inter')
                mobile=request.form.get('mobile')
                file = request.files['img_file']
                insert_sql="INSERT INTO data VALUES (NULL,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                cursor=db_conn.cursor()
                try:
                    if file:
                        filename = file.filename
                        s3_bucket = S3.Bucket(custombucket)
                        s3_object = s3_bucket.Object(filename)
                        s3_object.upload_fileobj(file, ExtraArgs={'ACL': 'public-read'})
                        image_url = f"https://{custombucket}.s3.amazonaws.com/{filename}"
                    try:
                        cursor.execute(insert_sql,(name,gname,dob,password,address,tenth,inter,mobile,image_url))
                        db_conn.commit()
                        query = "SELECT MAX(Roll) FROM data"
                        cursor.execute(query)
                        Rollno = cursor.fetchone()[0]
                    except Exception as a:
                        return str(a)
                except Exception as e:
                    return str(e)
                finally:
                    cursor.close()
                print("all Done")
    
                return render_template("registration_completed.html", name=name,roll=Rollno,image_url=image_url)
            else:
                return "Access denied."
    except Exception as e:
        return str(e)
        

if __name__=="__main__":
    app.run(debug=True)