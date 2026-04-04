/*
FermTrack - Fermentation Tracking System - Admin Panel JavaScript
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
*/

// Admin Panel JavaScript Functions
// This file contains all the admin panel functionality

// Admin tab management
function showAdminTab(tab, eventTarget = null) {
  // Hide all sections
  const sections = ['adminUsers', 'adminBakeries', 'adminBatches', 'adminRoles', 'adminApplications', 'adminVerification'];
  sections.forEach(sectionId => {
    const element = document.getElementById(sectionId);
    if (element) element.classList.add('hidden');
  });
  
  // Remove active class from all tabs
  document.querySelectorAll('.admin-tab').forEach(tabEl => tabEl.classList.remove('active'));
  
  // Show selected section and mark tab as active
  const targetSection = document.getElementById('admin' + tab.charAt(0).toUpperCase() + tab.slice(1));
  if (targetSection) targetSection.classList.remove('hidden');
  
  // Handle event target for marking active tab
  const target = eventTarget || (window.event && window.event.target);
  if (target && target.classList) {
    target.classList.add('active');
  } else {
    // Fallback: find the tab button by its onclick attribute
    const tabButtons = document.querySelectorAll('.admin-tab');
    tabButtons.forEach(button => {
      if (button.onclick && button.onclick.toString().includes(`'${tab}'`)) {
        button.classList.add('active');
      }
    });
  }
  
  // Load data for the selected tab
  switch(tab) {
    case 'users':
      refreshUsers();
      break;
    case 'bakeries':
      refreshBakeries();
      break;
    case 'batches':
      refreshBatches();
      break;
    case 'roles':
      refreshUserRoles();
      break;
    case 'applications':
      refreshApplications();
      break;
    case 'verification':
      refreshVerifications();
      break;
  }
}

// User Management Functions
async function refreshUsers() {
  try {
    showLoading('adminUsers');
    const response = await api('/api/auth/admin/users', 'GET');
    
    if (response.users) {
      displayUsers(response.users);
    }
    hideLoading('adminUsers');
  } catch (error) {
    hideLoading('adminUsers');
    console.error('Error loading users:', error);
    showMessage('Error loading users: ' + error.message, 'error');
  }
}

function displayUsers(users) {
  const container = document.getElementById('users-list');
  if (!container) return;
  
  if (users.length === 0) {
    container.innerHTML = '<div class="admin-empty">No users found</div>';
    return;
  }
  
  container.innerHTML = users.map(user => `
    <div class="admin-item">
      <div class="admin-item-info">
        <strong>${user.username}</strong>
        <div class="admin-item-meta">${user.email} • ID: ${user.id}</div>
        <div class="admin-item-meta">Active: ${user.is_active ? 'Yes' : 'No'}</div>
      </div>
      <div class="admin-item-actions">
        <button class="btn btn-small" onclick="toggleUserStatus('${user.id}', ${!user.is_active})">
          ${user.is_active ? 'Deactivate' : 'Activate'}
        </button>
        <button class="btn btn-danger btn-small" onclick="deleteUser('${user.id}')">Delete</button>
      </div>
    </div>
  `).join('');
}

async function toggleUserStatus(userId, newStatus) {
  try {
    await api(`/api/auth/admin/users/${userId}`, 'PUT', { is_active: newStatus });
    showMessage(`User ${newStatus ? 'activated' : 'deactivated'} successfully`, 'success');
    refreshUsers();
  } catch (error) {
    console.error('Error updating user:', error);
    showMessage('Error updating user: ' + error.message, 'error');
  }
}

async function deleteUser(userId) {
  if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
    return;
  }
  
  try {
    await api(`/api/auth/admin/users/${userId}`, 'DELETE');
    showMessage('User deleted successfully', 'success');
    refreshUsers();
  } catch (error) {
    console.error('Error deleting user:', error);
    showMessage('Error deleting user: ' + error.message, 'error');
  }
}

