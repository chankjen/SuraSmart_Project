import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import PrivateRoute from './components/PrivateRoute';

// Pages
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import FamilyDashboard from './pages/FamilyDashboard';
import PoliceDashboard from './pages/PoliceDashboard';
import GovernmentDashboard from './pages/GovernmentDashboard';
import ReportMissingPerson from './pages/ReportMissingPerson';
import UploadImage from './pages/UploadImage';
import Results from './pages/Results';
import FacialRecognitionSearch from './pages/FacialRecognitionSearch';
import FacialRecognitionResults from './pages/FacialRecognitionResults';
import CaseSummaryPage from './pages/CaseSummaryPage';
import AdminDashboard from './pages/AdminDashboard';
import AdminUserDetails from './pages/AdminUserDetails';
import MissingPersonDetails from './pages/MissingPersonDetails';

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
            path="/facial-search"
            element={
              <PrivateRoute>
                <FacialRecognitionSearch />
              </PrivateRoute>
            }
          />

          <Route
            path="/facial-search/:missingPersonId"
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
            path="/family-dashboard"
            element={
              <PrivateRoute>
                <FamilyDashboard />
              </PrivateRoute>
            }
          />

          <Route
            path="/reported-cases"
            element={
              <PrivateRoute>
                <CaseSummaryPage />
              </PrivateRoute>
            }
          />

          <Route
            path="/active-searches"
            element={
              <PrivateRoute>
                <CaseSummaryPage />
              </PrivateRoute>
            }
          />

          <Route
            path="/resolved-cases"
            element={
              <PrivateRoute>
                <CaseSummaryPage />
              </PrivateRoute>
            }
          />

          <Route
            path="/admin-dashboard"
            element={
              <PrivateRoute>
                <AdminDashboard />
              </PrivateRoute>
            }
          />

          <Route
            path="/admin/user/:userId"
            element={
              <PrivateRoute>
                <AdminUserDetails />
              </PrivateRoute>
            }
          />

          <Route
            path="/police-dashboard"
            element={
              <PrivateRoute>
                <PoliceDashboard />
              </PrivateRoute>
            }
          />

          <Route
            path="/government-dashboard"
            element={
              <PrivateRoute>
                <GovernmentDashboard />
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
            path="/missing-person/:id"
            element={
              <PrivateRoute>
                <MissingPersonDetails />
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
