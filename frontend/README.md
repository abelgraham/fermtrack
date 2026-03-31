# FermTrack Frontend

A single-page web application that provides a complete frontend interface for the FermTrack API. This frontend allows bakers and kitchen staff to manage fermentation batches, track actions, and monitor fermentation stages through an intuitive web interface.

## Features

### 🔐 Authentication
- **User Registration & Login** with role-based access (baker, manager, admin)
- **JWT Token Management** with automatic token validation
- **Secure Session Handling** with localStorage

### 📦 Batch Management
- **Create New Batches** with recipe name, weight, and environmental data
- **Edit Existing Batches** including status updates
- **View Batch Details** with complete history and current status
- **Delete Batches** (admin/manager only)
- **Real-time Status Tracking** with color-coded status indicators

### 🔄 Action Logging
- **Record Batch Actions** (fortify, re-ball, degas, wash, divide, shape)
- **Weight Change Tracking** for precise inventory management
- **Environmental Recording** (temperature, humidity)
- **Detailed Action History** with timestamps and descriptions

### ⏱️ Fermentation Stage Management
- **Start Fermentation Stages** (autolyse, bulk_ferment, proof, final_proof, retard)
- **Set Target Parameters** (duration, temperature, humidity)
- **Track Active Stages** with completion status
- **Complete Stages** with timestamp recording

### 🎨 User Interface
- **Dark Theme** matching the FermTrack brand
- **Responsive Design** for mobile and desktop use
- **Modal-based Workflows** for focused task completion
- **Real-time Alerts** for user feedback
- **Keyboard Shortcuts** (Ctrl+N for new batch, Escape to close modals)

## Quick Start

### Prerequisites
- FermTrack backend server running on `http://localhost:5000`
- Modern web browser with JavaScript enabled

### Method 1: Simple HTTP Server

For development, you can serve the frontend using Python's built-in server:

```bash
cd frontend
python3 -m http.server 8080
```

Then open your browser to `http://localhost:8080`

### Method 2: Live Server (VS Code)

If you're using VS Code:
1. Install the "Live Server" extension
2. Right-click on `index.html` 
3. Select "Open with Live Server"

### Method 3: Direct File Access

You can also open `index.html` directly in your browser, but some browsers may have CORS restrictions for local files.

## Usage

### First Time Setup

1. **Start the Backend**: Make sure the FermTrack backend is running at `http://localhost:5000`
2. **Open the Frontend**: Navigate to your frontend URL (e.g., `http://localhost:8080`)
3. **Login with Default Admin**: 
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ Change this password in production!
4. **Create Users**: Register additional users with appropriate roles

### Daily Workflow

1. **Create a New Batch**:
   - Click "New Batch" button
   - Fill in batch ID, recipe name, and initial weight
   - Set environmental conditions if available
   - Add any initial notes

2. **Track Batch Progress**:
   - View batch from the main dashboard
   - Click "View Details" to see full batch information
   - Use the "Actions" tab to record batch activities
   - Use the "Fermentation" tab to manage fermentation stages

3. **Record Actions**:
   - Select action type (fortify, re-ball, degas, etc.)
   - Add weight changes if applicable
   - Include descriptive notes
   - Action is automatically timestamped

4. **Manage Fermentation Stages**:
   - Start new fermentation stages with target parameters
   - Monitor active stages
   - Complete stages when finished
   - View complete fermentation timeline

## API Integration

The frontend communicates with the FermTrack backend API at `http://localhost:5000/api`. Key integration points:

### Authentication Endpoints
- `POST /auth/login` - User login
- `POST /auth/register` - User registration  
- `GET /auth/me` - Current user information

### Batch Endpoints
- `GET /batches` - List all batches
- `POST /batches` - Create new batch
- `PUT /batches/{id}` - Update batch
- `DELETE /batches/{id}` - Delete batch (admin/manager)
- `POST /batches/{id}/actions` - Add batch action
- `POST /batches/{id}/fermentation-stages` - Start fermentation stage
- `PUT /batches/{id}/fermentation-stages/{stage_id}/complete` - Complete stage

### Configuration

The API base URL is configured in the JavaScript:
```javascript
const API_BASE = 'http://localhost:5000/api';
```

To use a different backend URL, modify this constant in the HTML file.

## Browser Compatibility

- **Modern Browsers**: Chrome 88+, Firefox 85+, Safari 14+, Edge 88+
- **Features Used**: 
  - ES6+ JavaScript (async/await, template literals)  
  - Fetch API for HTTP requests
  - CSS Grid and Flexbox for layout
  - CSS Custom Properties for theming

## Security Considerations

- **JWT Token Storage**: Tokens are stored in localStorage
- **CORS Configuration**: Backend must allow your frontend origin
- **Input Validation**: All inputs are validated on both frontend and backend
- **Role-based Access**: Sensitive operations are restricted by user role

## Keyboard Shortcuts

- `Ctrl + N` - Create new batch
- `Escape` - Close open modals
- `Tab` - Navigate between form fields
- `Enter` - Submit forms

## Status Indicators

### Batch Status Colors
- **Mixing**: Yellow - Initial dough preparation
- **Bulk Ferment**: Blue - Primary fermentation phase  
- **Divided**: Purple - Dough has been portioned
- **Proofing**: Orange - Final proofing stage
- **Ready**: Green - Ready for baking
- **Baked**: Gray - Completed product
- **Discarded**: Red - Batch was discarded

### Action Types
- **Fortify**: Add flour or ingredients to adjust consistency
- **Re-ball**: Reform dough balls for better structure  
- **Degas**: Remove excess gas during fermentation
- **Wash**: Apply wash (egg wash, lye, etc.)
- **Divide**: Portion dough into individual pieces
- **Shape**: Form final product shapes
- **Other**: Custom actions not covered above

### Fermentation Stages
- **Autolyse**: Flour and water rest period
- **Bulk Ferment**: Primary fermentation phase
- **Proof**: Secondary fermentation
- **Final Proof**: Last proofing before baking
- **Retard**: Cold fermentation (refrigeration)

## Troubleshooting

### Connection Issues
- Ensure backend server is running on `http://localhost:5000`
- Check browser console for error messages
- Verify CORS configuration in backend

### Authentication Problems
- Clear localStorage if tokens become invalid
- Check username and password
- Ensure user account is active

### Data Not Loading
- Check network tab in browser developer tools
- Verify API endpoints are responding
- Check authentication token validity

## Development

The frontend is built as a single HTML file with embedded CSS and JavaScript for simplicity. For larger applications, consider:

- **Component Framework**: React, Vue, or Angular
- **State Management**: Redux, Vuex, or similar
- **Build Process**: Webpack, Vite, or Parcel
- **CSS Framework**: Tailwind, Bootstrap, or styled-components

## Production Deployment

For production deployment:

1. **Web Server**: Use nginx, Apache, or similar
2. **HTTPS**: Enable SSL/TLS certificates  
3. **API URL**: Update API_BASE to production backend URL
4. **Compression**: Enable gzip compression
5. **Caching**: Set appropriate cache headers
6. **CDN**: Consider using a CDN for static assets

## License

This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
See the LICENSE file for details.