// Bakery Management Functions
async function refreshBakeries() {
  try {
    showLoading('adminBakeries');
    const response = await api('/api/auth/admin/bakeries', 'GET');
    
    if (response.bakeries) {
      displayBakeries(response.bakeries);
    }
    hideLoading('adminBakeries');
  } catch (error) {
    hideLoading('adminBakeries');
    console.error('Error loading bakeries:', error);
    showMessage('Error loading bakeries: ' + error.message, 'error');
  }
}

function displayBakeries(bakeries) {
  const container = document.getElementById('bakeries-list');
  if (!container) return;
  
  if (bakeries.length === 0) {
    container.innerHTML = '<div class="admin-empty">No bakeries found</div>';
    return;
  }
  
  container.innerHTML = bakeries.map(bakery => `
    <div class="admin-item">
      <div class="admin-item-info">
        <strong>${bakery.name}</strong>
        <div class="admin-item-meta">${bakery.slug} • ID: ${bakery.id}</div>
        <div class="admin-item-meta">Active: ${bakery.is_active ? 'Yes' : 'No'}</div>
        ${bakery.description ? `<div class="admin-item-meta">${bakery.description}</div>` : ''}
      </div>
      <div class="admin-item-actions">
        <button class="btn btn-small" onclick="toggleBakeryStatus('${bakery.id}', ${!bakery.is_active})">
          ${bakery.is_active ? 'Deactivate' : 'Activate'}
        </button>
        <button class="btn btn-danger btn-small" onclick="deleteBakery('${bakery.id}')">Delete</button>
      </div>
    </div>
  `).join('');
}

async function toggleBakeryStatus(bakeryId, newStatus) {
  try {
    await api(`/api/auth/admin/bakeries/${bakeryId}`, 'PUT', { is_active: newStatus });
    showMessage(`Bakery ${newStatus ? 'activated' : 'deactivated'} successfully`, 'success');
    refreshBakeries();
  } catch (error) {
    console.error('Error updating bakery:', error);
    showMessage('Error updating bakery: ' + error.message, 'error');
  }
}

async function deleteBakery(bakeryId) {
  if (!confirm('Are you sure you want to delete this bakery? This will also delete all associated data and cannot be undone.')) {
    return;
  }
  
  try {
    await api(`/api/auth/admin/bakeries/${bakeryId}`, 'DELETE');
    showMessage('Bakery deleted successfully', 'success');
    refreshBakeries();
  } catch (error) {
    console.error('Error deleting bakery:', error);
    showMessage('Error deleting bakery: ' + error.message, 'error');
  }
}

// Batch Management Functions
async function refreshBatches() {
  try {
    showLoading('adminBatches');
    let url = '/api/auth/admin/batches';
    const response = await api(url, 'GET');
    
    if (response.batches) {
      displayBatches(response.batches);
    }
    hideLoading('adminBatches');
  } catch (error) {
    hideLoading('adminBatches');
    console.error('Error loading batches:', error);
    showMessage('Error loading batches: ' + error.message, 'error');
  }
}

function displayBatches(batches) {
  const container = document.getElementById('batches-list');
  if (!container) return;
  
  if (batches.length === 0) {
    container.innerHTML = '<div class="admin-empty">No batches found</div>';
    return;
  }
  
  container.innerHTML = batches.map(batch => `
    <div class="admin-item">
      <div class="admin-item-info">
        <strong>${batch.name}</strong>
        <div class="admin-item-meta">ID: ${batch.id} • Bakery: ${batch.bakery_name || batch.bakery_id}</div>
        <div class="admin-item-meta">Type: ${batch.type} • Status: ${batch.status}</div>
        ${batch.description ? `<div class="admin-item-meta">${batch.description}</div>` : ''}
      </div>
      <div class="admin-item-actions">
        <button class="btn btn-danger btn-small" onclick="deleteBatch('${batch.id}')">Delete</button>
      </div>
    </div>
  `).join('');
}

