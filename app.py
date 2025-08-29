import os
from flask import Flask, send_from_directory, render_template
from config import config
from extensions import db, migrate, login_manager, csrf, session, scheduler, redis_client
import redis


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(app.config['REDIS_URL'])
    app.config['SESSION_REDIS'] = redis_client
    
    # Initialize Session with explicit configuration
    session.init_app(app)
    
    # Create upload directories
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'food'), exist_ok=True)
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.onboarding import onboarding_bp
    from routes.settings import settings_bp
    from routes.coach import coach_bp
    from routes.admin import admin_bp
    from api.routes import api_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(onboarding_bp, url_prefix='/onboarding')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    app.register_blueprint(coach_bp, url_prefix='/coach')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Exempt API routes from CSRF protection
    csrf.exempt(api_bp)

    # Serve OpenAPI spec and Swagger UI
    @app.route('/openapi.yaml')
    def serve_openapi_spec():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return send_from_directory(base_dir, 'openapi.yaml', mimetype='application/yaml')

    @app.route('/api/docs')
    def swagger_ui():
        return render_template('swagger_ui.html')
    
    # User loader for Flask-Login
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))
    
    # Start background scheduler
    if not scheduler.running:
        scheduler.start()
    
    # Initialize reminder scheduler
    from services.reminder_scheduler import init_reminder_scheduler
    init_reminder_scheduler(scheduler)
    
    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        try:
            # Wait a bit for database to be ready
            import time
            time.sleep(2)
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")
            # Don't exit, let the app start anyway
    
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    print(f"Starting NutriCoach on port {port} (debug={debug_mode})")
    app.run(debug=debug_mode, host='0.0.0.0', port=port)