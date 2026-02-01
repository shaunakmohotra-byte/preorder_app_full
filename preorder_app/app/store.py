# Simple JSON storage layer (file-based "memory")
import os, json, uuid, datetime
from werkzeug.security import generate_password_hash
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ITEMS_FILE = os.path.join(DATA_DIR, 'items.json')
CARTS_FILE = os.path.join(DATA_DIR, 'carts.json')
ORDERS_FILE = os.path.join(DATA_DIR, 'orders.json')

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def load_json(path, default):
    ensure_data_dir()
    if not os.path.exists(path):
        with open(path, 'w') as f:
            json.dump(default, f, indent=2)
        return default
    with open(path, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default

def save_json(path, data):
    ensure_data_dir()
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def init_default_data():
    users = load_json(USERS_FILE, [])
    if not any(u.get('email') == 'admin@example.com' for u in users):
        admin = {
            'id': str(uuid.uuid4()),
            'name': 'Admin',
            'email': 'admin@example.com',
            'password_hash': generate_password_hash('adminpass'),
            'is_admin': True
        }
        users.append(admin)
        save_json(USERS_FILE, users)
    items = load_json(ITEMS_FILE, [])
    if not items:
        items = [
            {'id': 'item1', 'name': 'Veg Burger', 'price': 70},
            {'id': 'item2', 'name': 'Chicken Sandwich', 'price': 120},
            {'id': 'item3', 'name': 'Coffee', 'price': 40},
        ]
        save_json(ITEMS_FILE, items)
    load_json(CARTS_FILE, {})
    load_json(ORDERS_FILE, [])
