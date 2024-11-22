from flask import Flask, render_template
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Config
    app.config['SECRET_KEY'] = 'dev-key-please-change'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///hal9000.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Root route
    @app.route('/')
    def index():
        return render_template('pages/index.html')
    
    # Register blueprints
    from .modules.system_control.routes import bp as system_bp
    from .modules.api_hub.routes import bp as api_hub_bp  # Changed from api_bp
    from .modules.terminal.routes import bp as terminal_bp
    from .modules.dashboard.routes import bp as dashboard_bp
    
    app.register_blueprint(system_bp, url_prefix='/system')
    app.register_blueprint(api_hub_bp, url_prefix='/api_hub')  # Changed URL prefix
    app.register_blueprint(terminal_bp, url_prefix='/terminal')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    
    return app