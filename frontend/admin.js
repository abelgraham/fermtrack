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

// DOM debugging helper
function debugDOMElements() {
  console.log('🔍 DOM Debug - Starting element inspection');
  
  // Check if we're in an iframe or different context
  console.log('Document context:', document === window.document);
  
  // Find all tbody elements
  const allTbodies = document.querySelectorAll('tbody');
  console.log('All tbody elements found:', allTbodies.length);
  
  allTbodies.forEach((tbody, index) => {
    console.log(`tbody ${index + 1}:`, {
      id: tbody.id || 'NO ID',
      className: tbody.className,
      parentId: tbody.parentElement?.id || 'NO PARENT ID',
      innerHTML: tbody.innerHTML.substring(0, 100) + '...'
    });
  });
  
  // Check specifically for our target IDs
  const targetIds = ['usersTableBody', 'bakeriesTableBody', 'batchesTableBody', 
                     'applicationsTableBody', 'verificationsTableBody', 'rolesTableBody'];
  
  targetIds.forEach(id => {
    const byId = document.getElementById(id);
    const byQuery = document.querySelector(`#${id}`);
    console.log(`${id}:`, {
      getElementById: !!byId,
      querySelector: !!byQuery,
      match: byId === byQuery
    });
  });
  
  // Check admin sections
  const adminSections = ['adminUsers', 'adminBakeries', 'adminBatches', 
                        'adminApplications', 'adminVerification', 'adminRoles'];
  
  adminSections.forEach(sectionId => {
    const section = document.getElementById(sectionId);
    if (section) {
      const tbody = section.querySelector('tbody');
      console.log(`${sectionId} tbody:`, {
        exists: !!tbody,
        hasId: tbody?.id || 'NO ID',
        className: tbody?.className || 'NO CLASS'
      });
    }
  });
}

// DOM structure recreation helper
function ensureAdminSectionExists(sectionId, tbodyId, headers, colspan = 6) {
  console.log(`🔧 Ensuring ${sectionId} structure exists...`);
  
  let section = document.getElementById(sectionId);
  if (!section) {
    console.log(`❌ Section ${sectionId} not found, cannot recreate`);
    return false;
  }
  
  let tbody = document.getElementById(tbodyId);
  if (tbody) {
    console.log(`✅ ${tbodyId} already exists`);
    return true;
  }
  
  // Check if table structure exists in section
  let table = section.querySelector('table');
  if (!table) {
    console.log(`🔧 Recreating table structure for ${sectionId}`);
    const container = section.querySelector('.admin-table-container') || section;
    container.innerHTML = `
      <table class="admin-table">
        <thead>
          <tr>
            ${headers.map(h => `<th>${h}</th>`).join('')}
          </tr>
        </thead>
        <tbody id="${tbodyId}">
          <tr><td colspan="${colspan}" class="loading">Loading...</td></tr>
        </tbody>
      </table>
    `;
    console.log(`✅ Recreated table structure for ${sectionId}`);
    return true;
  } else {
    // Table exists but tbody is missing
    tbody = table.querySelector('tbody');
    if (!tbody) {
      console.log(`🔧 Adding missing tbody to ${sectionId}`);
      tbody = document.createElement('tbody');
      tbody.id = tbodyId;
      tbody.innerHTML = `<tr><td colspan="${colspan}" class="loading">Loading...</td></tr>`;
      table.appendChild(tbody);
      console.log(`✅ Added missing tbody to ${sectionId}`);
      return true;
    }
  }
  
  console.log(`✅ ${sectionId} structure verified`);
  return true;
}

// Check if updated admin.js loaded  
console.log('Admin.js loaded at', new Date().toISOString());

// Check DOM state when admin.js loads
console.log('🔍 DOM state at admin.js load time:', {
  readyState: document.readyState,
  adminSections: document.querySelectorAll('[id^="admin"]').length,
  tbodyElements: document.querySelectorAll('tbody').length,
  tableBodyElements: document.querySelectorAll('[id*="TableBody"]').length
});

// Wait for DOM to be ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 DOM now ready - rechecking elements:', {
      readyState: document.readyState,
      adminSections: document.querySelectorAll('[id^="admin"]').length,
      tbodyElements: document.querySelectorAll('tbody').length,
      tableBodyElements: document.querySelectorAll('[id*="TableBody"]').length
    });
  });
}

