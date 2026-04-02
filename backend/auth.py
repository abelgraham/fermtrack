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

from flask import Blueprint, request, jsonify, g
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from models import db, User, Bakery, UserBakery
from middleware import require_bakery, get_current_bakery_id
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
        validate=lambda x: x == 'baker',
        error_messages={'validator_failed': 'Only baker role is allowed during registration. Contact an admin to upgrade your role.'}
    )
    bakery_slug = fields.Str(missing=None)

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    bakery_slug = fields.Str(required=True)

@auth_bp.route('/bakeries/available', methods=['GET'])
def list_available_bakeries():
    """List all active bakeries for selection (public endpoint)"""
    bakeries = Bakery.query.filter_by(is_active=True).all()
    return jsonify({
        'bakeries': [{
            'id': bakery.id,
            'slug': bakery.slug, 
            'name': bakery.name,
            'description': bakery.description
        } for bakery in bakeries]
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user and associate with specified bakery"""
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
        email=data['email']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Associate user with specified or default bakery
        bakery_slug = data.get('bakery_slug', 'demo')
        bakery = Bakery.query.filter_by(slug=bakery_slug, is_active=True).first()
        if not bakery:
            return jsonify({'error': f'Bakery "{bakery_slug}" not found'}), 404
            
        user_bakery = UserBakery(
            user_id=user.id,
            bakery_id=bakery.id,
            role=data['role']
        )
        db.session.add(user_bakery)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user.to_dict(include_bakeries=True)
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
    
    # Validate user has access to the specified bakery
    bakery_slug = data['bakery_slug']
    user_bakery = db.session.query(UserBakery).join(Bakery).filter(
        UserBakery.user_id == user.id,
        Bakery.slug == bakery_slug,
        Bakery.is_active == True
    ).first()
    
    if not user_bakery:
        return jsonify({
            'error': f'Access denied to bakery "{bakery_slug}" or bakery not found'
        }), 403
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict(include_bakeries=True)
    }), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({'user': user.to_dict(include_bakeries=True)}), 200

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@require_bakery
def list_users():
    """List users in current bakery (admin/manager only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    bakery_id = get_current_bakery_id()
    
    # Check if user has admin/manager role in current bakery
    user_role = current_user.get_role_in_bakery(bakery_id) if current_user else None
    if not user_role or user_role not in ['admin', 'manager']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    # Get users in current bakery
    user_bakeries = UserBakery.query.filter_by(bakery_id=bakery_id, is_active=True).all()
    users_data = []
    for ub in user_bakeries:
        user_dict = ub.user.to_dict()
        user_dict['role'] = ub.role
        users_data.append(user_dict)
    
    return jsonify({
        'users': users_data
    }), 200

@auth_bp.route('/users/<user_id>/deactivate', methods=['PUT'])
@jwt_required()
@require_bakery
def deactivate_user(user_id):
    """Deactivate a user in current bakery (admin only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    bakery_id = get_current_bakery_id()
    
    # Check if user has admin role in current bakery
    user_role = current_user.get_role_in_bakery(bakery_id) if current_user else None
    if not user_role or user_role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Find user-bakery association
    user_bakery = UserBakery.query.filter_by(
        user_id=user_id, 
        bakery_id=bakery_id, 
        is_active=True
    ).first()
    
    if not user_bakery:
        return jsonify({'error': 'User not found in this bakery'}), 404
    
    user_bakery.is_active = False
    db.session.commit()
    
    return jsonify({'message': 'User access revoked successfully'}), 200

@auth_bp.route('/context/default-bakery', methods=['GET'])
@jwt_required()
def get_default_bakery():
    """Get user's default bakery context"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get first active bakery as default
    active_bakeries = [ub for ub in current_user.user_bakeries if ub.is_active and ub.bakery.is_active]
    
    if not active_bakeries:
        return jsonify({'error': 'No bakeries available'}), 404
    
    default_bakery = active_bakeries[0]
    
    return jsonify({
        'default_bakery': {
            'slug': default_bakery.bakery.slug,
            'name': default_bakery.bakery.name,
            'role': default_bakery.role,
            'bakery_id': default_bakery.bakery_id
        },
        'all_bakeries': [{
            'slug': ub.bakery.slug,
            'name': ub.bakery.name,
            'role': ub.role,
            'bakery_id': ub.bakery_id
        } for ub in active_bakeries]
    }), 200

@auth_bp.route('/context/set-bakery', methods=['POST'])
@jwt_required()
def set_bakery_context():
    """Set bakery context for user session"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    data = request.get_json() or {}
    bakery_slug = data.get('bakery_slug')
    
    if not bakery_slug:
        return jsonify({'error': 'bakery_slug is required'}), 400
    
    # Check if user has access to this bakery
    bakery = Bakery.query.filter_by(slug=bakery_slug, is_active=True).first()
    if not bakery:
        return jsonify({'error': 'Bakery not found'}), 404
    
    if not current_user.has_access_to_bakery(bakery.id):
        return jsonify({'error': 'Access denied to this bakery'}), 403
    
    # Return bakery context for frontend to use
    user_role = current_user.get_role_in_bakery(bakery.id)
    return jsonify({
        'message': 'Bakery context set successfully',
        'bakery': bakery.to_dict(),
        'role': user_role,
        'headers': {
            'X-Bakery-Slug': bakery_slug
        }
    }), 200

@auth_bp.route('/bakeries', methods=['GET'])
@jwt_required() 
def list_user_bakeries():
    """List all bakeries current user has access to"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    bakeries_data = []
    for ub in current_user.user_bakeries:
        if ub.is_active and ub.bakery.is_active:
            bakery_dict = ub.bakery.to_dict()
            bakery_dict['role'] = ub.role
            bakery_dict['joined_at'] = ub.joined_at.isoformat() if ub.joined_at else None
            bakeries_data.append(bakery_dict)
    
    return jsonify({'bakeries': bakeries_data}), 200

class UserRoleUpdateSchema(Schema):
    role = fields.Str(
        required=True,
        validate=lambda x: x in ['baker', 'manager', 'admin'],
        error_messages={'validator_failed': 'Role must be one of: baker, manager, admin'}
    )

@auth_bp.route('/users/<user_id>/role', methods=['PUT'])
@jwt_required()
@require_bakery
def update_user_role(user_id):
    """Update a user's role in current bakery (admin only)"""
    schema = UserRoleUpdateSchema()
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    bakery_id = get_current_bakery_id()
    
    # Check if current user has admin role in current bakery
    user_role = current_user.get_role_in_bakery(bakery_id) if current_user else None
    if not user_role or user_role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Validate request data
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Find target user-bakery association
    user_bakery = UserBakery.query.filter_by(
        user_id=user_id, 
        bakery_id=bakery_id, 
        is_active=True
    ).first()
    
    if not user_bakery:
        return jsonify({'error': 'User not found in this bakery'}), 404
    
    # Don't allow admin to demote themselves
    if user_id == current_user_id and data['role'] != 'admin':
        return jsonify({'error': 'Cannot change your own admin role'}), 400
    
    old_role = user_bakery.role
    user_bakery.role = data['role']
    
    try:
        db.session.commit()
        return jsonify({
            'message': f'User role updated from {old_role} to {data["role"]}',
            'user_id': user_id,
            'old_role': old_role,
            'new_role': data['role']
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user role', 'details': str(e)}), 500
    
    return jsonify({'bakeries': bakeries_data}), 200