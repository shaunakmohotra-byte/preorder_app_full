from flask import Flask
from .store import init_default_data

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your-secure-key-here'
    
    # 1. Initialize the JSON files so they aren't missing
    init_default_data()

    # 2. Register all your blueprints
    from .routes import bp as main_bp
    from .auth import bp as auth_bp
    from .admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