async function deleteBatch(batchId) {
  if (!confirm('Are you sure you want to delete this batch? This action cannot be undone.')) {
    return;
  }
  
  try {
    await api(`/api/auth/admin/batches/${batchId}`, 'DELETE');
    showMessage('Batch deleted successfully', 'success');
    refreshBatches();
  } catch (error) {
    console.error('Error deleting batch:', error);
    showMessage('Error deleting batch: ' + error.message, 'error');
  }
}

// User Role Management Functions
async function refreshUserRoles() {
  try {
    showLoading('adminUserRoles');
    const response = await api('/api/auth/admin/user-roles', 'GET');
    
    if (response.user_roles) {
      displayUserRoles(response.user_roles);
    }
    hideLoading('adminUserRoles');
  } catch (error) {
    hideLoading('adminUserRoles');
    console.error('Error loading user roles:', error);
    showMessage('Error loading user roles: ' + error.message, 'error');
  }
}

function displayUserRoles(userRoles) {
  const container = document.getElementById('user-roles-list');
  if (!container) return;
  
  if (userRoles.length === 0) {
    container.innerHTML = '<div class="admin-empty">No user roles found</div>';
    return;
  }
  
  container.innerHTML = userRoles.map(role => `
    <div class="admin-item">
      <div class="admin-item-info">
        <strong>${role.username} @ ${role.bakery_name}</strong>
        <div class="admin-item-meta">Role: ${role.role} • User ID: ${role.user_id}</div>
        <div class="admin-item-meta">Bakery: ${role.bakery_name} (${role.bakery_id})</div>
        <div class="admin-item-meta">Active: ${role.is_active ? 'Yes' : 'No'}</div>
      </div>
      <div class="admin-item-actions">
        <select onchange="updateUserRole('${role.user_id}', '${role.bakery_id}', this.value)" style="margin-right: 5px;">
          <option value="baker" ${role.role === 'baker' ? 'selected' : ''}>Baker</option>
          <option value="admin" ${role.role === 'admin' ? 'selected' : ''}>Admin</option>
        </select>
        <button class="btn btn-danger btn-small" onclick="removeUserRole('${role.user_id}', '${role.bakery_id}')">Remove</button>
      </div>
    </div>
  `).join('');
}

async function updateUserRole(userId, bakeryId, newRole) {
  try {
    await api(`/api/auth/admin/user-roles`, 'PUT', {
      user_id: userId,
      bakery_id: bakeryId,
      role: newRole
    });
    showMessage('User role updated successfully', 'success');
    refreshUserRoles();
  } catch (error) {
    console.error('Error updating user role:', error);
    showMessage('Error updating user role: ' + error.message, 'error');
  }
}

async function removeUserRole(userId, bakeryId) {
  if (!confirm('Are you sure you want to remove this user role?')) {
    return;
  }
  
  try {
    await api(`/api/auth/admin/user-roles`, 'DELETE', {
      user_id: userId,
      bakery_id: bakeryId
    });
    showMessage('User role removed successfully', 'success');
    refreshUserRoles();
  } catch (error) {
    console.error('Error removing user role:', error);
    showMessage('Error removing user role: ' + error.message, 'error');
  }
}

// Admin authentication functions
async function adminLogin() {
  const username = document.getElementById('adminUsername').value.trim();
  const password = document.getElementById('adminPassword').value;
  
  if (!username || !password) {
    showMessage('Please enter both username and password', 'error');
    return;
  }
  
  try {
    const response = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username,
        password: password
        // No bakery_slug for global admin login
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Store token and user data
      authToken = data.access_token;
      localStorage.setItem('fermtrack_token', authToken);
      currentUser = data.user;
      
      // Check if user is a global admin
      if (currentUser.is_global_admin) {
        // Close admin login modal and show admin panel
        closeAdminLoginModal();
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('registerForm').classList.add('hidden');
        document.getElementById('adminPanel').classList.remove('hidden');
        
        // For global admins, no specific bakery is set
        currentBakery = null;
        localStorage.removeItem('fermtrack_current_bakery');
        
        showMessage('Global admin login successful', 'success');
        
        // Load initial admin data
        showAdminTab('users');
        refreshUsers();
      } else {
        showMessage('Global admin access required. You do not have global admin privileges.', 'error');
        localStorage.removeItem('fermtrack_token');
      }
    } else {
      showMessage(data.error || 'Invalid credentials', 'error');
    }
  } catch (error) {
    console.error('Error during admin login:', error);
    showMessage('Login failed: ' + error.message, 'error');
  }
}