// Debug function to check DOM elements
window.debugAdminDOM = function() {
  console.log('🐞 Admin DOM Debug Report:');
  const containers = [
    'adminPanel', 'adminUsers', 'adminBakeries', 'adminBatches', 
    'adminRoles', 'adminApplications', 'adminVerification',
    'usersTableBody', 'bakeriesTableBody', 'batchesTableBody',
    'rolesTableBody', 'applicationsTableBody', 'verificationsTableBody'
  ];
  
  containers.forEach(id => {
    const element = document.getElementById(id);
    console.log(`${id}:`, element ? '✅ EXISTS' : '❌ MISSING');
    if (element) {
      console.log(`  - tagName: ${element.tagName}, classes: ${element.className}`);
    }
  });
  
  console.log('All tbody elements in document:');
  document.querySelectorAll('tbody').forEach((tbody, i) => {
    console.log(`  tbody[${i}]: id="${tbody.id}", parent="${tbody.parentElement.tagName}"`);
  });
};
// This file contains all the admin panel functionality

// Initialize admin security - called on page load and logout
function initializeAdminSecurity() {
  console.log('Initializing admin security checks...');
  
  // Only disable admin functions if we detect a previous session that's now invalid
  // Don't disable on fresh page load when user hasn't tried to login yet
  const hadPreviousSession = localStorage.getItem('fermtrack_token') !== null;
  const hasValidAuth = window.isAppInitialized && 
                      window.currentUser && 
                      window.currentUser.is_global_admin && 
                      (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (hadPreviousSession && !hasValidAuth) {
    console.log('Previous session detected but authentication invalid - disabling admin functions');
    disableAdminTabs();
  } else if (!hadPreviousSession) {
    console.log('No previous session detected - keeping admin functions available for login');
  } else {
    console.log('Valid admin authentication detected - admin functions remain enabled');
  }
}

// Function to enable admin tabs after successful authentication
function enableAdminTabs() {
  console.log('Enabling admin tabs for authenticated global admin');
  
  // Re-enable all admin tab buttons
  const adminTabButtons = document.querySelectorAll('#adminTabs button, .admin-tab, .admin-nav button');
  adminTabButtons.forEach(button => {
    button.disabled = false;
    button.style.opacity = '1';
    button.style.pointerEvents = 'auto';
  });
  
  // Show the admin navigation
  const adminTabs = document.getElementById('adminTabs');
  if (adminTabs) {
    adminTabs.style.display = 'block';
    adminTabs.classList.remove('hidden');
  }
  
  // Show admin panel if hidden
  const adminPanel = document.getElementById('adminPanel');
  if (adminPanel) {
    adminPanel.style.display = 'block';
    adminPanel.classList.remove('hidden');
    // Add body class for layout management
    document.body.classList.add('admin-open');
  }
}

// Call on script load
document.addEventListener('DOMContentLoaded', initializeAdminSecurity);
// Also call immediately in case DOMContentLoaded already fired
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeAdminSecurity);
} else {
  initializeAdminSecurity();
}

