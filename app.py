from flask import Flask, render_template, url_for, request, redirect, make_response, session, flash, render_template_string
import hashlib
from time import sleep
import os
from flask_mail import Mail, Message
from dotenv import load_dotenv

load_dotenv()

from models import User, db

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
db.init_app(app)

mail = Mail(app)

@app.route('/index')
@app.route('/home')
@app.route('/')
def index():
    return render_template("index.html")


@app.route('/account', methods=['POST', 'GET'])
def account():
    if request.method == 'POST' and request.form.get('1') == 'Accept':
        flash('Вы приняли запрос "accept"! Ура')
    elif request.method == 'POST' and request.form.get('2') == 'NoAccept':
        flash('Вау вау вау')
    return render_template("account.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/user/<username>')
def get_user(username):
    return f"Hello {username}"


@app.route('/signin', methods=['POST', 'GET'])
def signin():
    if session.get('data'):
        return redirect('/')
    else:
        if request.method == 'POST':
            email = request.form.get('username')
            password = request.form.get('password')
            try:
                user = User.query.filter(User.email == email).one()

                if user and hashlib.sha224(password.encode()).hexdigest() == user.password:
                    session['data'] = {'id': user.id, 'name': user.username, 'email': user.email}
                    return redirect("/")
                else:
                    return flash("Неверный логин или пароль")
            except:
                return redirect("/error")
    return render_template("signin.html")


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password = hashlib.sha224(password.encode()).hexdigest()
        new_user = User(email=email, username=username, password=password)
        try:
            db.session.add(new_user)
            db.session.commit()
        except:
            flash("Виталя что-то ту не так")
        return redirect("/signin")
    return render_template("signup.html")


@app.route('/news')
def news():
    return render_template("news.html")


@app.route('/goods')
def goods():
    return render_template("goods.html")


@app.route('/choose')
def choose():
    return render_template("choose.html")


@app.route("/contact",methods=["GET","POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("email")
        phone = request.form.get("phone")
        message = request.form.get("message")
        msg = Message("Вам поступило новое обращение на сайте",recipients=[name])
        msg.body = f"Клиент оставил номер телефона:{phone} и сообщение: {message}"
        mail.send(msg)
        return redirect('/thanks')
    else:
        return render_template("contact.html")


@app.route('/thanks')
def thanks():
    return render_template("thanks.html")


@app.route('/del_session')
def del_session():
    session.pop('data', None)
    return redirect('/')


@app.route('/error')
def error():
    return render_template("error.html")


@app.route('/trap')
def trap():
    return render_template("trap.html")


@app.route('/ogon_i_voda')
def ogon_i_voda():
    return render_template("games/ogon_i_voda.html")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
