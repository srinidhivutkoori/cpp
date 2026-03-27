import { Routes, Route } from 'react-router-dom';
import { useAuth } from './auth';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Conferences from './pages/Conferences';
import Papers from './pages/Papers';
import SubmitPaper from './pages/SubmitPaper';
import PaperDetail from './pages/PaperDetail';

export default function App() {
  const { user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50">
      {user && <Navbar />}
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/conferences"
          element={
            <ProtectedRoute>
              <Conferences />
            </ProtectedRoute>
          }
        />
        <Route
          path="/papers"
          element={
            <ProtectedRoute>
              <Papers />
            </ProtectedRoute>
          }
        />
        <Route
          path="/papers/submit"
          element={
            <ProtectedRoute>
              <SubmitPaper />
            </ProtectedRoute>
          }
        />
        <Route
          path="/papers/:id"
          element={
            <ProtectedRoute>
              <PaperDetail />
            </ProtectedRoute>
          }
        />
      </Routes>
    </div>
  );
}
