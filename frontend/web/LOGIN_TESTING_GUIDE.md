# SuraSmart Frontend Login - Testing Guide

## Frontend Access

**Frontend URL:** http://localhost:3000

The frontend is fully configured to communicate with the backend API at `http://localhost:8000/api`.

---

## Demo User Accounts

All demo users are now available to login on the frontend. Simply navigate to the login page and either:

1. **Enter credentials manually**, or
2. **Click a demo user button** to auto-populate the username and password

### Family Members
| Username | Password | Role |
|----------|----------|------|
| alex | family123 | Family Member |
| amanda | family123 | Family Member |

**What they can do:**
- Report missing persons
- Upload images for their own cases
- View only their own missing person reports
- Cannot verify matches or access other cases

---

### Police Officers
| Username | Password | Role |
|----------|----------|------|
| bernard | police456 | Police Officer |
| betty | police456 | Police Officer |

**What they can do:**
- Report missing persons
- Upload images for any case
- View ALL missing person cases
- Verify and reject facial matches
- Modify any case

---

### Government Officials
| Username | Password | Role |
|----------|----------|------|
| cate | official789 | Government Official |
| dan | official789 | Government Official |

**What they can do:**
- Same as Police Officers
- Report missing persons
- Upload images for any case
- View ALL cases
- Verify and reject matches
- Modify any case

---

## How to Test Login

### Step 1: Start the Servers
Make sure both servers are running:
- **Frontend:** Running on port 3000
- **Backend:** Running on port 8000

### Step 2: Navigate to Login Page
Visit: http://localhost:3000

### Step 3: Test Different Users

#### Option A: Quick Login (Demo Buttons)
1. Click any demo user button (e.g., "alex")
2. The username and password are auto-populated
3. Click "Login" button
4. Should redirect to Dashboard

#### Option B: Manual Login
1. Type username (e.g., `alex`)
2. Type password (e.g., `family123`)
3. Click "Login" button
4. Should redirect to Dashboard

### Step 4: Verify Role-Based Access
Once logged in as different users, notice:

**As Family Member (alex):**
- Can only see their own reports
- Cannot verify matches
- Limited dashboard functionality

**As Police Officer (bernard):**
- Can see all reports
- Can verify matches
- Full dashboard access

**As Government Official (cate):**
- Can see all reports
- Can verify matches
- Full dashboard access

---

## Testing Workflow

### 1. Register New User (Optional)
- Click "Register here" link
- Fill in registration form
- New users default to "Family Member" role

### 2. Login with Demo Account
- Use any demo account credentials
- Auto-populate by clicking demo user button
- Or type credentials manually

### 3. Navigate Dashboard
- After login, user is redirected to `/dashboard`
- Dashboard shows user's role and available actions
- Different features based on user role

### 4. Test Role-Based Features
- **Report Missing Person:** Available to all roles
- **Upload Image:** Available to all roles, but permissions vary
- **Verify Matches:** Only for Police Officers and Government Officials
- **View Cases:** Family members see only own; others see all

---

## API Authentication Flow

The frontend uses JWT (JSON Web Token) authentication:

1. **Login Request**
   ```
   POST /api/auth/token/
   Body: { "username": "alex", "password": "family123" }
   ```

2. **Response**
   ```
   {
     "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
     "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
   }
   ```

3. **Token Storage**
   - Access token stored in localStorage
   - Used for all subsequent API requests
   - Included in Authorization header: `Bearer <access_token>`

4. **Token Refresh**
   - If access token expires (60 minutes)
   - Automatically refreshes using refresh token
   - User stays logged in

5. **Logout**
   - Removes tokens from localStorage
   - User redirected to login page

---

## Troubleshooting Login Issues

### Issue: "Login failed. Please try again."
**Cause:** Incorrect credentials
**Solution:** 
- Check username and password spelling
- Ensure backend is running
- Verify user exists in database

### Issue: "Cannot POST /api/auth/token/"
**Cause:** Backend API not running
**Solution:**
- Start backend server: `python manage.py runserver 0.0.0.0:8000`
- Check backend is accessible at http://localhost:8000

### Issue: CORS Error
**Cause:** Frontend and backend communication blocked
**Solution:**
- Ensure `CORS_ALLOWED_ORIGINS` includes `http://localhost:3000`
- Check backend CORS configuration in settings.py

### Issue: Demo buttons not working
**Cause:** Frontend not fully compiled
**Solution:**
- Restart npm: `npm start` in frontend directory
- Clear browser cache (Ctrl+Shift+Delete)
- Try manual login instead

---

## Testing Across Different Browsers

The login system works on all modern browsers:
- Chrome/Chromium ✅
- Firefox ✅
- Safari ✅
- Edge ✅

**Tip:** Use browser DevTools (F12) to inspect:
- Network requests to `/api/auth/token/`
- localStorage for stored tokens
- Console for any errors

---

## Next Steps After Login

After successfully logging in, users can:

1. **View Dashboard** - See overview of missing persons
2. **Report Missing Person** - Fill out form to report
3. **Upload Images** - Add facial recognition images
4. **Search Cases** - Find missing persons (if authorized)
5. **Verify Matches** - Review facial recognition results (if authorized)
6. **Receive Notifications** - Get alerts about case updates

---

## Security Notes

✅ **Secure Practices Implemented:**
- Passwords are hashed (bcrypt)
- JWT tokens expire after 60 minutes
- Refresh tokens enable seamless re-authentication
- HTTPS recommended for production
- CORS properly configured
- Role-based access enforced server-side

⚠️ **For Development Only:**
- Demo passwords are simple for testing
- Change passwords in production
- Use strong passwords for real users
- Enable HTTPS in production
- Use environment variables for secrets

---

## Testing Checklist

- [ ] Frontend loads at http://localhost:3000
- [ ] Login page displays with demo user buttons
- [ ] Can login with alex / family123
- [ ] Can login with bernard / police456
- [ ] Can login with cate / official789
- [ ] After login, redirected to dashboard
- [ ] Dashboard shows correct user info
- [ ] Can logout and return to login
- [ ] Role-based features work correctly
- [ ] Tokens stored in localStorage
- [ ] Token refresh works after 60 minutes
- [ ] Errors handled gracefully

