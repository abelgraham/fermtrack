#!/usr/bin/env python3
"""
FermTrack - Fermentation Tracking System - Middleware
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

from flask import request, g, jsonify, current_app
from functools import wraps
from models import Bakery, db
import re

class TenantMiddleware:
    """Middleware to handle multi-tenant bakery resolution from subdomains"""
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with the Flask app"""
        app.before_request(self.extract_bakery_context)
    
    def extract_bakery_context(self):
        """Extract bakery context from subdomain before each request"""
        # Skip for certain routes (health checks, etc.)
        if request.endpoint in ['health_check', 'api_info', 'auth.list_available_bakeries']:
            return
            
        # Get host from request
        host = request.host.lower()
        
        # Extract subdomain (everything before the main domain)
        # Supports patterns like: bakery1.fermtrack.com, localhost, 127.0.0.1, bakery1.localhost
        parts = host.split('.')
        
        if len(parts) >= 2 and not self._is_ip_address(host):
            # Extract potential bakery slug from subdomain
            bakery_slug = parts[0]
            
            # Skip common non-tenant subdomains
            if bakery_slug in ['www', 'api', 'admin']:
                bakery_slug = None
        else:
            # For localhost, IP addresses, or no subdomain, try header fallback
            bakery_slug = request.headers.get('X-Bakery-Slug')
            
            # For development, allow a default bakery
            if not bakery_slug and current_app.config.get('FLASK_ENV') == 'development':
                bakery_slug = 'demo'
        
        # Resolve bakery from database
        if bakery_slug:
            try:
                # Import here to avoid circular imports and ensure proper app context
                from models import Bakery
                bakery = Bakery.query.filter_by(slug=bakery_slug, is_active=True).first()
                if bakery:
                    g.current_bakery = bakery
                    g.bakery_id = bakery.id
                    g.bakery_slug = bakery.slug
                    return
            except Exception as e:
                # Log the error but don't crash the request
                current_app.logger.error(f"Error resolving bakery context: {e}")
        
        # No valid bakery found
        g.current_bakery = None
        g.bakery_id = None
        g.bakery_slug = None
    
    def _is_ip_address(self, host):
        """Check if host is an IP address"""
        # Remove port if present
        host = host.split(':')[0]
        
        # Check for IPv4 pattern
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        return bool(re.match(ip_pattern, host))

def require_bakery(f):
    """Decorator to require valid bakery context for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'current_bakery') or g.current_bakery is None:
            # Try to provide helpful info for frontend
            from flask_jwt_extended import get_jwt_identity, jwt_required
            try:
                # Check if user is authenticated
                current_user_id = get_jwt_identity()
                if current_user_id:
                    from models import User
                    user = User.query.get(current_user_id)
                    if user:
                        user_bakeries = [{'slug': ub.bakery.slug, 'name': ub.bakery.name} 
                                       for ub in user.user_bakeries if ub.is_active]
                        return jsonify({
                            'error': 'No bakery context provided',
                            'code': 'MISSING_BAKERY_CONTEXT',
                            'message': 'Please select a bakery to continue',
                            'available_bakeries': user_bakeries,
                            'instructions': 'Add X-Bakery-Slug header with bakery slug'
                        }), 400
            except:
                pass
            
            return jsonify({
                'error': 'Invalid or missing bakery context',
                'message': 'Please access via a valid bakery subdomain (e.g., bakery1.fermtrack.com)'
            }), 400
        return f(*args, **kwargs)
    return decorated_function

def get_current_bakery():
    """Helper function to get current bakery from request context"""
    return getattr(g, 'current_bakery', None)

def get_current_bakery_id():
    """Helper function to get current bakery ID from request context"""
    return getattr(g, 'bakery_id', None)