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
from models import db, User, Bakery, UserBakery, UserBakeryApplication
from middleware import require_bakery, get_current_bakery_id
from datetime import datetime
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
    bakery_slug = fields.Str(missing=None, allow_none=True)

class UserLoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)
    bakery_slug = fields.Str(missing=None, allow_none=True)  # Optional for global admins

@auth_bp.route('/bakeries/available', methods=['GET'])
def list_available_bakeries():
    """List all active and verified bakeries for selection (public endpoint)"""
    bakeries = Bakery.query.filter_by(is_active=True, is_verified=True).all()
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
        
        # Associate user with specified bakery (optional)
        bakery_slug = data.get('bakery_slug')
        
        if bakery_slug:
            # User selected a bakery - associate them with it
            bakery = Bakery.query.filter_by(slug=bakery_slug, is_active=True, is_verified=True).first()
            if not bakery:
                return jsonify({'error': f'Bakery "{bakery_slug}" not found or not yet verified'}), 404
                
            user_bakery = UserBakery(
                user_id=user.id,
                bakery_id=bakery.id,
                role=data['role']
            )
            db.session.add(user_bakery)
        
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=user.id)
        
        message = 'User registered successfully'
        if not bakery_slug:
            message += '. You can now apply to join verified bakeries.'
        
        return jsonify({
            'message': message,
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
    
    bakery_slug = data.get('bakery_slug')
    
    # Global admins can login without specifying a bakery
    if user.is_global_admin:
        # For global admins, bakery_slug is optional
        pass
    elif bakery_slug:
        # Regular user must have access to the specified bakery
        user_bakery = db.session.query(UserBakery).join(Bakery).filter(
            UserBakery.user_id == user.id,
            Bakery.slug == bakery_slug,
            Bakery.is_active == True
        ).first()
        
        if not user_bakery:
            return jsonify({
                'error': f'Access denied to bakery "{bakery_slug}" or bakery not found'
            }), 403
    else:
        # Regular user must specify a bakery
        return jsonify({
            'error': 'Bakery must be specified for non-admin users'
        }), 400
    
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

# ==================== ADMIN ENDPOINTS ====================

def require_admin():
    """Decorator to require admin role"""
    from functools import wraps
    
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Check if user is a global admin first
            if user.is_global_admin:
                return f(*args, **kwargs)
            
            # Check if user has admin role in any bakery
            admin_role = UserBakery.query.filter_by(
                user_id=user.id,
                role='admin',
                is_active=True
            ).first()
            
            if not admin_role:
                return jsonify({'error': 'Admin access required'}), 403
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@auth_bp.route('/admin/users', methods=['GET', 'POST'])
@require_admin()
def admin_users():
    """Handle admin user operations"""
    
    if request.method == 'GET':
        """Get all users for admin management"""
        try:
            users = User.query.all()
            users_data = []
            
            for user in users:
                users_data.append({
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                })
                
            return jsonify({'users': users_data}), 200
        except Exception as e:
            return jsonify({'error': 'Failed to fetch users', 'details': str(e)}), 500
    
    elif request.method == 'POST':
        """Create a new user (admin only)"""
        try:
            data = request.get_json()
            if data is None:
                return jsonify({'error': 'Invalid JSON data provided'}), 400
                
            # Validate required fields
            required_fields = ['username', 'email', 'password']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Clean up username
            username = data['username'].strip()
            email = data['email'].strip()
            
            # Check if username or email already exists
            existing_user = User.query.filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    return jsonify({'error': 'Username already exists'}), 409
                else:
                    return jsonify({'error': 'Email already exists'}), 409
            
            # Create new user
            user = User(
                username=username,
                email=email,
                is_active=data.get('is_active', True)  # Default to active
            )
            user.set_password(data['password'])
            
            db.session.add(user)
            db.session.commit()
            
            return jsonify({
                'message': 'User created successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
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

@auth_bp.route('/admin/users/<user_id>', methods=['PUT'])
@require_admin()
def admin_update_user(user_id):
    """Update user details"""
    try:
        data = request.get_json()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        if 'is_active' in data:
            user.is_active = data['is_active']
            
        if 'username' in data:
            user.username = data['username']
            
        if 'email' in data:
            user.email = data['email']
            
        db.session.commit()
        return jsonify({'message': 'User updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user', 'details': str(e)}), 500

@auth_bp.route('/admin/users/<user_id>', methods=['DELETE'])
@require_admin()
def admin_delete_user(user_id):
    """Delete a user (admin only)"""
    try:
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        # Delete user bakery relationships first
        UserBakery.query.filter_by(user_id=user_id).delete()
        
        # Delete the user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user', 'details': str(e)}), 500

@auth_bp.route('/admin/bakeries', methods=['GET'])
@require_admin()
def admin_get_bakeries():
    """Get all bakeries for admin management"""
    try:
        bakeries = Bakery.query.all()
        bakeries_data = []
        
        for bakery in bakeries:
            bakeries_data.append({
                'id': bakery.id,
                'name': bakery.name,
                'slug': bakery.slug,
                'description': bakery.description,
                'is_active': bakery.is_active,
                'timezone': bakery.timezone,
                'created_at': bakery.created_at.isoformat() if bakery.created_at else None
            })
            
        return jsonify({'bakeries': bakeries_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch bakeries', 'details': str(e)}), 500

@auth_bp.route('/admin/bakeries/<bakery_id>', methods=['PUT'])
@require_admin()
def admin_update_bakery(bakery_id):
    """Update bakery details"""
    try:
        data = request.get_json()
        bakery = Bakery.query.get(bakery_id)
        
        if not bakery:
            return jsonify({'error': 'Bakery not found'}), 404
            
        if 'is_active' in data:
            bakery.is_active = data['is_active']
            
        if 'name' in data:
            bakery.name = data['name']
            
        if 'description' in data:
            bakery.description = data['description']
            
        if 'timezone' in data:
            bakery.timezone = data['timezone']
            
        db.session.commit()
        return jsonify({'message': 'Bakery updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update bakery', 'details': str(e)}), 500

@auth_bp.route('/admin/bakeries/<bakery_id>', methods=['DELETE'])
@require_admin()
def admin_delete_bakery(bakery_id):
    """Delete a bakery (admin only)"""
    try:
        bakery = Bakery.query.get(bakery_id)
        
        if not bakery:
            return jsonify({'error': 'Bakery not found'}), 404
            
        # Delete user bakery relationships first
        UserBakery.query.filter_by(bakery_id=bakery_id).delete()
        
        # Note: Batches will be cascade deleted due to foreign key constraints
        
        # Delete the bakery
        db.session.delete(bakery)
        db.session.commit()
        
        return jsonify({'message': 'Bakery deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete bakery', 'details': str(e)}), 500

@auth_bp.route('/admin/batches', methods=['GET'])
@require_admin()
def admin_get_batches():
    """Get all batches for admin management"""
    try:
        from models import Batch  # Import here to avoid circular imports
        
        bakery_id = request.args.get('bakery_id')
        
        if bakery_id:
            batches = Batch.query.filter_by(bakery_id=bakery_id).all()
        else:
            batches = Batch.query.all()
        
        batches_data = []
        
        for batch in batches:
            # Get bakery name
            bakery = Bakery.query.get(batch.bakery_id)
            
            batches_data.append({
                'id': batch.id,
                'batch_id': batch.batch_id,  # Human-readable ID
                'recipe_name': batch.recipe_name,  # Use recipe_name instead of name
                'status': batch.status,
                'bakery_id': batch.bakery_id,
                'bakery_name': bakery.name if bakery else 'Unknown',
                'created_at': batch.created_at.isoformat() if batch.created_at else None
            })
            
        return jsonify({'batches': batches_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch batches', 'details': str(e)}), 500

@auth_bp.route('/admin/batches/<batch_id>', methods=['DELETE'])
@require_admin()
def admin_delete_batch(batch_id):
    """Delete a batch (admin only)"""
    try:
        from models import Batch  # Import here to avoid circular imports
        
        batch = Batch.query.get(batch_id)
        
        if not batch:
            return jsonify({'error': 'Batch not found'}), 404
            
        db.session.delete(batch)
        db.session.commit()
        
        return jsonify({'message': 'Batch deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete batch', 'details': str(e)}), 500

@auth_bp.route('/admin/user-roles', methods=['GET'])
@require_admin()
def admin_get_user_roles():
    """Get all user-bakery relationships for admin management"""
    try:
        user_roles = db.session.query(
            UserBakery.user_id,
            UserBakery.bakery_id,
            UserBakery.role,
            UserBakery.is_active,
            User.username,
            Bakery.name.label('bakery_name')
        ).join(User).join(Bakery).all()
        
        roles_data = []
        
        for role in user_roles:
            roles_data.append({
                'user_id': role.user_id,
                'bakery_id': role.bakery_id,
                'role': role.role,
                'is_active': role.is_active,
                'username': role.username,
                'bakery_name': role.bakery_name
            })
            
        return jsonify({'user_roles': roles_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user roles', 'details': str(e)}), 500

@auth_bp.route('/admin/user-roles', methods=['PUT'])
@require_admin()
def admin_update_user_role():
    """Update a user's role in a bakery"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bakery_id = data.get('bakery_id')
        new_role = data.get('role')
        
        if not all([user_id, bakery_id, new_role]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        if new_role not in ['baker', 'manager', 'admin']:
            return jsonify({'error': 'Invalid role'}), 400
            
        user_bakery = UserBakery.query.filter_by(
            user_id=user_id,
            bakery_id=bakery_id
        ).first()
        
        if not user_bakery:
            return jsonify({'error': 'User-bakery relationship not found'}), 404
            
        user_bakery.role = new_role
        db.session.commit()
        
        return jsonify({'message': 'User role updated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user role', 'details': str(e)}), 500

@auth_bp.route('/admin/user-roles', methods=['DELETE'])
@require_admin()
def admin_delete_user_role():
    """Remove a user from a bakery"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        bakery_id = data.get('bakery_id')
        
        if not all([user_id, bakery_id]):
            return jsonify({'error': 'Missing required fields'}), 400
            
        user_bakery = UserBakery.query.filter_by(
            user_id=user_id,
            bakery_id=bakery_id
        ).first()
        
        if not user_bakery:
            return jsonify({'error': 'User-bakery relationship not found'}), 404
            
        db.session.delete(user_bakery)
        db.session.commit()
        
        return jsonify({'message': 'User removed from bakery successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove user from bakery', 'details': str(e)}), 500

# ==================== USER APPLICATION ENDPOINTS ====================

class UserApplicationSchema(Schema):
    bakery_slug = fields.Str(required=True)
    requested_role = fields.Str(missing='baker', validate=lambda x: x in ['baker', 'manager', 'admin'])
    message = fields.Str(allow_none=True)

@auth_bp.route('/apply', methods=['POST'])
@jwt_required()
def apply_to_bakery():
    """Submit an application to join a bakery"""
    schema = UserApplicationSchema()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Find the bakery
    bakery = Bakery.query.filter_by(slug=data['bakery_slug'], is_active=True).first()
    if not bakery:
        return jsonify({'error': 'Bakery not found'}), 404
    
    # Check if user is already in this bakery
    existing_membership = UserBakery.query.filter_by(
        user_id=user.id,
        bakery_id=bakery.id
    ).first()
    
    if existing_membership:
        return jsonify({'error': 'You are already a member of this bakery'}), 409
    
    # Check if application already exists
    existing_application = UserBakeryApplication.query.filter_by(
        user_id=user.id,
        bakery_id=bakery.id,
        status='pending'
    ).first()
    
    if existing_application:
        return jsonify({'error': 'You already have a pending application for this bakery'}), 409
    
    # Create new application
    application = UserBakeryApplication(
        user_id=user.id,
        bakery_id=bakery.id,
        requested_role=data['requested_role'],
        message=data.get('message')
    )
    
    try:
        db.session.add(application)
        db.session.commit()
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to submit application', 'details': str(e)}), 500

@auth_bp.route('/admin/applications', methods=['GET'])
@require_admin()
def admin_get_applications():
    """Get bakery applications for admin review"""
    try:
        # Get current admin user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.is_global_admin:
            # Global admins can see all applications
            applications = UserBakeryApplication.query.order_by(
                UserBakeryApplication.created_at.desc()
            ).all()
        else:
            # Regular admins only see applications for bakeries they manage
            admin_bakeries = UserBakery.query.filter_by(
                user_id=user.id,
                role='admin',
                is_active=True
            ).all()
            
            bakery_ids = [ub.bakery_id for ub in admin_bakeries]
            applications = UserBakeryApplication.query.filter(
                UserBakeryApplication.bakery_id.in_(bakery_ids)
            ).order_by(UserBakeryApplication.created_at.desc()).all()
        
        return jsonify({
            'applications': [app.to_dict() for app in applications]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch applications', 'details': str(e)}), 500

@auth_bp.route('/admin/applications/<application_id>', methods=['PUT'])
@require_admin()
def admin_review_application(application_id):
    """Approve or reject a user application"""
    try:
        data = request.get_json()
        status = data.get('status')  # approved, rejected
        admin_notes = data.get('admin_notes', '')
        
        if status not in ['approved', 'rejected']:
            return jsonify({'error': 'Invalid status. Must be approved or rejected'}), 400
        
        application = UserBakeryApplication.query.get(application_id)
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        if application.status != 'pending':
            return jsonify({'error': 'Application has already been reviewed'}), 400
        
        # Get current admin user
        current_user = get_jwt_identity()
        admin_user = User.query.filter_by(username=current_user).first()
        
        # Check admin has permission for this bakery
        admin_access = UserBakery.query.filter_by(
            user_id=admin_user.id,
            bakery_id=application.bakery_id,
            role='admin',
            is_active=True
        ).first()
        
        if not admin_access:
            return jsonify({'error': 'You do not have admin access to this bakery'}), 403
        
        # Update application
        application.status = status
        application.admin_notes = admin_notes
        application.reviewed_at = datetime.utcnow()
        application.reviewed_by_id = admin_user.id
        
        # If approved, create UserBakery relationship
        if status == 'approved':
            user_bakery = UserBakery(
                user_id=application.user_id,
                bakery_id=application.bakery_id,
                role=application.requested_role
            )
            db.session.add(user_bakery)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Application {status} successfully',
            'application': application.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to review application', 'details': str(e)}), 500

@auth_bp.route('/admin/verification', methods=['GET'])
@require_admin()
def admin_get_verification():
    """Get bakery verification data for admin management"""
    try:
        # Get current admin user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.is_global_admin:
            # Global admins can see all bakeries
            bakeries = Bakery.query.all()
        else:
            # Regular admins only see bakeries they manage
            admin_bakeries = UserBakery.query.filter_by(
                user_id=user.id,
                role='admin',
                is_active=True
            ).all()
            bakery_ids = [ub.bakery_id for ub in admin_bakeries]
            bakeries = Bakery.query.filter(Bakery.id.in_(bakery_ids)).all()
        
        verification_data = []
        for bakery in bakeries:
            verification_data.append({
                'id': bakery.id,
                'name': bakery.name,
                'slug': bakery.slug,
                'is_verified': getattr(bakery, 'is_verified', True),  # Default to verified if no field
                'is_active': bakery.is_active,
                'created_at': bakery.created_at.isoformat() if bakery.created_at else None,
                'description': bakery.description
            })
        
        return jsonify({'verifications': verification_data}), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch verification data', 'details': str(e)}), 500