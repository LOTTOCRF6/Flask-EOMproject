
import hmac
import sqlite3
import datetime

from flask import Flask, request, jsonify
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS
from flask_mail import Mail, Message


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


def init_product_table():
    with sqlite3.connect('blog.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS Product_create (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "product_image TEXT NOT NULL,"
                     "description TEXT NOT NULL)")
    print("Products_create table created successfully.")


init_product_table()


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


# app.config['MAIL_SERVER'] = 'smtp.gmail.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'sithandathuzipho@gmail.com'
# app.config['MAIL_PASSWORD'] = 'Crf6ZS@#'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True
# mail = Mail(app)


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

            # msg = Message('WELCOME', sender='sithandathuzipho@gmail.com', recipients=['sithandathuzipho@gmail.com'])
            # msg.body = "You have successfully registered"
            # mail.send(msg)
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


@app.route('/create-products/', methods=["POST"])
def create_product():
    response = {}

    if request.method == "POST":
        product_name = request.form['product_name']
        price = request.form['price']
        product_image = request.form['product_image']
        description = request.form['description']
        with sqlite3.connect('blog.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Product_create("
                           "product_name,"
                           "price,"
                           "product_image,"
                           "description) VALUES(?, ?, ?, ?)", (product_name, price, product_image, description))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "products created successfully"
        return response


@app.route('/Get-Products/', methods=["GET"])
def get_Point_of_Sales():
    response = {}
    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row
        cursor.execute("SELECT * FROM Product_create")
        deals = cursor.fetchall()
        deal_acc = []
        for i in deals:
            deal_acc.append({x: i[x] for x in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(deal_acc)
    return response


@app.route('/products/')
def show_products():
    products = [{'id': 1, 'Product_name': 'Dead Line', 'Price:' '5000,' 'Description': 'Great level of a usb'}]
    return jsonify(products)


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


@app.route("/delete-products/<int:post_id>")
def delete_post(post_id):
    response = {}
    with sqlite3.connect("blog.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Product_create WHERE id=" + str(post_id))
        conn.commit()
        response['status_code'] = 200
        response['message'] = "products deleted successfully."
    return response


@app.route('/edit-post/<int:post_id>/', methods=["PUT"])
def edit_post(post_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('blog.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("product_name") is not None:
                put_data["product_name"] = incoming_data.get("product_name")
                with sqlite3.connect('blog.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Product_create SET product_name =? WHERE id=?", (put_data["product_name"], post_id))
                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200
            if incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('blog.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Product_create SET price =? WHERE id=?", (put_data["price"], post_id))
                    conn.commit()

                    response["price"] = "Price updated successfully"
                    response["status_code"] = 200
            if incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('blog.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Product_create SET description =? WHERE id=?", (put_data["description"], post_id))
                    conn.commit()

                    response["description"] = "Description updated successfully"
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