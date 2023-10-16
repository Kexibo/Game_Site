import flask
from flask import Flask, render_template, url_for, request, redirect, session, flash
from flask_mail import Mail
from sqlalchemy.dialects.postgresql import psycopg2
import hashlib
from functions import resize_and_convert_to_jpg, profile_photo
import base64
from flask import Flask, request, logging
import psycopg2
import logging
from datetime import datetime


def get_pg_connect():
    conn = psycopg2.connect(host='localhost', port=3434, database='flask', user='admin', password='change_me', )
    return conn


app = Flask(__name__)

app.config["SECRET_KEY"] = 'bc72183212182182171232192137ab98798799869faffa9q6969fa69f69v8s9'
app.config["JSON_AS_ASCII"] = True
app.config["MAIL_SERVER"] = 'smpt.gmail.com'
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = 'моя почта'
app.config["MAIL_PASSWORD"] = 'мой пароль'

mail = Mail(app)


@app.route('/')
def index():
    if 'data' in session:
        data = session['data']
        print(data.get('roll'))

        try:
            conn = get_pg_connect()
            cur = conn.cursor()

            if data.get('roll') == 'customer':
                cur.execute(
                    f"""SELECT username FROM {data.get('roll')} WHERE id = %s""", (str(data['id'])))
            else:
                cur.execute(
                    f"""SELECT username FROM {data.get('roll')} WHERE id = %s""", (str(data['id'])))

            username = cur.fetchone()[0] if cur.rowcount > 0 else None
            conn.close()

            return render_template('index.html', username=username)

        except Exception as ex:
            logging.error(ex, exc_info=True)
            conn.rollback()
            conn.close()

    return render_template('index.html')


@app.route('/authors')
def authors():
    # conn = get_pg_connect()
    # cur = conn.cursor()
    # try:
    #     cur.execute(
    #         """SELECT id, user_id, title, date_created, photo_data FROM users
    #         ORDER BY photo_data is not null desc, date_created desc, date_created desc """)
    # except Exception as ex:
    #     logging.error(ex, exc_info=True)
    #     conn.rollback()
    #     conn.close()
    #     return "Ошибка при получении статей из базы данных"

    return render_template('authors.html')


@app.route('/orders/<skill>')
def orders_skill(skill):
    conn = get_pg_connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT id, title, description, price, date, customer_id, skill, status FROM orders where skill = %s and status = %s""",
            (skill, True))

        orders_list = []
        for order in cur.fetchall():
            id, title, description, price, date_created, customer_id, skill, status = order
            formatted_date = datetime.strftime(date_created, '%d-%m-%Y')
            orders_list.append({
                'id': id,
                'title': title,
                'description': description,
                'price': price,
                'date_created': formatted_date,
                'customer_id': customer_id,
                'skill': skill,
                'status': status,
            })
        cur.execute("""SELECT count(*) FROM orders where skill = %s and status = %s""",
                    (skill, True))

        return render_template('orders.html', orders=orders_list, count=cur.fetchone()[0])

    except Exception as ex:
        logging.error(ex, exc_info=True)
        conn.rollback()
        conn.close()
        return "Ошибка при получении заказов из базы данных"


@app.route('/order/<id>')
def order(id):
    conn = get_pg_connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT o.id, title, price, c.rating, data, c.data, full_description, skill, c.username FROM orders o
join customer c on o.customer_id = c.id 
WHERE o.id = %s""", (id,))
        result = cur.fetchone()
        formatted_date = datetime.strftime(result[4], '%d-%m-%Y')
        order_dict = {
            'id': result[0],
            'title': result[1],
            'price': result[2],
            'rating': result[3],
            'date_created': formatted_date,
            'data_reg': result[5],
            'full_description': result[6],
            'skill': result[7],
            'username': result[8],
        }
        return render_template('order.html', order=order_dict)
    except Exception as ex:
        logging.error(ex, exc_info=True)
        conn.rollback()
        conn.close()
        return "Ошибка при получении заказов из базы данных"

    finally:
        cur.close()
        conn.close()


