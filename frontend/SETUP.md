# SuraSmart Frontend - Setup & Deployment Guide

## Development Setup

### Quick Start with Docker Compose

```bash
# From project root
docker-compose up -d frontend
```

This will:
1. Start the frontend on port 3000
2. Connect to backend on http://localhost:8000/api
3. Auto-rebuild on code changes

### Local Development

```bash
cd frontend
npm install
npm start
```

Frontend will be available at `http://localhost:3000`

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/          # Reusable UI components
│   │   └── PrivateRoute.js
│   ├── contexts/            # React Context for state management
│   │   └── AuthContext.js
│   ├── pages/               # Page components
│   │   ├── Login.js
│   │   ├── Register.js
│   │   ├── Dashboard.js
│   │   ├── ReportMissingPerson.js
│   │   ├── UploadImage.js
│   │   └── Results.js
│   ├── services/            # API client & utilities
│   │   └── api.js
│   ├── styles/              # CSS modules
│   │   ├── global.css
│   │   ├── Auth.css
│   │   ├── Forms.css
│   │   ├── Dashboard.css
│   │   └── Results.css
│   ├── App.js               # Main app component
│   └── index.js             # React DOM entry
├── Dockerfile
├── .env.example
├── .gitignore
├── package.json
└── README.md
```

## Key Features

### 🔐 Authentication
- Login & Register pages
- JWT token management
- Automatic token refresh
- Protected routes via PrivateRoute component
- User context for easy access

### 📱 Dashboard
- Overview of all missing persons
- Real-time notifications
- Quick actions for reporting and searching
- Status filtering

### 📋 Report Missing Person
- Comprehensive form for reporting
- Age, gender, description, identifying marks
- Last seen location and date
- Immediate image upload redirect

### 📸 Image Upload
- File validation (JPEG/PNG only)
- Size validation (max 5MB)
- Image preview
- Processing priority selection

### 🔍 Results
- Real-time match updates
- Auto-refresh capability
- Match confidence display
- Verification workflow
- Status tracking (pending, verified, rejected)

## API Integration

### Base URL
```
http://localhost:8000/api
```

### Authentication Flow
1. User registers/logs in
2. Backend returns access & refresh tokens
3. Tokens stored in localStorage
4. Access token included in Authorization header: `Bearer <token>`
5. On 401, automatic refresh token request
6. If refresh fails, redirect to login

### Key API Endpoints Used

**Auth:**
- `POST /auth/token/` - Login
- `POST /auth/users/` - Register
- `GET /auth/users/me/` - Get current user
- `POST /auth/token/refresh/` - Refresh token

**Missing Persons:**
- `GET /facial-recognition/missing-persons/` - List all
- `POST /facial-recognition/missing-persons/` - Create new
- `GET /facial-recognition/missing-persons/{id}/` - Get details

**Images:**
- `POST /facial-recognition/missing-persons/{id}/upload_image/` - Upload

**Matches:**
- `GET /facial-recognition/matches/` - List matches
- `POST /facial-recognition/matches/{id}/verify/` - Verify match
- `POST /facial-recognition/matches/{id}/reject/` - Reject match

**Notifications:**
- `GET /notifications/notifications/` - Get notifications
- `POST /notifications/notifications/{id}/mark_as_read/` - Mark read

## Environment Variables

Create `.env` file:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_APP_NAME=SuraSmart
REACT_APP_JWT_EXPIRY_MINUTES=60
REACT_APP_ENABLE_AUTO_REFRESH=true
REACT_APP_REFRESH_INTERVAL_MS=3000
```

## Build & Deployment

### Development Build
```bash
npm start
```

### Production Build
```bash
npm run build
```

Output: `build/` directory

### Docker Build
```bash
docker build -t sura-smart-frontend .
docker run -p 3000:3000 sura-smart-frontend
```

### Deployment to Netlify
```bash
npm run build
# Deploy build/ folder to Netlify
```

### Deployment to Vercel
```bash
npm install -g vercel
vercel
```

## Styling System

### Global Styles (global.css)
- Color variables
- Base button styles
- Form styles
- Utility classes

### Page-Specific Styles
- `Auth.css` - Login/Register pages
- `Forms.css` - Form pages
- `Dashboard.css` - Dashboard page
- `Results.css` - Results page

### Color Palette
```css
--primary: #2563eb (Blue)
--primary-dark: #1d4ed8
--primary-light: #3b82f6
--success: #10b981 (Green)
--danger: #ef4444 (Red)
--warning: #f59e0b (Amber)
--secondary: #6b7280 (Gray)
--light: #f3f4f6
--dark: #1f2937
```

## State Management

### AuthContext
Manages authentication state globally:
```javascript
import { useAuth } from './contexts/AuthContext';

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();
  // ...
}
```

### API Service
Axios instance with JWT interceptors:
```javascript
import api from './services/api';

const response = await api.getMissingPersons();
const matches = await api.getMatches({ missing_person: id });
```

## Responsive Design

- Mobile-first approach
- Breakpoints: 768px (tablet), 1024px (desktop)
- Flexible grid layouts
- Touch-friendly buttons (min 44px)

## Performance Optimization

1. **Code Splitting**: Dynamic imports for pages
2. **Lazy Loading**: Images load on demand
3. **Caching**: API responses cached where appropriate
4. **Minification**: Automatic with production build

## Security Best Practices

1. **JWT Tokens**: Stored in localStorage with automatic refresh
2. **HTTPS**: Use in production
3. **CORS**: Configured on backend
4. **Input Validation**: Form validation before API calls
5. **Protected Routes**: PrivateRoute component prevents unauthorized access

## Development Workflow

### Adding a New Page
1. Create component in `src/pages/`
2. Add route in `App.js`
3. Create CSS file in `src/styles/`
4. Import and use AuthContext/API as needed

### Adding a New API Call
1. Add method to `api.js`
2. Use in component with try/catch
3. Handle errors appropriately

### Testing Components
```bash
npm test
```

## Troubleshooting

### "Cannot find module" errors
```bash
rm -rf node_modules package-lock.json
npm install
```

### Port 3000 already in use
```bash
# Change port in .env or kill process using port 3000
```

### API connection errors
- Check backend is running on port 8000
- Verify `REACT_APP_API_URL` is correct
- Check CORS configuration in backend
- Look at browser console Network tab

### Authentication issues
- Clear localStorage: `localStorage.clear()`
- Check token expiry in browser DevTools
- Verify backend is issuing tokens

### Styling issues
- Clear browser cache (Ctrl+Shift+Delete)
- Check CSS file is imported correctly
- Verify CSS class names match

## Additional Resources

- [React Documentation](https://react.dev)
- [React Router Documentation](https://reactrouter.com)
- [Axios Documentation](https://axios-http.com)
- [JWT Documentation](https://jwt.io)

## Support

For issues or questions:
1. Check existing GitHub issues
2. Review backend API documentation in `backend/README.md`
3. Consult `ARCHITECTURE_REFERENCE.md` for system design
