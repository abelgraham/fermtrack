#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Database Models
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

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class Bakery(db.Model):
    """Bakery model for multi-tenancy"""
    __tablename__ = 'bakeries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)  # Used in subdomain
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    timezone = db.Column(db.String(50), default='UTC')
    is_active = db.Column(db.Boolean, default=True)
    # Verification fields for admin approval workflow
    is_verified = db.Column(db.Boolean, default=False)
    verification_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    verification_notes = db.Column(db.Text)
    
    # Credit system fields
    credit_type = db.Column(db.String(20), default='limited')  # limited, unlimited
    credit_limit = db.Column(db.Integer, default=10)  # Monthly credit limit for limited accounts
    credit_used = db.Column(db.Integer, default=0)  # Credits used this cycle
    credit_reset_date = db.Column(db.DateTime, default=lambda: datetime.utcnow().replace(day=1))  # Monthly reset
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_bakeries = db.relationship('UserBakery', back_populates='bakery', cascade='all, delete-orphan')
    batches = db.relationship('Batch', backref='bakery', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert bakery to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'description': self.description,
            'timezone': self.timezone,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'verification_status': self.verification_status, 
            'verification_notes': self.verification_notes,
            'credit_type': self.credit_type,
            'credit_limit': self.credit_limit,
            'credit_used': self.credit_used,
            'credit_remaining': self.get_credit_remaining(),
            'credit_reset_date': self.credit_reset_date.isoformat() if self.credit_reset_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
    def get_credit_remaining(self):
        """Get remaining credits for this bakery"""
        if self.credit_type == 'unlimited':
            return -1  # -1 indicates unlimited
        return max(0, self.credit_limit - self.credit_used)
    
    def can_create_batch(self):
        """Check if bakery can create a new batch based on credit limits"""
        # Unverified bakeries have stricter limits
        if not self.is_verified:
            if self.credit_type == 'unlimited':
                return False, "Unlimited credits requires bakery verification"
            # Unverified limited accounts get half the credits
            effective_limit = self.credit_limit // 2
            if self.credit_used >= effective_limit:
                return False, f"Credit limit reached ({self.credit_used}/{effective_limit} for unverified account)"
        
        # Verified bakeries
        if self.credit_type == 'unlimited':
            return True, "Unlimited credits"
        
        if self.credit_used >= self.credit_limit:
            return False, f"Credit limit reached ({self.credit_used}/{self.credit_limit})"
        
        return True, f"Credits available ({self.credit_used}/{self.credit_limit})"
    
    def consume_credit(self):
        """Consume one credit for creating a batch"""
        can_create, message = self.can_create_batch()
        if not can_create:
            return False, message
        
        self.credit_used += 1
        return True, f"Credit consumed. Remaining: {self.get_credit_remaining()}"
    
    def reset_credits_if_needed(self):
        """Reset credits if we're in a new billing cycle"""
        from datetime import datetime, timedelta
        import calendar
        
        now = datetime.utcnow()
        
        # If reset date is in the past, reset credits
        if self.credit_reset_date and self.credit_reset_date < now:
            self.credit_used = 0
            
            # Set next reset date to the first day of next month
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            
            self.credit_reset_date = next_month
            return True
        
        return False

class UserBakeryApplication(db.Model):
    """Model for users applying to join bakeries"""
    __tablename__ = 'user_bakery_applications'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    bakery_id = db.Column(db.String(36), db.ForeignKey('bakeries.id'), nullable=False)
    requested_role = db.Column(db.String(20), nullable=False, default='baker')  # baker, manager, admin
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    message = db.Column(db.Text)  # User's message explaining why they want to join
    admin_notes = db.Column(db.Text)  # Admin notes for approval/rejection
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed_at = db.Column(db.DateTime)
    reviewed_by_id = db.Column(db.String(36), db.ForeignKey('users.id'))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='bakery_applications')
    bakery = db.relationship('Bakery', backref='user_applications')
    reviewed_by = db.relationship('User', foreign_keys=[reviewed_by_id])
    
    # Unique constraint to prevent duplicate applications
    __table_args__ = (db.UniqueConstraint('user_id', 'bakery_id', name='uq_user_bakery_application'),)
    
    def to_dict(self):
        """Convert application to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email
            } if self.user else None,
            'bakery_id': self.bakery_id,
            'bakery': {
                'id': self.bakery.id,
                'name': self.bakery.name,
                'slug': self.bakery.slug
            } if self.bakery else None,
            'requested_role': self.requested_role,
            'status': self.status,
            'message': self.message,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewed_at': self.reviewed_at.isoformat() if self.reviewed_at else None,
            'reviewed_by': {
                'id': self.reviewed_by.id,
                'username': self.reviewed_by.username
            } if self.reviewed_by else None
        }

class UserBakery(db.Model):
    """Association model for User-Bakery many-to-many relationship with roles"""
    __tablename__ = 'user_bakeries'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    bakery_id = db.Column(db.String(36), db.ForeignKey('bakeries.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='baker')  # baker, manager, admin
    is_active = db.Column(db.Boolean, default=True)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='user_bakeries')
    bakery = db.relationship('Bakery', back_populates='user_bakeries')
    
    # Unique constraint to prevent duplicate user-bakery combinations
    __table_args__ = (db.UniqueConstraint('user_id', 'bakery_id', name='uq_user_bakery'),)
    
    def to_dict(self):
        """Convert user-bakery association to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'bakery_id': self.bakery_id,
            'bakery': self.bakery.to_dict() if self.bakery else None,
            'role': self.role,
            'is_active': self.is_active,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

