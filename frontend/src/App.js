import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/DashboardNew';
import ReportMissingPerson from './pages/ReportMissingPerson';
import UploadImage from './pages/UploadImage';
import Results from './pages/Results';
import RoleSelector from './pages/RoleSelector';
import FacialRecognitionSearch from './pages/FacialRecognitionSearch';
import FacialRecognitionResults from './pages/FacialRecognitionResults';

// Styles
import './styles/global.css';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          <Route
            path="/role-selector"
            element={
              <PrivateRoute>
                <RoleSelector />
              </PrivateRoute>
            }
          />

          <Route
            path="/facial-search"
            element={
              <PrivateRoute>
                <FacialRecognitionSearch />
              </PrivateRoute>
            }
          />

          <Route
            path="/facial-results"
            element={
              <PrivateRoute>
                <FacialRecognitionResults />
              </PrivateRoute>
            }
          />

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

          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
