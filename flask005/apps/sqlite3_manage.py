import os
import sqlite3

from flask import g

from apps import app
from apps.model import User


def connect_db():
    """Connects to the specific database."""
    # print(app.config["DATABASE"])
    db = sqlite3.connect(app.config['DATABASE'])
    return db


def init_db():
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.before_request
def before_request():
    # print('before_request()')
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        # print('teardown_request()')
        g.db.close()


def insert_user_to_db(user):
    # sql_insert = "INSERT INTO users (name,pwd,email,age,birthday,face) VALUES (?, ?, ?, ?, ?, ?)"
    user_attrs = user.getAttrs()
    values = " VALUES ("
    last_attr = user_attrs[-1]
    for attr in user_attrs:
        if attr != last_attr:
            values += " ?,"
        else:
            values += " ?"
    values += " )"
    sql_insert = "INSERT INTO users" + str(user_attrs) + values
    args = user.toList()
    g.db.execute(sql_insert, args)
    g.db.commit()


def query_users_from_db():
    users = []
    sql_select = "SELECT * FROM users"
    args = []
    cur = g.db.execute(sql_select, args)
    for item in cur.fetchall():
        user = User()
        user.fromList(item[1:])
        users.append(user)
    return users


def query_user_by_name(user_name):
    sql_select = "SELECT * FROM users where name=?"
    args = [user_name]
    cur = g.db.execute(sql_select, args)
    items = cur.fetchall()
    if len(items) < 1:
        return None
    first_item = items[0]
    user = User()
    user.fromList(first_item[1:])
    return user


def delete_user_by_name(user_name):
    delete_sql = "DELETE FROM users WHERE name=?"
    args = [user_name]
    g.db.execute(delete_sql, args)
    g.db.commit()


def update_user_by_name(old_name, user):
    update_str = ""
    user_attrs = user.getAttrs()
    last_attr = user_attrs[-1]
    for attr in user_attrs:
        if attr != last_attr:
            update_str += attr + " = ?,"
        else:
            update_str += attr + " = ?"
    sql_update = "UPDATE users SET " + update_str + " WHERE name = ?"
    args = user.toList()
    args.append(old_name)
    g.db.execute(sql_update, args)
    g.db.commit()


if __name__ == "__main__":
    print("sqlite3: ", os.getcwd())
    init_db()
