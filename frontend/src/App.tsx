import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import PrivateRoute from './routes/PrivateRoute';
import MainLayout from './layouts/MainLayout';

// Lazy load pages
const Landing = React.lazy(() => import('./pages/Landing'));
const Login = React.lazy(() => import('./pages/Login'));
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Upload = React.lazy(() => import('./pages/Upload'));
const Settings = React.lazy(() => import('./pages/Settings'));

const App: React.FC = () => {
  const { checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, []);

  return (
    <Router>
      <React.Suspense fallback={
        <div className="h-screen w-full flex items-center justify-center bg-background">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
        </div>
      }>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Login />} /> {/* Using same login for demo/simplicity or separate if needed */}

          {/* Protected Routes */}
          <Route path="/dashboard" element={
            <PrivateRoute>
              <MainLayout>
                <Dashboard />
              </MainLayout>
            </PrivateRoute>
          } />
          <Route path="/upload" element={
            <PrivateRoute>
              <MainLayout>
                <Upload />
              </MainLayout>
            </PrivateRoute>
          } />
          <Route path="/settings" element={
            <PrivateRoute>
              <MainLayout>
                <Settings />
              </MainLayout>
            </PrivateRoute>
          } />

          {/* 404 Route */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </React.Suspense>
    </Router>
  );
};

export default App;
