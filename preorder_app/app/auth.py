from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from .store import load_json, save_json, USERS_FILE
import uuid
bp = Blueprint('auth', __name__,)

def current_user():
    uid = session.get('user_id')
    if not uid: return None
    users = load_json(USERS_FILE, [])
    for u in users:
        if u['id'] == uid:
            return u
    return None

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']; email = request.form['email']; pwd = request.form['password']
        users = load_json(USERS_FILE, [])
        if any(u['email'] == email for u in users):
            flash('Email already registered'); return redirect(url_for('auth.register'))
        u = {'id': str(uuid.uuid4()), 'name': name, 'email': email, 'password_hash': generate_password_hash(pwd), 'is_admin': False}
        users.append(u); save_json(USERS_FILE, users)
        flash('Registered. Please login.'); return redirect(url_for('auth.login'))
    return render_template('register.html', user=current_user())

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']; pwd = request.form['password']
        users = load_json(USERS_FILE, [])
        user = next((u for u in users if u['email']==email), None)
        if not user or not check_password_hash(user['password_hash'], pwd):
            flash('Invalid credentials'); return redirect(url_for('auth.login'))
        session['user_id'] = user['id']; flash('Logged in'); return redirect(url_for('main.menu'))
    return render_template('login.html', user=current_user())

@bp.route('/logout')
def logout():
    session.pop('user_id', None); flash('Logged out'); return redirect(url_for('main.menu'))
# auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash
import json, os

auth_bp = Blueprint('auth', __name__)

# Load users from data/users.json
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'users.json')

with open(DATA_PATH, 'r') as f:
    users = json.load(f)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.get(username)

        if user and check_password_hash(user["password"], password):
            session["username"] = username
            session["role"] = user.get("role", "student")
            return redirect(url_for('routes.menu'))

        flash("Invalid username or password")

    return render_template('login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
