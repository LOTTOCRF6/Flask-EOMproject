
import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def init_user_login_table():
    conn = sqlite3.connect('blog.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS user_login(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL,"
                 "address TEXT NOT NULL,"
                 "phone TEXT NOT NULL,"
                 "email TEXT NOT NULL)")
    print("user table created successfully")
    conn.close()


init_user_login_table()


def init_post_table():
    with sqlite3.connect('blog.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Login (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "user_email TEXT NOT NULL,"
                     "password TEXT NOT NULL,"
                     "login_date TEXT NOT NULL)")
    print("Login table created successfully.")


init_post_table()
#init_user_login_table()


def product_table():
    with sqlite3.connect('blog.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Products (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL, quantity TEXT NOT NULL)")
    print("Products table created successfully.")


product_table()


def fetch_users():
    with sqlite3.connect('blog.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_login")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


users = fetch_users()


username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/user-registration/', methods=["POST"])
def user_registration():
    response = {}
    if request.method == "POST":

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        phone = request.form['phone']
        email = request.form['email']

        with sqlite3.connect("blog.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO user_login("
                           "first_name,"
                           "last_name,"
                           "username,"
                           "password,"
                           "address,"
                           "phone,"
                           "email) VALUES(?, ?, ?, ?, ?, ?, ?)", (first_name, last_name, username, password, address, phone, email))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
        return response


@app.route('/create-blog/', methods=["POST"])
def create_blog():
    response = {}

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']
        date_created = datetime.datetime.now()

        with sqlite3.connect('blog.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO post("
                           "title,"
                           "content,"
                           "date_created) VALUES(?, ?, ?)", (title, content, date_created))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Blog post added successfully"
        return response


@app.route('/get-blogs/', methods=["GET"])
def get_blogs():
    response = {}
    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM post")

        posts = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = posts
    return response


@app.route("/delete-post/<int:post_id>")
def delete_post(post_id):
    response = {}
    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM post WHERE id=" + str(post_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "blog post deleted successfully."
    return response


@app.route('/edit-post/<int:post_id>/', methods=["PUT"])
def edit_post(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('blog.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("title") is not None:
                put_data["title"] = incoming_data.get("title")
                with sqlite3.connect('blog.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE post SET title =? WHERE id=?", (put_data["title"], post_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
            if incoming_data.get("content") is not None:
                put_data['content'] = incoming_data.get('content')

                with sqlite3.connect('blog.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE post SET content =? WHERE id=?", (put_data["content"], post_id))
                    conn.commit()

                    response["content"] = "Content updated successfully"
                    response["status_code"] = 200
    return response


@app.route('/get-post/<int:post_id>/', methods=["GET"])
def get_post(post_id):
    response = {}

    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM post WHERE id=" + str(post_id))

        response["status_code"] = 200
        response["description"] = "Blog post retrieved successfully"
        response["data"] = cursor.fetchone()

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)