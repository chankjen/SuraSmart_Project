import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';

// Pages
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/DashboardNew';
import ReportMissingPerson from './pages/ReportMissingPerson';
import UploadImage from './pages/UploadImage';
import Results from './pages/Results';

// Styles
import './styles/global.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />

          <Route
            path="/report"
            element={
              <PrivateRoute>
                <ReportMissingPerson />
              </PrivateRoute>
            }
          />

          <Route
            path="/missing-person/:missingPersonId/upload"
            element={
              <PrivateRoute>
                <UploadImage />
              </PrivateRoute>
            }
          />

          <Route
            path="/results/:missingPersonId"
            element={
              <PrivateRoute>
                <Results />
              </PrivateRoute>
            }
          />

          <Route path="/" element={<Navigate to="/dashboard" />} />
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
