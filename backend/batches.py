#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Batch Management Module
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
from models import db, Batch, BatchAction, FermentationStage, User
from middleware import require_bakery, get_current_bakery_id
from datetime import datetime
import uuid

batches_bp = Blueprint('batches', __name__, url_prefix='/api/batches')

class BatchCreateSchema(Schema):
    batch_id = fields.Str(required=True, validate=lambda x: len(x) >= 1 and len(x) <= 50)
    recipe_name = fields.Str(required=True, validate=lambda x: len(x) >= 1 and len(x) <= 100)
    dough_weight = fields.Float(required=True, validate=lambda x: x > 0)
    status = fields.Str(missing='mixing', validate=lambda x: x in ['mixing', 'bulk_ferment', 'divided', 'proofing', 'ready', 'baked', 'discarded'])
    temperature = fields.Float(allow_none=True)
    humidity = fields.Float(allow_none=True, validate=lambda x: x is None or (0 <= x <= 100))
    notes = fields.Str(allow_none=True)

class BatchUpdateSchema(Schema):
    recipe_name = fields.Str(validate=lambda x: len(x) >= 1 and len(x) <= 100)
    dough_weight = fields.Float(validate=lambda x: x > 0)
    status = fields.Str(validate=lambda x: x in ['mixing', 'bulk_ferment', 'divided', 'proofing', 'ready', 'baked', 'discarded'])
    temperature = fields.Float(allow_none=True)
    humidity = fields.Float(allow_none=True, validate=lambda x: x is None or (0 <= x <= 100))
    notes = fields.Str(allow_none=True)

class BatchActionSchema(Schema):
    action_type = fields.Str(required=True, validate=lambda x: x in ['fortify', 're-ball', 'degas', 'wash', 'divide', 'shape', 'other'])
    description = fields.Str(allow_none=True)
    weight_change = fields.Float(allow_none=True)
    temperature_recorded = fields.Float(allow_none=True)
    humidity_recorded = fields.Float(allow_none=True, validate=lambda x: x is None or (0 <= x <= 100))

class FermentationStageSchema(Schema):
    stage_name = fields.Str(required=True, validate=lambda x: x in ['autolyse', 'bulk_ferment', 'proof', 'final_proof', 'retard'])
    target_duration_hours = fields.Float(validate=lambda x: x > 0)
    temperature_target = fields.Float(allow_none=True)
    humidity_target = fields.Float(allow_none=True, validate=lambda x: x is None or (0 <= x <= 100))
    notes = fields.Str(allow_none=True)

