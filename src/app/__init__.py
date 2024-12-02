from flask import Flask
from app.system.routes import system_bp
from app.dataset.routes import dataset_bp
from app.model.routes import model_bp
from app.tree.routes import tree_bp
from app.user.routes import user_bp

def create_app():
    app = Flask(__name__, static_folder='../static')

    API_PREFIX = '/api/v1'

    # Register blueprints
    app.register_blueprint(system_bp, url_prefix=f'{API_PREFIX}/system')
    app.register_blueprint(dataset_bp, url_prefix=f'{API_PREFIX}/dataset')
    app.register_blueprint(model_bp, url_prefix=f'{API_PREFIX}/model')
    app.register_blueprint(tree_bp, url_prefix=f'{API_PREFIX}/tree')
    app.register_blueprint(user_bp, url_prefix=f'{API_PREFIX}/user')

    @app.errorhandler(404)
    def page_not_found(error):
        return app.send_static_file('404.html')

    # Index Page
    @app.route('/')
    def index():
        return app.send_static_file('index.html')
    
    # Serve static files
    @app.route('/<path:filename>')
    def serve_static(filename):
        return app.send_static_file(filename)
    
    @app.route('/dashboard')
    def dashboard():
        return app.send_static_file('dashboard.html')

    @app.route('/get-started')
    def get_started():
        return app.send_static_file('get-started.html')

    @app.route('/settings')
    def settings():
        return app.send_static_file('settings.html')

    @app.route('/train-status')
    def train_status():
        return app.send_static_file('train-status.html')

    return app
