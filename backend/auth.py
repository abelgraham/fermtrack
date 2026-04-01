#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Authentication Module
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

from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from models import db, User
import re

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

class UserRegistrationSchema(Schema):
    username = fields.Str(
        required=True, 
        validate=lambda x: len(x.strip()) >= 3 and len(x.strip()) <= 80,
        error_messages={'validator_failed': 'Username must be between 3 and 80 characters'}
    )
    email = fields.Email(
        required=True,
        error_messages={'invalid': 'Please provide a valid email address'}
    )
    password = fields.Str(
        required=True, 
        validate=lambda x: len(x) >= 6,
        error_messages={'validator_failed': 'Password must be at least 6 characters long'}
    )
    role = fields.Str(
        missing='baker', 
        validate=lambda x: x in ['baker', 'manager', 'admin'],
        error_messages={'validator_failed': 'Role must be one of: baker, manager, admin'}
    )

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    schema = UserRegistrationSchema()
    
    # Get and validate request data
    try:
        request_data = request.get_json()
        if request_data is None:
            return jsonify({'error': 'Invalid JSON data provided'}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to parse JSON data', 'details': str(e)}), 400
    
    try:
        data = schema.load(request_data)
        # Clean up username by trimming whitespace
        data['username'] = data['username'].strip()
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Check if username or email already exists
    existing_user = User.query.filter(
        (User.username == data['username']) | (User.email == data['email'])
    ).first()
    
    if existing_user:
        if existing_user.username == data['username']:
            return jsonify({'error': 'Username already exists'}), 409
        else:
            return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        role=data['role']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        error_msg = str(e)
        
        # Check for specific database constraint violations
        if 'UNIQUE constraint failed: users.username' in error_msg:
            return jsonify({'error': 'Username already exists'}), 409
        elif 'UNIQUE constraint failed: users.email' in error_msg:
            return jsonify({'error': 'Email already exists'}), 409
        else:
            return jsonify({'error': 'Failed to create user', 'details': error_msg}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user and return access token"""
    schema = UserLoginSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Find user by username
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is inactive'}), 401
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    """List all users (admin/manager only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role not in ['admin', 'manager']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    users = User.query.all()
    return jsonify({
        'users': [user.to_dict() for user in users]
    }), 200

@auth_bp.route('/users/<user_id>/deactivate', methods=['PUT'])
@jwt_required()
def deactivate_user(user_id):
    """Deactivate a user (admin only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user or current_user.role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    user.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'User deactivated successfully'}), 200