@app.route('/orders')
def orders():
    conn = get_pg_connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT id, title, description, price, date, customer_id, skill, status FROM orders""")

        orders_list = []
        for order in cur.fetchall():
            id, title, description, price, date_created, customer_id, skill, status = order

            # Format the date as 'dd-mm-yyyy'
            formatted_date = datetime.strftime(date_created, '%d-%m-%Y')

            orders_list.append({
                'id': id,
                'title': title,
                'description': description,
                'price': price,
                'date_created': formatted_date,
                'customer_id': customer_id,
                'skill': skill,
                'status': status,
            })
        cur.execute("""SELECT count(*) FROM orders""")

        return render_template('orders.html', orders=orders_list, count=cur.fetchone()[0])

    except Exception as ex:
        logging.error(ex, exc_info=True)
        conn.rollback()
        conn.close()
        return "Ошибка при получении заказов из базы данных"

    finally:
        cur.close()
        conn.close()


@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    return f"hello {username}"


@app.route('/articles', methods=['GET'])
def articles():
    conn = get_pg_connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT id, user_id, title, date_created, photo_data FROM articles 
            ORDER BY photo_data is not null desc, date_created desc, date_created desc """)

        articles_list = []
        for article in cur.fetchall():
            article_id, user_id, title, date_created, photo_data = article
            if photo_data is not None:
                photo_data_base64 = base64.b64encode(photo_data).decode()
            else:
                photo_data_base64 = None

            articles_list.append({
                'article_id': article_id,
                'user_id': user_id,
                'title': title,
                'date_created': str(date_created)[:11],
                'photo_data_base64': photo_data_base64
            })

        return render_template('articles.html', articles=articles_list)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        conn.rollback()
        conn.close()
        return "Ошибка при получении статей из базы данных"


@app.route('/signin', methods=['POST', 'GET'])
def sign_in():
    if session.get('data'):
        return redirect('/')
    else:
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            roll = request.form.get('roll')

            conn = get_pg_connect()
            cur = conn.cursor()

            try:
                if roll != 'customer':
                    cur.execute(
                        f"SELECT id, username, first_name, last_name, email, data, rating, password, photo FROM {roll} WHERE email = %s",
                        (email,))
                else:
                    cur.execute(
                        f"SELECT id, username, first_name, last_name, email, data, rating, password, photo FROM {roll} WHERE email = %s",
                        (email,))

                user = cur.fetchone()

                if user and user[4] and hashlib.sha224(password.encode()).hexdigest() == user[7]:
                    if user[8]:
                        photo_data_base64 = base64.b64encode(user[2]).decode()
                        session['data'] = {"id": user[0], 'photo': photo_data_base64, "roll": roll}
                    else:
                        session['data'] = {"id": user[0], "photo": None, "roll": roll}

                    conn.close()
                    return redirect('/')
                else:
                    flash("Пароль не верен")

            except Exception as ex:
                logging.error(ex, exc_info=True)
                flash("Произошла ошибка при входе. Пожалуйста, попробуйте снова позже.")

            finally:
                conn.close()

    return render_template("sign_in.html")