@batches_bp.route('', methods=['POST'])
@jwt_required()
@require_bakery
def create_batch():
    """Create a new fermentation batch in current bakery"""
    schema = BatchCreateSchema()
    current_user_id = get_jwt_identity()
    bakery_id = get_current_bakery_id()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    # Check if batch_id already exists in this bakery
    existing_batch = Batch.query.filter_by(
        bakery_id=bakery_id, 
        batch_id=data['batch_id']
    ).first()
    if existing_batch:
        return jsonify({'error': 'Batch ID already exists in this bakery'}), 409
    
    # Create new batch
    batch = Batch(
        bakery_id=bakery_id,
        batch_id=data['batch_id'],
        recipe_name=data['recipe_name'],
        dough_weight=data['dough_weight'],
        status=data['status'],
        temperature=data.get('temperature'),
        humidity=data.get('humidity'),
        notes=data.get('notes'),
        created_by=current_user_id
    )
    
    try:
        db.session.add(batch)
        db.session.commit()
        
        return jsonify({
            'message': 'Batch created successfully',
            'batch': batch.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create batch'}), 500

@batches_bp.route('', methods=['GET'])
@jwt_required()
@require_bakery
def list_batches():
    """List batches in current bakery with optional filtering"""
    bakery_id = get_current_bakery_id()
    status_filter = request.args.get('status')
    limit = request.args.get('limit', type=int, default=50)
    offset = request.args.get('offset', type=int, default=0)
    
    query = Batch.query.filter_by(bakery_id=bakery_id)
    
    if status_filter:
        query = query.filter(Batch.status == status_filter)
    
    batches = query.order_by(Batch.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'batches': [batch.to_dict() for batch in batches],
        'total': query.count()
    }), 200

@batches_bp.route('/<batch_id>', methods=['GET'])
@jwt_required()
@require_bakery
def get_batch(batch_id):
    """Get a specific batch by ID in current bakery"""
    bakery_id = get_current_bakery_id()
    batch = Batch.query.filter_by(bakery_id=bakery_id, batch_id=batch_id).first()
    
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    return jsonify({'batch': batch.to_dict()}), 200

@batches_bp.route('/<batch_id>', methods=['PUT'])
@jwt_required()
@require_bakery
def update_batch(batch_id):
    """Update a batch in current bakery"""
    schema = BatchUpdateSchema()
    bakery_id = get_current_bakery_id()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    batch = Batch.query.filter_by(bakery_id=bakery_id, batch_id=batch_id).first()
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    # Update fields
    for field, value in data.items():
        setattr(batch, field, value)
    
    batch.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Batch updated successfully',
            'batch': batch.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update batch'}), 500

@batches_bp.route('/<batch_id>/actions', methods=['POST'])
@jwt_required()
@require_bakery
def add_batch_action(batch_id):
    """Add an action to a batch in current bakery"""
    schema = BatchActionSchema()
    current_user_id = get_jwt_identity()
    bakery_id = get_current_bakery_id()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    batch = Batch.query.filter_by(bakery_id=bakery_id, batch_id=batch_id).first()
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    # Create batch action
    action = BatchAction(
        batch_id=batch.id,
        user_id=current_user_id,
        action_type=data['action_type'],
        description=data.get('description'),
        weight_change=data.get('weight_change'),
        temperature_recorded=data.get('temperature_recorded'),
        humidity_recorded=data.get('humidity_recorded')
    )
    
    # Update batch weight if weight change is specified
    if data.get('weight_change'):
        batch.dough_weight += data['weight_change']
        batch.updated_at = datetime.utcnow()
    
    try:
        db.session.add(action)
        db.session.commit()
        
        return jsonify({
            'message': 'Action added successfully',
            'action': action.to_dict(),
            'batch': batch.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add action'}), 500

@batches_bp.route('/<batch_id>/fermentation-stages', methods=['POST'])
@jwt_required()
@require_bakery
def add_fermentation_stage(batch_id):
    """Add a fermentation stage to a batch in current bakery"""
    schema = FermentationStageSchema()
    bakery_id = get_current_bakery_id()
    
    try:
        data = schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'error': 'Validation error', 'details': err.messages}), 400
    
    batch = Batch.query.filter_by(bakery_id=bakery_id, batch_id=batch_id).first()
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    # Deactivate any existing active stages
    FermentationStage.query.filter_by(batch_id=batch.id, is_active=True).update({'is_active': False})
    
    # Create new fermentation stage
    stage = FermentationStage(
        batch_id=batch.id,
        stage_name=data['stage_name'],
        target_duration_hours=data.get('target_duration_hours'),
        temperature_target=data.get('temperature_target'),
        humidity_target=data.get('humidity_target'),
        notes=data.get('notes')
    )
    
    try:
        db.session.add(stage)
        db.session.commit()
        
        return jsonify({
            'message': 'Fermentation stage added successfully',
            'stage': stage.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add fermentation stage'}), 500

@batches_bp.route('/<batch_id>/fermentation-stages/<stage_id>/complete', methods=['PUT'])
@jwt_required()
@require_bakery
def complete_fermentation_stage(batch_id, stage_id):
    """Mark a fermentation stage as complete in current bakery"""
    bakery_id = get_current_bakery_id()
    batch = Batch.query.filter_by(bakery_id=bakery_id, batch_id=batch_id).first()
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    stage = FermentationStage.query.filter_by(id=stage_id, batch_id=batch.id).first()
    if not stage:
        return jsonify({'error': 'Fermentation stage not found'}), 404
    
    stage.end_time = datetime.utcnow()
    stage.is_active = False
    
    try:
        db.session.commit()
        return jsonify({
            'message': 'Fermentation stage completed successfully',
            'stage': stage.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to complete fermentation stage'}), 500

@batches_bp.route('/<batch_id>', methods=['DELETE'])
@jwt_required()
@require_bakery
def delete_batch(batch_id):
    """Delete a batch in current bakery (admin/manager only)"""
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)
    bakery_id = get_current_bakery_id()
    
    # Check if user has admin/manager role in current bakery
    user_role = current_user.get_role_in_bakery(bakery_id) if current_user else None
    if not user_role or user_role not in ['admin', 'manager']:
        return jsonify({'error': 'Insufficient permissions'}), 403
    
    batch = Batch.query.filter_by(bakery_id=bakery_id, batch_id=batch_id).first()
    if not batch:
        return jsonify({'error': 'Batch not found'}), 404
    
    try:
        db.session.delete(batch)
        db.session.commit()
        return jsonify({'message': 'Batch deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete batch'}), 500