// Admin tab management
async function showAdminTab(tab, eventTarget = null) {
  console.log('showAdminTab called for:', tab);
  
  // Check for valid admin authentication - allow if user is global admin even if app not fully initialized
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  // IMMEDIATE AUTHENTICATION CHECK - fail fast only if no valid admin auth
  if (!hasValidAdminAuth) {
    console.warn('showAdminTab: No valid admin authentication - blocking immediately');
    // Disable admin functions to prevent repeated calls
    disableAdminTabs();
    return;
  }
  
  // If we have valid admin auth but app not initialized, mark it as initialized for admin session
  if (!window.isAppInitialized) {
    console.log('Setting app as initialized for admin session');
    window.isAppInitialized = true;
  }
  
  console.log('showAdminTab: Valid admin authentication found, proceeding with tab:', tab);
  
  // Hide all sections
  const sections = ['adminUsers', 'adminBakeries', 'adminBatches', 'adminRoles', 'adminApplications', 'adminVerification'];
  sections.forEach(sectionId => {
    const element = document.getElementById(sectionId);
    if (element) element.classList.add('hidden');
  });
  
  // Remove active class from all tabs
  document.querySelectorAll('.admin-tab').forEach(tabEl => tabEl.classList.remove('active'));
  
  // Show selected section and mark tab as active
  const targetSectionId = 'admin' + tab.charAt(0).toUpperCase() + tab.slice(1);
  console.log('Looking for section with ID:', targetSectionId);
  const targetSection = document.getElementById(targetSectionId);
  console.log('Target section found:', !!targetSection);
  if (targetSection) {
    targetSection.classList.remove('hidden');
    console.log('Removed hidden class from section:', targetSectionId);
    
    // PROACTIVE DOM STRUCTURE CHECK: Ensure table structures exist before data loading
    console.log('🔧 Proactive DOM check for', tab);
    switch(tab) {
      case 'users':
        ensureAdminSectionExists('adminUsers', 'usersTableBody', 
          ['ID', 'Username', 'Email', 'Active', 'Created', 'Actions'], 6);
        break;
      case 'bakeries':
        ensureAdminSectionExists('adminBakeries', 'bakeriesTableBody', 
          ['ID', 'Name', 'Slug', 'Active', 'Description', 'Actions'], 6);
        break;
      case 'batches':
        ensureAdminSectionExists('adminBatches', 'batchesTableBody', 
          ['ID', 'Name', 'Bakery', 'Status', 'Created', 'Actions'], 6);
        break;
      case 'applications':
        ensureAdminSectionExists('adminApplications', 'applicationsTableBody', 
          ['User', 'Bakery', 'Role Requested', 'Status', 'Applied', 'Message', 'Actions'], 7);
        break;
      case 'verification':
        ensureAdminSectionExists('adminVerification', 'verificationsTableBody', 
          ['Bakery Name', 'Slug', 'Status', 'Created', 'Description', 'Actions'], 6);
        break;
      case 'roles':
        // User roles has a slightly different structure, check if it needs fixing
        if (!document.getElementById('rolesTableBody')) {
          ensureAdminSectionExists('adminRoles', 'rolesTableBody', 
            ['User', 'Bakery', 'Role', 'Active', 'Actions'], 5);
        }
        break;
    }
  }
  
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
  
  // Load data for the selected tab (now with proper initialization)
  console.log('About to load data for tab:', tab);
  switch(tab) {
    case 'users':
      console.log('Switch: calling refreshUsers()');
      refreshUsers();
      break;
    case 'bakeries':
      console.log('Switch: calling refreshBakeries()');
      refreshBakeries();
      break;
    case 'batches':
      console.log('Switch: calling refreshBatches()');
      refreshBatches();
      break;
    case 'roles':
      console.log('Switch: calling refreshUserRoles()');
      refreshUserRoles();
      break;
    case 'applications':
      console.log('Switch: calling refreshApplications()');
      refreshApplications();
      break;
    case 'verification':
      console.log('Switch: calling refreshVerifications()');
      refreshVerifications();
      break;
    default:
      console.warn('Unknown tab:', tab);
  }
}

// User Management Functions
async function refreshUsers() {
  console.log('refreshUsers called - checking authentication state');
  
  // Debug DOM elements when loading users
  debugDOMElements();
  
  // Check for valid admin auth, auto-initialize app if needed
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (!hasValidAdminAuth) {
    console.warn('Cannot load users: No valid admin authentication');
    return;
  }
  
  if (!window.isAppInitialized) {
    console.log('Auto-initializing app for admin refreshUsers');
    window.isAppInitialized = true;
  }
  
  // Check both window and localStorage tokens with validation
  const windowToken = window.authToken;
  const storedToken = localStorage.getItem('fermtrack_token');
  const validStoredToken = storedToken && storedToken.trim() && storedToken !== '' && storedToken !== 'null' ? storedToken : null;
  const currentToken = windowToken || validStoredToken;
  
  console.log('refreshUsers token check:', {
    windowToken: !!windowToken,
    rawStorageToken: !!storedToken,
    validStorageToken: !!validStoredToken,
    finalToken: !!currentToken,
    currentUser: !!window.currentUser,
    isGlobalAdmin: window.currentUser?.is_global_admin
  });
  
  if (!currentToken) {
    console.warn('Cannot load users: No valid authentication token');
    showMessage('Authentication required. Please log in again.', 'error');
    return;
  }
  
  try {
    showLoading('adminUsers');
    console.log('Making API call to /api/auth/admin/users...');
    const response = await api('/api/auth/admin/users', 'GET');
    console.log('Users API response:', response);
    
    if (response.users) {
      console.log('Displaying', response.users.length, 'users');
      displayUsers(response.users);
    } else {
      console.log('No users property in response');
    }
    hideLoading('adminUsers');
  } catch (error) {
    hideLoading('adminUsers');
    console.error('Error loading users:', error);
    
    // If authentication error, clear tokens and disable admin functions
    if (error.message.includes('authentication') || error.message.includes('expired') || error.message.includes('token') || error.message.includes('session')) {
      console.log('Authentication error detected - clearing tokens and disabling admin');
      localStorage.removeItem('fermtrack_token');
      window.authToken = null;
      window.currentUser = null;
      if (typeof disableAdminTabs === 'function') {
        disableAdminTabs();
      }
    }
    
    showMessage('Error loading users: ' + error.message, 'error');
  }
}

