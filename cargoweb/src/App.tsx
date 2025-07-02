import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import LoadingScreen from './components/common/LoadingScreen';
import { useAuthStore } from './store/authStore';
import Login from './pages/auth/Login';

// Lazy load pages to improve initial load time
const Dashboard = lazy(() => import('./pages/dashboard/Dashboard'));
const OrdersList = lazy(() => import('./pages/orders/OrdersList'));
const OrderDetails = lazy(() => import('./pages/orders/OrderDetails'));
const TransportersList = lazy(() => import('./pages/transporters/TransportersList'));
// const TransporterDetails = lazy(() => import('./pages/transporters/TransporterDetails'));
const CreateTransporter = lazy(() => import('./pages/transporters/CreateTransporter'));
// const Profile = lazy(() => import('./pages/profile/Profile'));
// const NotFound = lazy(() => import('./pages/common/NotFound'));

// Protected route component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

function App() {
  const { isAuthenticated } = useAuthStore();
  
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        <Route path="/login" element={
          isAuthenticated ? <Navigate to="/dashboard\" replace /> : <Login />
        } />
        
        <Route path="/" element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }>
          <Route index element={<Navigate to="/dashboard\" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="orders" element={<OrdersList />} />
          <Route path="orders/:id" element={<OrderDetails />} />
          <Route path="transporters" element={<TransportersList />} />
          <Route path="transporters/create" element={<CreateTransporter />} />
          {/* <Route path="transporters/:id" element={<TransporterDetails />} />
          <Route path="profile" element={<Profile />} />
          <Route path="*" element={<NotFound />} /> */}
        </Route>
      </Routes>
    </Suspense>
  );
}

export default App;