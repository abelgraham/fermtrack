from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db, User, Batch, BatchAction, FermentationStage
from auth import auth_bp
from batches import batches_bp
import os

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configure CORS
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000', 'https://fermtrack.com'])
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(batches_bp)
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'error': 'Authentication token required'}), 401
    
    # Health check endpoint
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'FermTrack API is running'
        }), 200
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return jsonify({
            'name': 'FermTrack API',
            'version': '1.0.0',
            'description': 'Backend API for FermTrack fermentation tracking application',
            'endpoints': {
                'authentication': '/api/auth',
                'batches': '/api/batches',
                'health': '/api/health'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Endpoint not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin_user = User(
                username='admin',
                email='admin@fermtrack.com',
                role='admin'
            )
            admin_user.set_password('admin123')  # Change this in production!
            
            try:
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin user created: admin/admin123")
            except Exception as e:
                db.session.rollback()
                print(f"Could not create default admin user: {e}")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)