function displayUsers(users) {
  console.log('🔍 displayUsers called with', users.length, 'users');
  
  // FIRST: Ensure the DOM structure exists
  ensureAdminSectionExists('adminUsers', 'usersTableBody', [
    'ID', 'Username', 'Email', 'Active', 'Created', 'Actions'
  ], 6);
  
  // Try multiple approaches to find the container
  let container = document.getElementById('usersTableBody');
  
  if (!container) {
    // Try finding by querySelector
    container = document.querySelector('#usersTableBody');
    console.log('📦 Found via querySelector:', !!container);
  }
  
  if (!container) {
    // Try finding within admin users section
    const adminUsers = document.getElementById('adminUsers');
    if (adminUsers) {
      container = adminUsers.querySelector('tbody');
      console.log('📦 Found tbody in adminUsers section:', !!container);
      if (container && !container.id) {
        container.id = 'usersTableBody'; // Set the ID if missing
        console.log('📦 Set missing ID on tbody');
      }
    }
  }
  
  if (!container) {
    console.error('❌ usersTableBody container not found after all attempts!');
    return;
  }
  
  console.log('📦 Users container found:', !!container, 'ID:', container.id);
  if (users.length === 0) {
    container.innerHTML = '<tr><td colspan="6" class="admin-empty">No users found</td></tr>';
    console.log('📝 Set "no users" message');
    return;
  }
  
  console.log('📝 Building HTML for', users.length, 'users');
  const html = users.map(user => `
    <tr>
      <td>${user.id.substring(0, 8)}...</td>
      <td><strong>${user.username}</strong></td>
      <td>${user.email}</td>
      <td>
        <span class="status-badge ${user.is_active ? 'active' : 'inactive'}">
          ${user.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td>${new Date(user.created_at).toLocaleDateString()}</td>
      <td>
        <button class="btn btn-small ${user.is_active ? 'btn-warning' : 'btn-success'}" 
                onclick="toggleUserStatus('${user.id}', ${!user.is_active})">
          ${user.is_active ? 'Deactivate' : 'Activate'}
        </button>
        <button class="btn btn-danger btn-small" onclick="deleteUser('${user.id}')">Delete</button>
      </td>
    </tr>
  `).join('');
  
  container.innerHTML = html;
  console.log('✅ Successfully set users table:', container.children.length, 'rows added');
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
  console.log('🔍 refreshBakeries called - checking authentication state');
  
  // Debug DOM elements when loading bakeries
  debugDOMElements();
  
  // Check for valid admin auth, auto-initialize app if needed
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (!hasValidAdminAuth) {
    console.warn('Cannot load bakeries: No valid admin authentication');
    return;
  }
  
  if (!window.isAppInitialized) {
    console.log('Auto-initializing app for admin refreshBakeries');
    window.isAppInitialized = true;
  }
  
  const currentToken = window.authToken || localStorage.getItem('fermtrack_token');
  const actualStorageToken = localStorage.getItem('fermtrack_token');
  
  if (!currentToken || !actualStorageToken) {
    console.warn('Cannot load bakeries: No valid authentication token');
    showMessage('Authentication required. Please log in again.', 'error');
    return;
  }
  
  try {
    showLoading('adminBakeries');
    console.log('🌐 Making API call to /api/auth/admin/bakeries...');
    const response = await api('/api/auth/admin/bakeries', 'GET');
    console.log('🔍 Bakeries API response:', response);
    
    if (response && response.bakeries) {
      console.log('✅ Displaying', response.bakeries.length, 'bakeries');
      displayBakeries(response.bakeries);
    } else {
      console.warn('⚠️ No bakeries data in response:', response);
      displayBakeries([]);
    }
    hideLoading('adminBakeries');
  } catch (error) {
    hideLoading('adminBakeries');
    console.error('Error loading bakeries:', error);
    showMessage('Error loading bakeries: ' + error.message, 'error');
  }
}

