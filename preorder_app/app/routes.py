from email.message import EmailMessage
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .store import load_json, save_json, ITEMS_FILE, CARTS_FILE, ORDERS_FILE, USERS_FILE
import datetime, uuid
import os
import json
import smtplib

bp = Blueprint('main', __name__,)


# -----------------------
# Helper Functions
# -----------------------

def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    
    users = load_json(USERS_FILE, [])
    return next((u for u in users if u['id'] == uid), None)


def load_orders():
    try:
        data = load_json(ORDERS_FILE, [])
        if isinstance(data, list):
            return data
        else:
            return []     # safety reset
    except:
        return []

def save_orders(data):
    save_json(ORDERS_FILE, data)



def save_orders(data):
    return save_json(ORDERS_FILE, data)


from utils.repair import repair_json

def load_json(path, default):
    # Repair automatically and return repaired content
    repaired = repair_json(path, type(default))
    return repaired

def send_order_email(user_email, user_name, order):
    msg = EmailMessage()
    msg["Subject"] = "Cafeteria Order Confirmation"
    msg["From"] = SMTP_EMAIL
    msg["To"] = user_email

    body = f"""
Hi {user_name},

Your order has been successfully placed.

Order ID: {order['id']}
Total Amount: ₹{order['total']}

Items:
"""

    for item in order["items"]:
        body += f"- {item['name']} × {item['qty']} (₹{item['price']})\n"

    body += "\nThank you for ordering!\nCafeteria Team"

    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)


# -----------------------
# Main Routes
# -----------------------

@bp.route('/')
def index():
    return redirect(url_for('main.menu'))


@bp.route('/menu')
def menu():
    items = load_json(ITEMS_FILE, [])
    return render_template('menu.html', items=items, user=current_user())


@bp.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user = current_user()
    if not user:
        flash('Please login to add to cart')
        return redirect(url_for('auth.login'))

    item_id = request.form['item_id']
    qty = int(request.form.get('qty', 1))

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    existing = next((c for c in user_cart if c['item_id'] == item_id), None)
    if existing:
        existing['qty'] += qty
    else:
        user_cart.append({'item_id': item_id, 'qty': qty})

    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    flash('Added to cart')
    return redirect(url_for('main.menu'))


@bp.route('/cart')
def view_cart():
    user = current_user()
    if not user:
        flash('Login to view cart')
        return redirect(url_for('auth.login'))

    carts = load_json(CARTS_FILE, {})
    items = {i['id']: i for i in load_json(ITEMS_FILE, [])}
    user_cart = carts.get(user['id'], [])

    cart_details = []
    total = 0

    for c in user_cart:
        it = items.get(c['item_id'])
        if not it:
            continue
        subtotal = it['price'] * c['qty']
        total += subtotal
        cart_details.append({
            'item': it,
            'qty': c['qty'],
            'subtotal': subtotal
        })

    return render_template('cart.html', cart_details=cart_details, total=total, user=user)


@bp.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user = current_user()
    if not user:
        return redirect(url_for('auth.login'))

    item_id = request.form['item_id']

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    user_cart = [c for c in user_cart if c['item_id'] != item_id]
    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    flash('Removed')
    return redirect(url_for('main.view_cart'))

@bp.route('/cart/increase', methods=['POST'])
def cart_increase():
    user = current_user()
    if not user:
        return redirect(url_for('auth.login'))

    item_id = request.form['item_id']

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    for c in user_cart:
        if c['item_id'] == item_id:
            c['qty'] += 1
            break

    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    return redirect(url_for('main.view_cart'))


@bp.route('/cart/decrease', methods=['POST'])
def cart_decrease():
    user = current_user()
    if not user:
        return redirect(url_for('auth.login'))

    item_id = request.form['item_id']

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    for c in user_cart:
        if c['item_id'] == item_id:
            if c['qty'] > 1:
                c['qty'] -= 1
            else:
                # If quantity becomes 0, remove it
                user_cart = [x for x in user_cart if x['item_id'] != item_id]
            break

    carts[user['id']] = user_cart
    save_json(CARTS_FILE, carts)

    return redirect(url_for('main.view_cart'))


@bp.route('/checkout')
def checkout():
    user = current_user()
    if not user:
        flash('Login to checkout')
        return redirect(url_for('auth.login'))

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    if not user_cart:
        flash('Cart empty')
        return redirect(url_for('main.view_cart'))

    items = {i['id']: i for i in load_json(ITEMS_FILE, [])}

    cart_details = []
    total = 0

    for c in user_cart:
        it = items.get(c['item_id'])
        if not it:
            continue
        subtotal = it['price'] * c['qty']
        total += subtotal
        cart_details.append({
            'name': it['name'],
            'price': it['price'],
            'qty': c['qty'],
            'subtotal': subtotal
        })

    return render_template(
        "checkout.html",
        cart_details=cart_details,
        total=total,
        user=user
    )


@bp.route('/pay_now', methods=['POST'])
def pay_now():
    user = current_user()
    if not user:
        return redirect(url_for('auth.login'))

    carts = load_json(CARTS_FILE, {})
    user_cart = carts.get(user['id'], [])

    if not user_cart:
        flash("Cart empty")
        return redirect(url_for('main.menu'))

    items = {i['id']: i for i in load_json(ITEMS_FILE, [])}

    order_items = []
    total = 0

    for c in user_cart:
        it = items.get(c['item_id'])
        if not it:
            continue
        order_items.append({
            'item_id': it['id'],
            'name': it['name'],
            'price': it['price'],
            'qty': c['qty']
        })
        total += it['price'] * c['qty']

    order = {
        'id': str(uuid.uuid4()),
        'user_id': user['id'],
        'user_name': user['name'],
        'items': order_items,
        'total': total,
        'status': 'paid',
        'created_at': datetime.datetime.utcnow().isoformat()
    }

    orders = load_orders()
    orders.append(order)
    save_orders(orders)

    carts[user['id']] = []        # EMPTY CART
    save_json(CARTS_FILE, carts)

    flash("Payment successful")
    return redirect(url_for('main.menu'))
db_user = get_user_by_id(user["id"])

if db_user and db_user.get("email"):
    try:
        send_order_email(
            user_email=db_user["email"],
            user_name=db_user["name"],
            order=order
        )
    except Exception as e:
        print("SMTP email failed:", e)


@bp.route('/cafeteria')
def cafeteria():
    orders = load_orders()

    # HARD SAFETY CHECK
    if not isinstance(orders, list):
        orders = []

    return render_template("cafeteria.html", orders=orders)


@bp.route('/cafeteria/mark_paid/<order_id>', methods=['POST'])
def mark_order_paid(order_id):
    orders = load_orders()
    orders = [o for o in orders if o['id'] != order_id]
    save_orders(orders)
    flash("Order marked as delivered & paid")
    return redirect(url_for('main.cafeteria'))