// Admin logout
function adminLogout() {
  localStorage.removeItem('token');
  document.getElementById('adminPanel').classList.add('hidden');
  document.getElementById('loginForm').classList.remove('hidden');
  showMessage('Logged out successfully', 'success');
}

// Initialize admin panel when loaded
function initializeAdminPanel() {
  // Load users by default when admin panel is shown
  if (!document.getElementById('adminPanel').classList.contains('hidden')) {
    showAdminTab('users');
  }
}

// ==================== APPLICATION MANAGEMENT ====================

async function refreshApplications() {
  try {
    showLoading('adminApplications');
    const response = await api('/api/auth/admin/applications', 'GET');
    
    if (response.applications) {
      displayApplications(response.applications);
    }
    hideLoading('adminApplications');
  } catch (error) {
    hideLoading('adminApplications');
    console.error('Error loading applications:', error);
    showMessage('Error loading applications: ' + error.message, 'error');
  }
}

function displayApplications(applications) {
  const tbody = document.getElementById('applicationsTableBody');
  if (!tbody) return;
  
  if (applications.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="admin-empty">No applications found</td></tr>';
    return;
  }
  
  const statusFilter = document.getElementById('applicationStatusFilter').value;
  const filteredApplications = statusFilter ? 
    applications.filter(app => app.status === statusFilter) : 
    applications;
  
  tbody.innerHTML = filteredApplications.map(application => {
    const statusClass = application.status === 'pending' ? 'warning' : 
                       application.status === 'approved' ? 'success' : 'danger';
    
    return `
      <tr>
        <td>${application.user ? application.user.username : 'Unknown'}</td>
        <td>${application.bakery ? application.bakery.name : 'Unknown'}</td>
        <td>${application.requested_role}</td>
        <td><span class="status-badge status-${statusClass}">${application.status}</span></td>
        <td>${new Date(application.created_at).toLocaleDateString()}</td>
        <td title="${application.message || 'No message'}">${
          application.message ? 
          (application.message.length > 50 ? application.message.substring(0, 50) + '...' : application.message) 
          : '-'
        }</td>
        <td class="admin-actions-cell">
          ${application.status === 'pending' ? `
            <button class="btn btn-success btn-small" onclick="reviewApplication('${application.id}', 'approved')">
              <i class="fas fa-check"></i> Approve
            </button>
            <button class="btn btn-danger btn-small" onclick="reviewApplication('${application.id}', 'rejected')">
              <i class="fas fa-times"></i> Reject
            </button>
          ` : `
            <span class="text-muted">Reviewed ${application.reviewed_at ? 'on ' + new Date(application.reviewed_at).toLocaleDateString() : ''}</span>
          `}
        </td>
      </tr>
    `;
  }).join('');
}

async function reviewApplication(applicationId, status) {
  const action = status === 'approved' ? 'approve' : 'reject';
  const notes = prompt(`${action === 'approve' ? 'Approval' : 'Rejection'} notes (optional):`);
  
  if (notes === null) return; // User cancelled
  
  try {
    const response = await api(`/api/auth/admin/applications/${applicationId}`, 'PUT', {
      status: status,
      admin_notes: notes || ''
    });
    
    showMessage(`Application ${action}d successfully`, 'success');
    refreshApplications();
  } catch (error) {
    console.error(`Error ${action}ing application:`, error);
    showMessage(`Error ${action}ing application: ` + error.message, 'error');
  }
}

// ==================== BAKERY VERIFICATION ====================