function displayBakeries(bakeries) {
  console.log('🔍 displayBakeries called with', bakeries.length, 'bakeries');
  
  // FIRST: Ensure the DOM structure exists
  ensureAdminSectionExists('adminBakeries', 'bakeriesTableBody', [
    'ID', 'Name', 'Slug', 'Active', 'Description', 'Actions'
  ], 6);
  
  // Try multiple approaches to find the container
  let container = document.getElementById('bakeriesTableBody');
  
  if (!container) {
    // Try finding by querySelector
    container = document.querySelector('#bakeriesTableBody');
    console.log('📦 Found via querySelector:', !!container);
  }
  
  if (!container) {
    // Try finding within admin bakeries section
    const adminBakeries = document.getElementById('adminBakeries');
    if (adminBakeries) {
      container = adminBakeries.querySelector('tbody');
      console.log('📦 Found tbody in adminBakeries section:', !!container);
      if (container && !container.id) {
        container.id = 'bakeriesTableBody'; // Set the ID if missing
        console.log('📦 Set missing ID on tbody');
      }
    }
  }
  
  if (!container) {
    console.error('❌ bakeriesTableBody container not found after all attempts!');
    return;
  }
  
  console.log('📦 Bakeries container found:', !!container, 'ID:', container.id);
  
  if (bakeries.length === 0) {
    container.innerHTML = '<tr><td colspan="6" class="admin-empty">No bakeries found</td></tr>';
    console.log('📝 Set "no bakeries" message');
    return;
  }
  
  console.log('📝 Building HTML for', bakeries.length, 'bakeries');
  const html = bakeries.map(bakery => `
    <tr>
      <td>${bakery.id.substring(0, 8)}...</td>
      <td><strong>${bakery.name}</strong></td>
      <td>${bakery.slug}</td>
      <td>${bakery.description || 'No description'}</td>
      <td>
        <span class="status-badge ${bakery.is_active ? 'active' : 'inactive'}">
          ${bakery.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td>
        <button class="btn btn-small ${bakery.is_active ? 'btn-warning' : 'btn-success'}" 
                onclick="toggleBakeryStatus('${bakery.id}', ${!bakery.is_active})">
          ${bakery.is_active ? 'Deactivate' : 'Activate'}
        </button>
        <button class="btn btn-danger btn-small" onclick="deleteBakery('${bakery.id}')">Delete</button>
      </td>
    </tr>
  `).join('');
  
  container.innerHTML = html;
  console.log('✅ Successfully set bakeries table:', container.children.length, 'rows added');
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
  console.log('refreshBatches called - checking authentication state');
  
  // Check for valid admin auth, auto-initialize app if needed
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (!hasValidAdminAuth) {
    console.warn('Cannot load batches: No valid admin authentication');
    return;
  }
  
  if (!window.isAppInitialized) {
    console.log('Auto-initializing app for admin refreshBatches');
    window.isAppInitialized = true;
  }
  
  const currentToken = window.authToken || localStorage.getItem('fermtrack_token');
  const actualStorageToken = localStorage.getItem('fermtrack_token');
  
  if (!currentToken || !actualStorageToken) {
    console.warn('Cannot load batches: No valid authentication token');
    showMessage('Authentication required. Please log in again.', 'error');
    return;
  }
  
  try {
    showLoading('adminBatches');
    let url = '/api/auth/admin/batches';
    console.log('Making API call to', url);
    const response = await api(url, 'GET');
    console.log('Batches API response:', response);
    
    if (response.batches) {
      console.log('Displaying', response.batches.length, 'batches');
      displayBatches(response.batches);
    } else {
      console.log('No batches property in response');
    }
    hideLoading('adminBatches');
  } catch (error) {
    hideLoading('adminBatches');
    console.error('Error loading batches:', error);
    showMessage('Error loading batches: ' + error.message, 'error');
  }
}

