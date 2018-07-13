#-*- coding: utf-8-*-
from flask import Flask, render_template, session, redirect, flash
from flask_wtf import Form
from wtforms import StringField, PasswordField, IntegerField
from wtforms.validators import InputRequired, Email, Length
import MySQLdb
import os

# Flask가 동작하기 위해서 필요한 기본 설정 들..
app = Flask(__name__)
app.config['SECRET_KEY'] = "HansClass"
app.secret_key = os.urandom(50)

# 아래 클래스의 각 필드의 validator가 만족되지 않았을 때 띄워줄 메세지가 필요함
# 입력 칸을 정의하는 클래스 선언
class LoginForm(Form):
    userid = StringField("username", validators=[InputRequired()])
    userpw = PasswordField("password", validators=[InputRequired()])

# 회원가입란을 정의하는 클래스 선언
class SignupForm(Form):
    name = StringField("name", validators=[InputRequired()])
    phone = StringField("phone", validators=[InputRequired()])
    email = StringField("email", validators=[InputRequired()])
    userid = StringField("username", validators=[InputRequired()])
    userpw = PasswordField("password", validators=[InputRequired()])
    pwconfirm = PasswordField("password", validators=[InputRequired()])
    school = StringField("school", validators=[InputRequired()])

# 레벨테스트란을 정의하는 클래스 선언
class QuestionForm(Form):
    answer = StringField("answer")

# DB 연동을 수행하는 함수
def connectDB():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="4swedu@skku", db="GT_DB",charset="utf8mb4")
    c = conn.cursor()
    return c, conn

# 로그인을 수행했을 때 세션을 생성하는 함수
def createSession(username):
    session['user'] = username

# 로그아웃 함수
def deleteSession():
    session.pop('user', None)

def createError(message):
    session['errmsg'] = message

def deleteError():
    session.pop('errmsg', None)

# 홈페이지 # 로그인 없이는 각 버튼 접근 권한 없애야함!
@app.route('/')
def homepage():
    if('user' in session):
        userid = session['user']
        c, conn = connectDB()
        c.execute("SELECT name FROM USERS WHERE userid = %s", (userid,))
        name = c.fetchone()[0]
        return render_template("index.html", name=name, flag = True)
    else:
        return render_template("index.html", name="NULL", flag = False)

@app.route('/oops')
def error():
    if('errmsg' in session): # 현재 무슨 에러가 발생했다면
        error = session['errmsg'] # 무슨 에러인지 메세지 갖고오고
    else: # 동작하는지 테스트용도.. 실제로 이 url 치고 들어오는 사람은 없을테니까
        error = "현재 오류가 없습니다!"
    # error 변수는 정상적으로 나옴
    return render_template("/admin/error.html", message = error)
    # 렌더링 정상적으로 잘되는데

@app.route('/deleteerror')
def testtest():
    deleteError()
    return redirect('/error')

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if(login_form.validate_on_submit()): # 로그인 버튼이 눌렸을 때 수행되는 코드
        c, conn = connectDB() # DB에 연결하고
        userid = login_form.userid.data # 입력받은 아이디와
        userpw = login_form.userpw.data # 비밀번호를 저장
        c.execute("SELECT userpw FROM USERS WHERE userid = %s", (userid,)) # 아이디를 사용하여 비밀번호를 DB에서 가져옴
        if(userpw == c.fetchone()[0]): # 입력한 비밀번호와 DB상의 비밀번호가 같다면
            createSession(userid) # 로그인이 완료된 상황이니 세션을 생성
            return redirect('/')
        else: # 입력한 비밀번호가 DB와 다르다면
            message = "아이디나 비밀번호가 틀렸습니다."
            createError(message)
            return redirect('/error')
    return render_template("/admin/login.html", form=login_form)

@app.route('/onlyformembers')
def onlyformembers():
    return render_template("/admin/onlyformembers.html")

@app.route('/logout')
def logout():
    deleteSession()
    return redirect('/')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    signup_form = SignupForm()
    if(signup_form.validate_on_submit()):
        if(signup_form.userpw.data != signup_form.pwconfirm.data):
            message = "비밀번호가 일치하지 않습니다."
            createError(message)
            return redirect('/error')
        else:
            c, conn = connectDB()
            c.execute("INSERT INTO USERS VALUES (%s, %s, %s, %s, %s, %s)", (signup_form.name.data, signup_form.userid.data, signup_form.userpw.data, signup_form.email.data, signup_form.phone.data, signup_form.school.data))
            conn.commit()
            conn.close()
            return redirect("/login")
    return render_template("/admin/signup.html", form = signup_form)

@app.route("/leveltest")
def leveltest():
    if('user' in session):
        userid = session['user']
        c, conn = connectDB()
        c.execute("SELECT name FROM USERS WHERE userid = %s", (userid,))
        name = c.fetchone()[0]
        return render_template("/assessments/leveltest.html", name=name, flag = True)
    else:
        return redirect("/onlyformembers")

@app.route('/abouttest')
def aboutleveltest():
    return render_template("/assessments/abouttest.html")

@app.route("/leveltest/<variable>")
def leveltest_category(variable):
    if('user' in session):
        category_list = ['thinking', 'entry', 'python', 'c']
        if(variable in category_list):
            return render_template("/assessments/questions/" + variable + "/start.html")
        else:
            qnum = int(variable[1:])
            if(qnum <= 25):
                category = "thinking"
            elif(qnum <= 50):
                category = "entry"
            elif(qnum <= 75):
                category = "python"
            else:
                category = "c"
            return render_template("/assessments/questions/" + category + "/Q"+ str(qnum) + ".html",)
    else:
        return redirect("/onlyformembers")
        

@app.route('/sensitiveinfo')
def sensitiveinfo():
    return render_template("/privacy/sensitiveinfo.html")

@app.route('/lecture')
def lecture():
    return render_template("lecture.html")



# Start
if(__name__ == "__main__"):
    app.run()