@app.route('/signup', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        sub_password = request.form.get('sub_password')

        if password != sub_password:
            return render_template('sign_up.html')

        password_hash = hashlib.sha224(password.encode()).hexdigest()
        roll = request.form.get('roll')

        conn = get_pg_connect()
        cur = conn.cursor()

        try:
            cur.execute(f"SELECT email FROM {roll}")
            existing_emails = [row[0] for row in cur.fetchall()]

            if email in existing_emails:
                conn.close()
                return render_template('sign_up.html', email_exists=True)

            cur.execute(
                f"""INSERT INTO {roll} (username, email, password, first_name, last_name) VALUES (%s, %s, %s, %s, %s)""",
                (username, email, password_hash, first_name, last_name))

            conn.commit()
            conn.close()

            return redirect('/signin')
        except Exception as ex:
            logging.error(ex, exc_info=True)
            conn.rollback()
            conn.close()
            return f"Error: {ex}"

    return render_template('sign_up.html')


@app.route('/best_articles', methods=['GET', 'POST'])
def best_articles():
    names = ["OLEG", "Виталик", "ЯНА", "ХЗ", ]

    return render_template('best_articles.html', names=names)


@app.route('/p', methods=['GET', 'POST'])
def p():
    if request.method == 'POST':
        photo = request.files['photo']

        if photo:
            photo_data = photo.read()
            conn = get_pg_connect()

            cursor = conn.cursor()
            try:
                jpg_data = resize_and_convert_to_jpg(photo_data)

                cursor.execute(
                    "UPDATE articles SET photo_data = %s WHERE id = 3",
                    (jpg_data,)
                )

                conn.commit()
                conn.close()
            except Exception as ex:
                logging.error(ex, exc_info=True)
                conn.rollback()
                conn.close()
                return f"Error:"

    return render_template('photo.html')


@app.route('/pp', methods=['GET', 'POST'])
def pp():
    if request.method == 'POST':
        photo = request.files['photo']

Игнат, [02.10.2023 23:45]


        if photo:
            photo_data = photo.read()
            conn = get_pg_connect()
            cursor = conn.cursor()
            try:
                jpg_data = profile_photo(photo_data)

                cursor.execute(
                    "UPDATE users SET photo = %s WHERE id = 4",
                    (jpg_data,)
                )

                conn.commit()
                conn.close()
            except Exception as ex:
                logging.error(ex, exc_info=True)
                conn.rollback()
                conn.close()
                return f"Error:"

    print(123)

    return render_template('photo.html')


@app.route('/profile_executor', methods=['GET', 'POST'])
def profile_executor():
    return render_template('profile_executor.html')


@app.route('/profile_customer', methods=['GET', 'POST'])
def profile_customer():
    if session.get('data'):
        data = session.get('data')
        conn = get_pg_connect()
        cur = conn.cursor()
        try:
            cur.execute(
                """SELECT username, email, first_name, last_name from customer 
WHERE c.id = %s""",
                (str(data['id'])))
            result = cur.fetchone()
            user_data = {
                'username': result[0],
                'email': result[1],
                'first_name': result[2],
                'last_name': result[3],
            }
            print(123)
            cur.execute(
                """select title, description, price, date, skill, status from orders where customer_id = %s""",
                (str(data['id'])))

            orders_list = []
            for order in cur.fetchall():
                title, description, price, date_created,  skill, status = order

                formatted_date = datetime.strftime(date_created, '%d-%m-%Y')

                orders_list.append({
                    'title': title,
                    'description': description,
                    'price': price,
                    'date_created': formatted_date,
                    'skill': skill,
                    'status': status,
                })

            return render_template('profile_customer.html', user=user_data, orders=orders_list)
        except Exception as ex:
            logging.error(ex, exc_info=True)
            conn.rollback()
            conn.close()
            return render_template('index.html')

    return render_template('index.html')


@app.route('/del_session')
def del_session():
    session.pop('data', None)
    return redirect('/')


@app.route('/article/<id>', methods=['GET', 'POST'])
def article(id):
    conn = get_pg_connect()
    cur = conn.cursor()
    try:
        cur.execute(
            """SELECT title, description, rating, date_created, photo_data FROM articles WHERE id = %s""", (id,))
        result = cur.fetchone()
        if result[4] is not None:
            photo_data_base64 = base64.b64encode(result[4]).decode()
        else:
            photo_data_base64 = None
        article_dict = {
            'title': result[0],
            'description': result[1],
            'rating': result[2],
            'date_created': result[3],
            'photo': photo_data_base64}

        return render_template('article.html', article=article_dict)

    except Exception as ex:
        logging.error(ex, exc_info=True)
        conn.rollback()
        conn.close()
        return "Ошибка при получении статей из базы данных"


@app.route('/111')
def testtt():
    return render_template('page.html')


@app.route('/333')
def testttt():
    return render_template('Authors.html')


if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)