function displayBatches(batches) {
  console.log('displayBatches called with', batches.length, 'batches');
  
  // FIRST: Ensure the DOM structure exists
  ensureAdminSectionExists('adminBatches', 'batchesTableBody', [
    'ID', 'Name', 'Bakery', 'Status', 'Created', 'Actions'
  ], 6);
  
  // Try multiple approaches to find the container
  let container = document.getElementById('batchesTableBody');
  
  if (!container) {
    container = document.querySelector('#batchesTableBody');
    console.log('📦 Found via querySelector:', !!container);
  }
  
  if (!container) {
    const adminBatches = document.getElementById('adminBatches');
    if (adminBatches) {
      container = adminBatches.querySelector('tbody');
      console.log('📦 Found tbody in adminBatches section:', !!container);
      if (container && !container.id) {
        container.id = 'batchesTableBody';
        console.log('📦 Set missing ID on tbody');
      }
    }
  }
  
  if (!container) {
    console.error('❌ batchesTableBody container not found!');
    return;
  }
  
  if (batches.length === 0) {
    container.innerHTML = '<tr><td colspan="6" class="admin-empty">No batches found</td></tr>';
    return;
  }
  
  container.innerHTML = batches.map(batch => `
    <tr>
      <td>${batch.id.substring(0, 8)}...</td>
      <td><strong>${batch.recipe_name || batch.name || 'Unknown'}</strong></td>
      <td>${batch.bakery_name || 'Unknown'}</td>
      <td>
        <span class="status-badge ${batch.status === 'active' ? 'active' : 'inactive'}">
          ${batch.status || 'Unknown'}
        </span>
      </td>
      <td>${new Date(batch.start_time || batch.created_at).toLocaleDateString()}</td>
      <td>
        <button class="btn btn-primary btn-small" onclick="viewBatch('${batch.id}')">
          View
        </button>
        <button class="btn btn-danger btn-small" onclick="deleteBatch('${batch.id}')">Delete</button>
      </td>
    </tr>
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
  console.log('refreshUserRoles called - checking authentication state');
  
  // Debug DOM elements when loading user roles
  debugDOMElements();
  
  // Check for valid admin auth, auto-initialize app if needed
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (!hasValidAdminAuth) {
    console.warn('Cannot load user roles: No valid admin authentication');
    return;
  }
  
  if (!window.isAppInitialized) {
    console.log('Auto-initializing app for admin refreshUserRoles');
    window.isAppInitialized = true;
  }
  
  const currentToken = window.authToken || localStorage.getItem('fermtrack_token');
  const actualStorageToken = localStorage.getItem('fermtrack_token');
  
  if (!currentToken || !actualStorageToken) {
    console.warn('Cannot load user roles: No valid authentication token');
    showMessage('Authentication required. Please log in again.', 'error');
    return;
  }
  
  try {
    showLoading('adminRoles');
    console.log('Making API call to /api/auth/admin/user-roles...');
    const response = await api('/api/auth/admin/user-roles', 'GET');
    console.log('User roles API response:', response);
    
    if (response.user_roles) {
      console.log('Displaying', response.user_roles.length, 'user roles');
      displayUserRoles(response.user_roles);
    } else {
      console.log('No user_roles property in response');
    }
    hideLoading('adminRoles');
  } catch (error) {
    hideLoading('adminRoles');
    console.error('Error loading user roles:', error);
    showMessage('Error loading user roles: ' + error.message, 'error');
  }
}

function displayUserRoles(userRoles) {
  console.log('displayUserRoles called with', userRoles.length, 'user roles');
  
  // FIRST: Ensure the DOM structure exists
  ensureAdminSectionExists('adminRoles', 'rolesTableBody', [
    'User', 'Bakery', 'Role', 'Active', 'Actions'
  ], 5);
  
  const container = document.getElementById('rolesTableBody');
  if (!container) {
    console.error('❌ rolesTableBody container not found!');
    return;
  }
  
  if (userRoles.length === 0) {
    container.innerHTML = '<tr><td colspan="5" class="admin-empty">No user roles found</td></tr>';
    return;
  }
  
  container.innerHTML = userRoles.map(role => `
    <tr>
      <td><strong>${role.username || 'Unknown'}</strong></td>
      <td>${role.bakery_name || 'Unknown'}</td>
      <td>
        <span class="role-badge ${role.role}">
          ${role.role}
        </span>
      </td>
      <td>
        <span class="status-badge ${role.is_active ? 'active' : 'inactive'}">
          ${role.is_active ? 'Active' : 'Inactive'}
        </span>
      </td>
      <td>
        <select onchange="updateUserRole('${role.user_id}', '${role.bakery_id}', this.value)" class="btn btn-small">
          <option value="baker" ${role.role === 'baker' ? 'selected' : ''}>Baker</option>
          <option value="manager" ${role.role === 'manager' ? 'selected' : ''}>Manager</option>
          <option value="admin" ${role.role === 'admin' ? 'selected' : ''}>Admin</option>
        </select>
        <button class="btn btn-danger btn-small" onclick="removeUserRole('${role.user_id}', '${role.bakery_id}')">Remove</button>
      </td>
    </tr>
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
      window.authToken = data.access_token;
      localStorage.setItem('fermtrack_token', window.authToken);
      window.currentUser = data.user;
      
      // Check if user is a global admin
      if (window.currentUser.is_global_admin) {
        // Mark app as initialized for admin session
        window.isAppInitialized = true;
        
        // Re-enable admin tabs for successful authentication
        enableAdminTabs();
        
        // Close admin login modal and show admin panel
        closeAdminLoginModal();
        document.getElementById('loginForm').classList.add('hidden');
        document.getElementById('registerForm').classList.add('hidden');
        document.getElementById('adminPanel').classList.remove('hidden');
        
        // For global admins, no specific bakery is set
        window.currentBakery = null;
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
  localStorage.removeItem('fermtrack_token');
  localStorage.removeItem('fermtrack_current_bakery');
  window.authToken = null;
  window.currentUser = null;
  window.currentBakery = null;
  document.getElementById('adminPanel').classList.add('hidden');
  document.getElementById('loginForm').classList.remove('hidden');
  // Remove body class for layout management
  document.body.classList.remove('admin-open');
  showMessage('Logged out successfully', 'success');
}

// Initialize admin panel when loaded
function initializeAdminPanel() {
  // Load users by default when admin panel is shown
  if (!document.getElementById('adminPanel').classList.contains('hidden')) {
    showAdminTab('users');
  }
}

// Function to enable admin tabs after successful authentication
function enableAdminTabs() {
  console.log('Enabling admin tabs for authenticated global admin');
  
  // Enable all admin tab buttons
  const adminTabButtons = document.querySelectorAll('#adminTabs button');
  adminTabButtons.forEach(button => {
    button.disabled = false;
    button.style.opacity = '1';
  });
  
  // Show the admin navigation
  const adminTabs = document.getElementById('adminTabs');
  if (adminTabs) {
    adminTabs.style.display = 'block';
  }
}

// Function to disable admin tabs (for logout or unauthorized access)
function disableAdminTabs() {
  console.log('Disabling admin tabs and removing all event handlers');
  
  // Disable all admin tab buttons and remove event handlers completely
  const adminTabSelectors = [
    '#adminTabs button',
    '.admin-tab', 
    '.admin-nav button',
    '[onclick*="showAdminTab"]',
    '[onclick*="addUser"]',
    '[onclick*="openAddUserModal"]'
  ];
  
  adminTabSelectors.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
      element.disabled = true;
      element.style.opacity = '0.5';
      element.style.pointerEvents = 'none';
      // Remove all event handlers
      element.onclick = null;
      element.removeAttribute('onclick');
      // Clone and replace to remove all event listeners completely
      const newElement = element.cloneNode(true);
      if (element.parentNode) {
        element.parentNode.replaceChild(newElement, element);
      }
    });
  });
  
  // Hide the admin navigation completely
  const adminTabs = document.getElementById('adminTabs');
  if (adminTabs) {
    adminTabs.style.display = 'none';
    adminTabs.classList.add('hidden');
  }
  
  // Hide all admin content sections and panels
  const adminSelectors = [
    '[id^="admin"][id$="Content"]',
    '[id^="admin"][id*="Users"]',
    '[id^="admin"][id*="Bakeries"]', 
    '[id^="admin"][id*="Batches"]',
    '#adminPanel',
    '.admin-content'
  ];
  
  adminSelectors.forEach(selector => {
    const sections = document.querySelectorAll(selector);
    sections.forEach(section => {
      section.style.display = 'none';
      section.classList.add('hidden');
    });
  });
  
  // Hide any admin modals that might be open
  const adminModals = document.querySelectorAll('[id*="adminModal"], [id*="AddUserModal"]');
  adminModals.forEach(modal => {
    modal.style.display = 'none';
    modal.classList.add('hidden');
  });
  
  console.log('Admin tabs completely disabled and all handlers removed');
}

