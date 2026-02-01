from flask import Flask
from .store import init_default_data

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-secret-key-123' # Required for sessions/flash

    # Ensure JSON files exist before the app starts
    init_default_data()

    # Register Blueprints
    from .routes import bp as main_bp
    from .auth import bp as auth_bp
    from .admin import bp as admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app