async function refreshVerifications() {
  try {
    showLoading('adminVerification');
    const response = await api('/api/bakeries/verification/pending', 'GET');
    
    if (response.pending_bakeries) {
      displayVerifications(response.pending_bakeries);
    }
    hideLoading('adminVerification');
  } catch (error) {
    hideLoading('adminVerification');
    console.error('Error loading pending verifications:', error);
    showMessage('Error loading pending verifications: ' + error.message, 'error');
  }
}

function displayVerifications(bakeries) {
  const tbody = document.getElementById('verificationsTableBody');
  if (!tbody) return;
  
  if (bakeries.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="admin-empty">No pending verifications</td></tr>';
    return;
  }
  
  tbody.innerHTML = bakeries.map(bakery => {
    const statusClass = bakery.verification_status === 'pending' ? 'warning' : 
                       bakery.verification_status === 'approved' ? 'success' : 'danger';
    
    return `
      <tr>
        <td>${bakery.name}</td>
        <td>${bakery.slug}</td>
        <td><span class="status-badge status-${statusClass}">${bakery.verification_status}</span></td>
        <td>${new Date(bakery.created_at).toLocaleDateString()}</td>
        <td title="${bakery.description || 'No description'}">${
          bakery.description ? 
          (bakery.description.length > 50 ? bakery.description.substring(0, 50) + '...' : bakery.description) 
          : '-'
        }</td>
        <td class="admin-actions-cell">
          ${bakery.verification_status === 'pending' ? `
            <button class="btn btn-success btn-small" onclick="verifyBakery('${bakery.id}', 'approved')">
              <i class="fas fa-check"></i> Approve
            </button>
            <button class="btn btn-danger btn-small" onclick="verifyBakery('${bakery.id}', 'rejected')">
              <i class="fas fa-times"></i> Reject
            </button>
          ` : `
            <span class="text-muted">Already processed</span>
          `}
        </td>
      </tr>
    `;
  }).join('');
}

async function verifyBakery(bakeryId, status) {
  const action = status === 'approved' ? 'approve' : 'reject';
  const notes = prompt(`${action === 'approve' ? 'Approval' : 'Rejection'} notes (optional):`);
  
  if (notes === null) return; // User cancelled
  
  try {
    const response = await api(`/api/bakeries/${bakeryId}/verification`, 'PUT', {
      verification_status: status,
      verification_notes: notes || ''
    });
    
    showMessage(`Bakery ${action}d successfully`, 'success');
    refreshVerifications();
  } catch (error) {
    console.error(`Error ${action}ing bakery:`, error);
    showMessage(`Error ${action}ing bakery: ` + error.message, 'error');
  }
}

// Helper function for loading states
function showLoading(section) {
  // Implementation depends on how you want to show loading states
  console.log(`Loading ${section}...`);
}

function hideLoading(section) {
  // Implementation depends on how you want to hide loading states
  console.log(`Finished loading ${section}`);
}

// User add/edit functions
function showAddUser() {
  document.getElementById('addUserModal').style.display = 'block';
  // Clear the form
  document.getElementById('addUserForm').reset();
}

function hideAddUser() {
  document.getElementById('addUserModal').style.display = 'none';
}

async function addUser() {
  const form = document.getElementById('addUserForm');
  const formData = new FormData(form);
  
  const userData = {
    username: formData.get('username'),
    email: formData.get('email'),
    password: formData.get('password'),
    is_active: formData.get('is_active') === 'on'
  };
  
  try {
    const response = await api('/api/auth/admin/users', 'POST', userData);
    
    if (response.success) {
      showMessage('User added successfully', 'success');
      hideAddUser();
      refreshUsers();
    } else {
      showMessage(response.error || 'Failed to add user', 'error');
    }
  } catch (error) {
    console.error('Error adding user:', error);
    showMessage('Error adding user: ' + error.message, 'error');
  }
}

// Make functions available globally for HTML onclick handlers
window.adminLogin = adminLogin;
window.showAdminTab = showAdminTab;
window.showAddUser = showAddUser;
window.hideAddUser = hideAddUser;
window.addUser = addUser;
window.refreshUsers = refreshUsers;