// ==================== APPLICATION MANAGEMENT ====================

async function refreshApplications() {
  console.log('refreshApplications called - checking authentication state');
  
  // Check for valid admin auth, auto-initialize app if needed
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (!hasValidAdminAuth) {
    console.warn('Cannot load applications: No valid admin authentication');
    return;
  }
  
  if (!window.isAppInitialized) {
    console.log('Auto-initializing app for admin refreshApplications');
    window.isAppInitialized = true;
  }
  
  const currentToken = window.authToken || localStorage.getItem('fermtrack_token');
  const actualStorageToken = localStorage.getItem('fermtrack_token');
  
  if (!currentToken || !actualStorageToken) {
    console.warn('Cannot load applications: No valid authentication token');
    showMessage('Authentication required. Please log in again.', 'error');
    return;
  }
  
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
  console.log('displayApplications called with', applications.length, 'applications');
  
  // FIRST: Ensure the DOM structure exists
  ensureAdminSectionExists('adminApplications', 'applicationsTableBody', [
    'User', 'Bakery', 'Role Requested', 'Status', 'Applied', 'Message', 'Actions'
  ], 7);
  
  // Try multiple approaches to find the container
  let tbody = document.getElementById('applicationsTableBody');
  
  if (!tbody) {
    tbody = document.querySelector('#applicationsTableBody');
    console.log('📦 Found via querySelector:', !!tbody);
  }
  
  if (!tbody) {
    const adminApplications = document.getElementById('adminApplications');
    if (adminApplications) {
      tbody = adminApplications.querySelector('tbody');
      console.log('📦 Found tbody in adminApplications section:', !!tbody);
      if (tbody && !tbody.id) {
        tbody.id = 'applicationsTableBody';
        console.log('📦 Set missing ID on tbody');
      }
    }
  }
  
  if (!tbody) {
    console.error('❌ applicationsTableBody container not found!');
    return;
  }
  
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
  console.log('refreshVerifications called - checking authentication state');
  
  // Check for valid admin auth, auto-initialize app if needed
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (!hasValidAdminAuth) {
    console.warn('Cannot load verifications: No valid admin authentication');
    return;
  }
  
  if (!window.isAppInitialized) {
    console.log('Auto-initializing app for admin refreshVerifications');
    window.isAppInitialized = true;
  }
  
  const currentToken = window.authToken || localStorage.getItem('fermtrack_token');
  const actualStorageToken = localStorage.getItem('fermtrack_token');
  
  if (!currentToken || !actualStorageToken) {
    console.warn('Cannot load verifications: No valid authentication token');
    showMessage('Authentication required. Please log in again.', 'error');
    return;
  }
  
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
  console.log('displayVerifications called with', bakeries.length, 'verifications');
  
  // FIRST: Ensure the DOM structure exists
  ensureAdminSectionExists('adminVerification', 'verificationsTableBody', [
    'Bakery Name', 'Slug', 'Status', 'Created', 'Description', 'Actions'
  ], 6);
  
  // Try multiple approaches to find the container
  let tbody = document.getElementById('verificationsTableBody');
  
  if (!tbody) {
    tbody = document.querySelector('#verificationsTableBody');
    console.log('📦 Found via querySelector:', !!tbody);
  }
  
  if (!tbody) {
    const adminVerification = document.getElementById('adminVerification');
    if (adminVerification) {
      tbody = adminVerification.querySelector('tbody');
      console.log('📦 Found tbody in adminVerification section:', !!tbody);
      if (tbody && !tbody.id) {
        tbody.id = 'verificationsTableBody';
        console.log('📦 Set missing ID on tbody');
      }
    }
  }
  
  if (!tbody) {
    console.error('❌ verificationsTableBody container not found!');
    return;
  }
  
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
  console.log('addUser called - checking authentication state');
  
  // Check for valid admin auth, auto-initialize app if needed
  const hasValidAdminAuth = window.currentUser && 
                           window.currentUser.is_global_admin && 
                           (window.authToken || localStorage.getItem('fermtrack_token'));
  
  if (!hasValidAdminAuth) {
    console.warn('Cannot add user: No valid admin authentication');
    return;
  }
  
  if (!window.isAppInitialized) {
    console.log('Auto-initializing app for admin addUser');
    window.isAppInitialized = true;
  }
  
  // Token validation
  const windowToken = window.authToken;
  const storedToken = localStorage.getItem('fermtrack_token');
  const validStoredToken = storedToken && storedToken.trim() && storedToken !== '' && storedToken !== 'null' ? storedToken : null;
  const currentToken = windowToken || validStoredToken;
  
  if (!currentToken) {
    console.warn('Cannot add user: No valid authentication token');
    showMessage('Authentication required. Please log in again.', 'error');
    disableAdminTabs();
    return;
  }
  
  const form = document.getElementById('addUserForm');
  if (!form) {
    console.warn('Add user form not found');
    return;
  }
  
  const formData = new FormData(form);
  
  const userData = {
    username: formData.get('username'),
    email: formData.get('email'),
    password: formData.get('password'),
    is_active: formData.get('is_active') === 'on'
  };
  
  // Basic validation
  if (!userData.username || !userData.email || !userData.password) {
    showMessage('Please fill in all required fields', 'error');
    return;
  }
  
  try {
    const response = await api('/api/auth/admin/users', 'POST', userData);
    
    if (response.user || response.success) {
      showMessage('User added successfully', 'success');
      hideAddUser();
      refreshUsers();
    } else {
      showMessage(response.error || 'Failed to add user', 'error');
    }
  } catch (error) {
    console.error('Error adding user:', error);
    
    // If authentication error, clear tokens and disable admin functions
    if (error.message && (error.message.includes('authentication') || error.message.includes('expired') || error.message.includes('token') || error.message.includes('session'))) {
      console.log('Authentication error detected - clearing tokens and disabling admin');
      localStorage.removeItem('fermtrack_token');
      window.authToken = null;
      window.currentUser = null;
      disableAdminTabs();
    }
    
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
