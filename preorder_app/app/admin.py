from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .store import load_json, save_json, ITEMS_FILE, USERS_FILE, ORDERS_FILE
from .store import load_json as _load
import uuid
bp = Blueprint('admin', __name__,)

def current_user():
    uid = session.get('user_id')
    if not uid: return None
    users = _load(USERS_FILE, [])
    for u in users:
        if u['id'] == uid: return u
    return None

def admin_required():
    u = current_user()
    return u and u.get('is_admin')

@bp.route('/')
def index():
    if not admin_required(): flash('Admin access required'); return redirect(url_for('auth.login'))
    users = _load(USERS_FILE, []); items = _load(ITEMS_FILE, []); orders = _load(ORDERS_FILE, [])
    return render_template('admin.html', users=users, items=items, orders=orders, user=current_user())

@bp.route('/add_item', methods=['POST'])
def add_item():
    if not admin_required():
        flash('Admin access required')
        return redirect(url_for('auth.login'))

    name = request.form['name']
    price = int(request.form['price'])

    items = _load(ITEMS_FILE, [])
    # create new item with unique ID
    new_item = {
        'id': str(uuid.uuid4()),
        'name': name,
        'price': price
    }
    items.append(new_item)
    save_json(ITEMS_FILE, items)

    flash(f'Item "{name}" added successfully')
    return redirect(url_for('admin.index'))



@bp.route('/delete_item', methods=['POST'])
def delete_item():
    if not admin_required(): flash('Admin access required'); return redirect(url_for('auth.login'))
    item_id = request.form['item_id']; items = _load(ITEMS_FILE, []); items = [it for it in items if it['id']!=item_id]; save_json(ITEMS_FILE, items)
    flash('Deleted'); return redirect(url_for('admin.index'))

@bp.route('/edit_user/<user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if not admin_required():
        flash('Admin access required')
        return redirect(url_for('auth.login'))

    users = _load(USERS_FILE, [])

    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        flash('User not found')
        return redirect(url_for('admin.index'))

    if request.method == 'POST':
        user['username'] = request.form['username']
        user['email'] = request.form['email']
        user['is_admin'] = True if request.form.get('is_admin') else False

        save_json(USERS_FILE, users)
        flash('User updated successfully')
        return redirect(url_for('admin.index'))

    return render_template('edit_user.html', user=user)


@bp.route('/delete_user', methods=['POST'])
def delete_user():
    if not admin_required():
        flash('Admin access required')
        return redirect(url_for('auth.login'))

    user_id = request.form['user_id']

    users = _load(USERS_FILE, [])
    users = [u for u in users if u['id'] != user_id]

    save_json(USERS_FILE, users)
    flash('User deleted successfully')

    return redirect(url_for('admin.index'))