class User(db.Model):
    """User model for authentication and authorization"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_global_admin = db.Column(db.Boolean, default=False)  # Global admin can access all bakeries
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user_bakeries = db.relationship('UserBakery', back_populates='user', cascade='all, delete-orphan')
    actions = db.relationship('BatchAction', backref='user', lazy=True)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_bakeries(self):
        """Get all bakeries this user has access to"""
        return [ub.bakery for ub in self.user_bakeries if ub.is_active and ub.bakery.is_active]
    
    def get_role_in_bakery(self, bakery_id):
        """Get user's role in a specific bakery"""
        user_bakery = next((ub for ub in self.user_bakeries 
                           if ub.bakery_id == bakery_id and ub.is_active), None)
        return user_bakery.role if user_bakery else None
    
    def has_access_to_bakery(self, bakery_id):
        """Check if user has access to a specific bakery"""
        # Global admins have access to all bakeries
        if self.is_global_admin:
            return True
        return any(ub.bakery_id == bakery_id and ub.is_active 
                  for ub in self.user_bakeries)
    
    def to_dict(self, include_bakeries=False):
        """Convert user to dictionary for JSON serialization"""
        result = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_global_admin': self.is_global_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_bakeries:
            result['bakeries'] = [ub.to_dict() for ub in self.user_bakeries if ub.is_active]
        
        return result

class Batch(db.Model):
    """Batch model for tracking fermentation batches"""
    __tablename__ = 'batches'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    bakery_id = db.Column(db.String(36), db.ForeignKey('bakeries.id'), nullable=False)
    batch_id = db.Column(db.String(50), nullable=False, index=True)  # Human-readable ID (unique per bakery)
    recipe_name = db.Column(db.String(100), nullable=False)
    dough_weight = db.Column(db.Float, nullable=False)  # Weight in grams
    status = db.Column(db.String(20), nullable=False, default='mixing')  # mixing, bulk_ferment, divided, proofing, ready, baked, discarded
    temperature = db.Column(db.Float)  # Environment temperature in Celsius
    humidity = db.Column(db.Float)  # Environment humidity percentage
    notes = db.Column(db.Text)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref='created_batches', foreign_keys=[created_by])
    actions = db.relationship('BatchAction', backref='batch', lazy=True, cascade='all, delete-orphan')
    fermentation_stages = db.relationship('FermentationStage', backref='batch', lazy=True, cascade='all, delete-orphan')
    
    # Unique constraint for batch_id per bakery
    __table_args__ = (db.UniqueConstraint('bakery_id', 'batch_id', name='uq_bakery_batch_id'),)
    
    def to_dict(self):
        """Convert batch to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'bakery_id': self.bakery_id,
            'batch_id': self.batch_id,
            'recipe_name': self.recipe_name,
            'dough_weight': self.dough_weight,
            'status': self.status,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'notes': self.notes,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'actions': [action.to_dict() for action in self.actions],
            'fermentation_stages': [stage.to_dict() for stage in self.fermentation_stages]
        }

class BatchAction(db.Model):
    """Action log for batch modifications"""
    __tablename__ = 'batch_actions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = db.Column(db.String(36), db.ForeignKey('batches.id'), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)  # fortify, re-ball, degas, wash, divide, shape, etc.
    description = db.Column(db.Text)
    weight_change = db.Column(db.Float)  # Weight change in grams (+ or -)
    temperature_recorded = db.Column(db.Float)
    humidity_recorded = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert action to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'user_id': self.user_id,
            'action_type': self.action_type,
            'description': self.description,
            'weight_change': self.weight_change,
            'temperature_recorded': self.temperature_recorded,
            'humidity_recorded': self.humidity_recorded,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class FermentationStage(db.Model):
    """Fermentation stage tracking"""
    __tablename__ = 'fermentation_stages'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    batch_id = db.Column(db.String(36), db.ForeignKey('batches.id'), nullable=False)
    stage_name = db.Column(db.String(50), nullable=False)  # autolyse, bulk_ferment, proof, etc.
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    target_duration_hours = db.Column(db.Float)  # Target duration in hours
    temperature_target = db.Column(db.Float)  # Target temperature
    humidity_target = db.Column(db.Float)  # Target humidity
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        """Convert fermentation stage to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'stage_name': self.stage_name,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'target_duration_hours': self.target_duration_hours,
            'temperature_target': self.temperature_target,
            'humidity_target': self.humidity_target,
            'notes': self.notes,
            'is_active': self.is_active
        }