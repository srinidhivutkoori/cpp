import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { BookOpen, Mail, Lock, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../auth';
import { login } from '../api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { loginUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      toast.error('Please fill in all fields');
      return;
    }
    setLoading(true);
    try {
      const res = await login(email, password);
      loginUser(res.data.user, res.data.token);
      toast.success('Welcome back!');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-blue-600 rounded-2xl mb-4">
            <BookOpen className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome to PaperHub</h1>
          <p className="text-gray-500 mt-1">Academic Conference Paper Submission System</p>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">Sign in to your account</h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="you@example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter your password"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white py-2.5 rounded-lg text-sm font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            Don't have an account?{' '}
            <Link to="/register" className="text-blue-600 font-medium hover:text-blue-700">
              Create one
            </Link>
          </p>
        </div>

        <div className="mt-4 bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <p className="text-xs font-medium text-gray-500 mb-2 text-center">Demo Credentials</p>
          <div className="flex flex-col gap-2">
            <button
              type="button"
              onClick={() => { setEmail('admin@paperhub.demo'); setPassword('Admin1234!'); }}
              className="w-full text-left px-3 py-2 bg-blue-50 hover:bg-blue-100 border border-blue-200 rounded-lg text-xs text-blue-800 transition-colors cursor-pointer"
            >
              <span className="font-semibold">Admin:</span> admin@paperhub.demo / Admin1234!
            </button>
            <button
              type="button"
              onClick={() => { setEmail('reviewer@paperhub.demo'); setPassword('Review1234!'); }}
              className="w-full text-left px-3 py-2 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-xs text-emerald-800 transition-colors cursor-pointer"
            >
              <span className="font-semibold">Reviewer:</span> reviewer@paperhub.demo / Review1234!
            </button>
            <button
              type="button"
              onClick={() => { setEmail('author@paperhub.demo'); setPassword('Author1234!'); }}
              className="w-full text-left px-3 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-lg text-xs text-gray-800 transition-colors cursor-pointer"
            >
              <span className="font-semibold">Author:</span> author@paperhub.demo / Author1234!
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
