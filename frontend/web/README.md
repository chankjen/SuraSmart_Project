# Frontend Setup Instructions

## Quick Start

### Prerequisites
- Node.js 16+ and npm

### Installation
```bash
cd frontend
npm install
```

### Development
```bash
npm start
```

The frontend will be available at `http://localhost:3000`

### Production Build
```bash
npm run build
```

## Environment Variables

Create a `.env` file in the `frontend/` directory:

```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_JWT_EXPIRY_MINUTES=60
```

## Project Structure

```
frontend/
├── public/
│   └── index.html
├── src/
│   ├── components/
│   │   └── PrivateRoute.js       # Route protection
│   ├── contexts/
│   │   └── AuthContext.js        # Authentication state
│   ├── pages/
│   │   ├── Login.js              # Authentication
│   │   ├── Register.js           # Registration
│   │   ├── Dashboard.js          # Main dashboard
│   │   ├── ReportMissingPerson.js # Report form
│   │   ├── UploadImage.js        # Image upload
│   │   └── Results.js            # Match results
│   ├── services/
│   │   └── api.js                # API client with JWT
│   ├── styles/
│   │   ├── global.css            # Global styles
│   │   ├── Auth.css              # Auth pages
│   │   ├── Forms.css             # Form pages
│   │   ├── Dashboard.css         # Dashboard
│   │   └── Results.css           # Results page
│   ├── App.js                    # Main app component
│   └── index.js                  # React entry point
├── package.json
└── .env
```

## Features

### Authentication
- Login/Register with JWT tokens
- Automatic token refresh
- Protected routes
- Role-based access control ready

### Dashboard
- View all missing persons
- Filter by status
- Recent notifications
- Quick actions

### Report Missing Person
- Comprehensive form with personal details
- Identifying marks and description
- Last seen location and time

### Image Upload
- Face image upload for recognition
- Processing priority selection
- Image preview before upload
- File validation (JPEG/PNG, max 5MB)

### Results
- Real-time match updates
- Auto-refresh capability
- Match confidence scoring
- Verification workflow
- Status tracking

## API Integration

The frontend connects to the backend API at `http://localhost:8000/api`.

### Key Endpoints Used

**Authentication:**
- `POST /auth/token/` - Login
- `POST /auth/users/` - Register
- `GET /auth/users/me/` - Current user
- `POST /auth/users/change_password/` - Change password

**Missing Persons:**
- `GET /facial-recognition/missing-persons/` - List
- `POST /facial-recognition/missing-persons/` - Create
- `GET /facial-recognition/missing-persons/{id}/` - Detail

**Images:**
- `POST /facial-recognition/missing-persons/{id}/upload_image/` - Upload

**Matches:**
- `GET /facial-recognition/matches/` - List
- `POST /facial-recognition/matches/{id}/verify/` - Verify
- `POST /facial-recognition/matches/{id}/reject/` - Reject

**Notifications:**
- `GET /notifications/notifications/` - List
- `POST /notifications/notifications/{id}/mark_as_read/` - Mark read

## Styling

The frontend uses a custom CSS framework with:
- Material-inspired design
- Responsive grid layouts
- Color-coded status badges
- Smooth transitions and animations
- Mobile-friendly responsive design

### Colors
- Primary: Blue (#2563eb)
- Success: Green (#10b981)
- Danger: Red (#ef4444)
- Warning: Amber (#f59e0b)
- Secondary: Gray (#6b7280)

## Development Tips

### Adding a New Page
1. Create component in `src/pages/`
2. Add route in `App.js`
3. Import required services and contexts
4. Create corresponding CSS file in `src/styles/`

### Using the API Client
```javascript
import api from '../services/api';

// Automatically includes JWT token in Authorization header
const response = await api.getMissingPersons();
```

### Authentication
```javascript
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, login, logout, isAuthenticated } = useAuth();
  // ...
}
```

## Deployment

### Docker
```bash
docker build -f Dockerfile.frontend -t sura-smart-frontend .
docker run -p 3000:3000 sura-smart-frontend
```

### Netlify/Vercel
```bash
npm run build
# Deploy the build/ folder
```

## Troubleshooting

### CORS Errors
- Ensure backend is running on port 8000
- Check `CORS_ALLOWED_ORIGINS` in backend settings

### API Connection Errors
- Verify `REACT_APP_API_URL` environment variable
- Check backend is accessible

### Authentication Issues
- Clear browser cache and localStorage
- Verify JWT tokens in browser dev tools Network tab
- Check token expiry settings

## Performance Optimization

- Code splitting with React.lazy()
- Image optimization
- Lazy loading of components
- Caching of API responses

## Security Notes

- JWT tokens stored in localStorage
- HTTPS should be used in production
- Automatic logout on 401 unauthorized
- Token refresh handled transparently

## Testing

To add tests, use React Testing Library:

```bash
npm test
```

Example test:
```javascript
import { render, screen } from '@testing-library/react';
import Login from './Login';

test('renders login form', () => {
  render(<Login />);
  expect(screen.getByText(/login/i)).toBeInTheDocument();
});
```
