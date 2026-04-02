#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Bakery Management Module
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
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import Schema, fields, ValidationError
from models import db, Bakery, User, UserBakery
from middleware import get_current_bakery, require_bakery
import re

bakeries_bp = Blueprint('bakeries', __name__, url_prefix='/api/bakeries')

class BakeryRegistrationSchema(Schema):
    slug = fields.Str(
        required=True, 
        validate=lambda x: len(x) >= 2 and len(x) <= 50 and re.match(r'^[a-z0-9-]+$', x),
        error_messages={'validator_failed': 'Slug must be 2-50 characters, lowercase letters, numbers and hyphens only'}
    )
    name = fields.Str(
        required=True, 
        validate=lambda x: len(x.strip()) >= 2 and len(x.strip()) <= 100,
        error_messages={'validator_failed': 'Name must be between 2 and 100 characters'}
    )
    description = fields.Str(allow_none=True)
    timezone = fields.Str(missing='UTC')
    contact_email = fields.Email(required=True, error_messages={'invalid': 'Valid email required'})
    contact_name = fields.Str(required=True, validate=lambda x: len(x.strip()) >= 2)

@bakeries_bp.route('/register', methods=['POST'])
def register_bakery():
    """Public bakery registration endpoint"""
    schema = BakeryRegistrationSchema()
    
    try:
        data = schema.load(request.get_json())
        data['name'] = data['name'].strip()
        data['slug'] = data['slug'].lower()
        data['contact_name'] = data['contact_name'].strip()
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Check if slug already exists
    existing_bakery = Bakery.query.filter_by(slug=data['slug']).first()
    if existing_bakery:
        return jsonify({'error': 'Bakery slug already exists'}), 409
    
    # Create new bakery (starts as pending verification)
    bakery = Bakery(
        slug=data['slug'],
        name=data['name'],
        description=data.get('description'),
        timezone=data['timezone'],
        is_verified=False,
        verification_status='pending',
        verification_notes=f"Contact: {data['contact_name']} ({data['contact_email']})",
        is_active=False  # Not active until verified
    )
    
    try:
        db.session.add(bakery)
        db.session.commit()
        
        return jsonify({
            'message': 'Bakery registration submitted successfully. You will be notified when it is approved.',
            'bakery': {
                'id': bakery.id,
                'slug': bakery.slug,
                'name': bakery.name,
                'verification_status': bakery.verification_status
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to register bakery', 'details': str(e)}), 500

class BakeryCreateSchema(Schema):
    slug = fields.Str(
        required=True, 
        validate=lambda x: len(x) >= 2 and len(x) <= 50 and re.match(r'^[a-z0-9-]+$', x),
        error_messages={'validator_failed': 'Slug must be 2-50 characters, lowercase letters, numbers and hyphens only'}
    )
    name = fields.Str(
        required=True, 
        validate=lambda x: len(x.strip()) >= 2 and len(x.strip()) <= 100,
        error_messages={'validator_failed': 'Name must be between 2 and 100 characters'}
    )
    description = fields.Str(allow_none=True)
    timezone = fields.Str(missing='UTC')

class BakeryUpdateSchema(Schema):
    name = fields.Str(validate=lambda x: len(x.strip()) >= 2 and len(x.strip()) <= 100)
    description = fields.Str(allow_none=True)
    timezone = fields.Str()

@bakeries_bp.route('', methods=['POST'])
@jwt_required()
def create_bakery():
    """Create a new bakery (super admin functionality)"""
    schema = BakeryCreateSchema()
    current_user_id = get_jwt_identity()
    
    try:
        data = schema.load(request.get_json())
        data['name'] = data['name'].strip()
        data['slug'] = data['slug'].lower()
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Check if slug already exists
    existing_bakery = Bakery.query.filter_by(slug=data['slug']).first()
    if existing_bakery:
        return jsonify({'error': 'Bakery slug already exists'}), 409
    
    # Create new bakery (starts as pending verification)
    bakery = Bakery(
        slug=data['slug'],
        name=data['name'],
        description=data.get('description'),
        timezone=data['timezone'],
        is_verified=False,
        verification_status='pending',
        is_active=False  # Not active until verified
    )
    
    try:
        db.session.add(bakery)
        db.session.flush()  # Get bakery ID
        
        # Add creator as admin of this bakery
        user_bakery = UserBakery(
            user_id=current_user_id,
            bakery_id=bakery.id,
            role='admin'
        )
        db.session.add(user_bakery)
        db.session.commit()
        
        return jsonify({
            'message': 'Bakery created successfully',
            'bakery': bakery.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create bakery'}), 500

@bakeries_bp.route('/current', methods=['GET'])
@jwt_required()
@require_bakery
def get_current_bakery():
    """Get current bakery information"""
    current_bakery = get_current_bakery()
    if not current_bakery:
        return jsonify({'error': 'No bakery context'}), 400
    
    return jsonify({'bakery': current_bakery.to_dict()}), 200

@bakeries_bp.route('/current', methods=['PUT'])
@jwt_required()
@require_bakery
def update_current_bakery():
    """Update current bakery (admin only)"""
    schema = BakeryUpdateSchema()
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    current_bakery = get_current_bakery()
    
    # Check if user has admin role in current bakery
    user_role = current_user.get_role_in_bakery(current_bakery.id) if current_user else None
    if not user_role or user_role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = schema.load(request.get_json())
        if 'name' in data:
            data['name'] = data['name'].strip()
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Update fields
    for field, value in data.items():
        setattr(current_bakery, field, value)
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Bakery updated successfully',
            'bakery': current_bakery.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update bakery'}), 500

@bakeries_bp.route('/current/users/<user_id>/invite', methods=['POST']) 
@jwt_required()
@require_bakery
def invite_user_to_bakery(user_id):
    """Invite a user to current bakery (admin only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    current_bakery = get_current_bakery()
    
    # Check if user has admin role in current bakery
    user_role = current_user.get_role_in_bakery(current_bakery.id) if current_user else None
    if not user_role or user_role != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Validate role from request
    data = request.get_json() or {}
    role = data.get('role', 'baker')
    if role not in ['baker', 'manager', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Find target user
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user already has access
    existing = UserBakery.query.filter_by(
        user_id=user_id,
        bakery_id=current_bakery.id
    ).first()
    
    if existing:
        if existing.is_active:
            return jsonify({'error': 'User already has access to this bakery'}), 409
        else:
            # Reactivate existing association
            existing.is_active = True
            existing.role = role
    else:
        # Create new association
        user_bakery = UserBakery(
            user_id=user_id,
            bakery_id=current_bakery.id,
            role=role
        )
        db.session.add(user_bakery)
    
    try:
        db.session.commit()
        return jsonify({'message': 'User invited successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to invite user'}), 500

class BakeryVerificationSchema(Schema):
    verification_status = fields.Str(
        required=True,
        validate=lambda x: x in ['pending', 'approved', 'rejected'],
        error_messages={'validator_failed': 'Status must be one of: pending, approved, rejected'}
    )
    verification_notes = fields.Str(allow_none=True)

@bakeries_bp.route('/verification/pending', methods=['GET'])
@jwt_required()
def list_pending_verifications():
    """List bakeries pending verification (super admin only)"""
    # TODO: Add super admin check here
    # For now, allowing any authenticated user to see pending verifications
    
    pending_bakeries = Bakery.query.filter_by(verification_status='pending').all()
    
    return jsonify({
        'pending_bakeries': [bakery.to_dict() for bakery in pending_bakeries]
    }), 200

@bakeries_bp.route('/<bakery_id>/verification', methods=['PUT'])
@jwt_required()
def update_bakery_verification(bakery_id):
    """Update bakery verification status (super admin only)"""
    schema = BakeryVerificationSchema()
    
    # TODO: Add super admin check here
    # For now, allowing any authenticated user to update verification
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Find bakery
    bakery = Bakery.query.get(bakery_id)
    if not bakery:
        return jsonify({'error': 'Bakery not found'}), 404
    
    # Update verification fields
    bakery.verification_status = data['verification_status']
    bakery.verification_notes = data.get('verification_notes')
    bakery.is_verified = (data['verification_status'] == 'approved')
    
    # If rejecting, deactivate the bakery
    if data['verification_status'] == 'rejected':
        bakery.is_active = False
    elif data['verification_status'] == 'approved':
        bakery.is_active = True
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Bakery verification updated successfully',
            'bakery': bakery.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update verification'}), 500
        return jsonify({'error': 'Failed to invite user'}), 500