#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System
Copyright (C) 2026 FermTrack Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import config
from models import db, User, Batch, BatchAction, FermentationStage, Bakery, UserBakery
from auth import auth_bp
from batches import batches_bp
from bakeries import bakeries_bp
from middleware import TenantMiddleware
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
    
    # Initialize tenant middleware
    tenant_middleware = TenantMiddleware(app)
    
    # Configure CORS - Allow access from local network devices  
    cors_origins = ['*'] if os.environ.get('FLASK_ENV', 'development') == 'development' else [
        'http://localhost:3000', 'http://127.0.0.1:3000', 
        'http://localhost:8080', 'http://127.0.0.1:8080',
        'https://fermtrack.com'
    ]
    
    CORS(app, 
         origins=cors_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization', 'X-Bakery-Slug'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(batches_bp)
    app.register_blueprint(bakeries_bp)
    
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
            'license': {
                'name': 'GNU Affero General Public License v3.0',
                'url': 'https://www.gnu.org/licenses/agpl-3.0.html',
                'source_code': 'https://github.com/abelgraham/fermtrack',
                'notice': 'This software is licensed under AGPL3. Source code must be made available to network users.'
            },
            'endpoints': {
                'authentication': '/api/auth',
                'batches': '/api/batches',
                'bakeries': '/api/bakeries',
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
    
    # Initialize database tables only
    with app.app_context():
        db.create_all()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)