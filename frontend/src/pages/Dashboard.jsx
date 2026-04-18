import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText, CheckCircle, Clock, XCircle, BarChart3, Users,
  Bell, Loader2, Send, TrendingUp, Eye, AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../auth';
import { getDashboard, subscribe, getSubscriberCount } from '../api';

function StatCard({ icon: Icon, label, value, color, bgColor }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <div className="flex items-center gap-4">
        <div className={`w-12 h-12 ${bgColor} rounded-xl flex items-center justify-center`}>
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
      </div>
    </div>
  );
}

const statusConfig = {
  submitted: { color: 'bg-blue-100 text-blue-700', label: 'Submitted' },
  under_review: { color: 'bg-amber-100 text-amber-700', label: 'Under Review' },
  accepted: { color: 'bg-green-100 text-green-700', label: 'Accepted' },
  rejected: { color: 'bg-red-100 text-red-700', label: 'Rejected' },
  revision_required: { color: 'bg-purple-100 text-purple-700', label: 'Revision Required' },
};

function StatusBadge({ status }) {
  const cfg = statusConfig[status] || statusConfig.submitted;
  return (
    <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${cfg.color}`}>
      {cfg.label}
    </span>
  );
}

export default function Dashboard() {
  const { user } = useAuth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [subEmail, setSubEmail] = useState('');
  const [subLoading, setSubLoading] = useState(false);
  const [subCount, setSubCount] = useState(0);

  useEffect(() => {
    loadDashboard();
    loadSubCount();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await getDashboard();
      setData(res.data);
    } catch {
      toast.error('Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const loadSubCount = async () => {
    try {
      const res = await getSubscriberCount();
      setSubCount(res.data.count || 0);
    } catch {
      // ignore
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!subEmail) return;
    setSubLoading(true);
    try {
      await subscribe(subEmail);
      toast.success('Subscribed to notifications!');
      setSubEmail('');
      loadSubCount();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Subscription failed');
    } finally {
      setSubLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="skeleton h-8 w-48 mb-8" />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton h-28 rounded-xl" />
          ))}
        </div>
        <div className="skeleton h-64 rounded-xl" />
      </div>
    );
  }

  // Map Lambda response fields to what the UI expects
  const role = data?.role || user?.role;
  let papers = [];
  let stats = {};

  if (role === 'author') {
    papers = data?.myPapers || [];
    stats = {
      total: data?.submittedCount || 0,
      accepted: data?.acceptedCount || 0,
      pending: data?.pendingCount || 0,
      rejected: papers.filter(p => p.status === 'rejected').length,
    };
  } else if (role === 'reviewer') {
    papers = data?.assignedPapers || [];
    stats = {
      assigned: papers.length,
      completed: data?.completedReviews || 0,
      pending: data?.pendingReviews || 0,
    };
  } else if (role === 'admin') {
    papers = data?.recentSubmissions || [];
    const byStatus = data?.byStatus || {};
    stats = {
      total: data?.totalPapers || 0,
      acceptance_rate: data?.acceptanceRate || 0,
      users: data?.totalReviewers || 0,
      conferences: 0,
      ...byStatus,
    };
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.username}
        </h1>
        <p className="text-gray-500 mt-1">
          Here's an overview of your {user?.role} dashboard
        </p>
      </div>

      {/* Author Dashboard */}
      {user?.role === 'author' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard icon={FileText} label="My Papers" value={stats.total || 0} color="text-blue-600" bgColor="bg-blue-50" />
            <StatCard icon={CheckCircle} label="Accepted" value={stats.accepted || 0} color="text-green-600" bgColor="bg-green-50" />
            <StatCard icon={Clock} label="Pending" value={stats.pending || 0} color="text-amber-600" bgColor="bg-amber-50" />
            <StatCard icon={XCircle} label="Rejected" value={stats.rejected || 0} color="text-red-600" bgColor="bg-red-50" />
          </div>

          <div className="bg-white rounded-xl border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">My Papers</h2>
            </div>
            {papers.length === 0 ? (
              <div className="px-6 py-12 text-center">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No papers submitted yet</p>
                <Link to="/papers/submit" className="inline-block mt-3 text-sm text-blue-600 font-medium hover:text-blue-700">
                  Submit your first paper
                </Link>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {papers.map((p) => (
                  <Link key={p.id || p._id} to={`/papers/${p.id || p._id}`} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">{p.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{p.conference_name || 'No conference'}</p>
                    </div>
                    <StatusBadge status={p.status} />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Reviewer Dashboard */}
      {user?.role === 'reviewer' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            <StatCard icon={Eye} label="Assigned Papers" value={stats.assigned || 0} color="text-blue-600" bgColor="bg-blue-50" />
            <StatCard icon={CheckCircle} label="Completed Reviews" value={stats.completed || 0} color="text-green-600" bgColor="bg-green-50" />
            <StatCard icon={Clock} label="Pending Reviews" value={stats.pending || 0} color="text-amber-600" bgColor="bg-amber-50" />
          </div>

          <div className="bg-white rounded-xl border border-gray-200">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Assigned Papers</h2>
            </div>
            {papers.length === 0 ? (
              <div className="px-6 py-12 text-center">
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-500">No papers assigned for review</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-100">
                {papers.map((p) => (
                  <Link key={p.id || p._id} to={`/papers/${p.id || p._id}`} className="flex items-center justify-between px-6 py-4 hover:bg-gray-50 transition-colors">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 truncate">{p.title}</p>
                      <p className="text-xs text-gray-500 mt-0.5">By {Array.isArray(p.authors) ? p.authors.join(', ') : p.authors}</p>
                    </div>
                    <StatusBadge status={p.status} />
                  </Link>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      {/* Admin Dashboard */}
      {user?.role === 'admin' && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            <StatCard icon={FileText} label="Total Papers" value={stats.total || 0} color="text-blue-600" bgColor="bg-blue-50" />
            <StatCard icon={TrendingUp} label="Acceptance Rate" value={`${stats.acceptance_rate || 0}%`} color="text-green-600" bgColor="bg-green-50" />
            <StatCard icon={Users} label="Total Users" value={stats.users || 0} color="text-purple-600" bgColor="bg-purple-50" />
            <StatCard icon={BarChart3} label="Conferences" value={stats.conferences || 0} color="text-amber-600" bgColor="bg-amber-50" />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-xl border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Papers by Status</h3>
              <div className="space-y-3">
                {Object.entries(statusConfig).map(([key, cfg]) => {
                  const byStatus = data?.byStatus || {};
                  const count = byStatus[key] || stats[`status_${key}`] || stats[key] || 0;
                  const total = stats.total || 1;
                  const pct = Math.round((count / total) * 100);
                  return (
                    <div key={key}>
                      <div className="flex items-center justify-between text-sm mb-1">
                        <span className="text-gray-600">{cfg.label}</span>
                        <span className="font-medium text-gray-900">{count}</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${key === 'submitted' ? 'bg-blue-500' : key === 'under_review' ? 'bg-amber-500' : key === 'accepted' ? 'bg-green-500' : key === 'rejected' ? 'bg-red-500' : 'bg-purple-500'}`}
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Submissions</h3>
              </div>
              {papers.length === 0 ? (
                <div className="px-6 py-12 text-center">
                  <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                  <p className="text-gray-500">No submissions yet</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-100">
                  {papers.slice(0, 5).map((p) => (
                    <Link key={p.id || p._id} to={`/papers/${p.id || p._id}`} className="flex items-center justify-between px-6 py-3 hover:bg-gray-50 transition-colors">
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-gray-900 truncate">{p.title}</p>
                        <p className="text-xs text-gray-500 mt-0.5">{p.createdAt || ''}</p>
                      </div>
                      <StatusBadge status={p.status} />
                    </Link>
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {/* Subscribe Section */}
      <div className="mt-8 bg-white rounded-xl border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-purple-50 rounded-xl flex items-center justify-center">
            <Bell className="w-5 h-5 text-purple-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Stay Updated</h3>
            <p className="text-sm text-gray-500">Subscribe to get notifications about new conferences and deadlines</p>
          </div>
        </div>
        <form onSubmit={handleSubscribe} className="flex gap-3">
          <input
            type="email"
            value={subEmail}
            onChange={(e) => setSubEmail(e.target.value)}
            placeholder="Enter your email"
            className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
          />
          <button
            type="submit"
            disabled={subLoading}
            className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 disabled:opacity-50 transition-colors"
          >
            {subLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            Subscribe
          </button>
        </form>
        {subCount > 0 && (
          <p className="mt-3 text-xs text-gray-400">{subCount} subscriber{subCount !== 1 ? 's' : ''} and counting</p>
        )}
      </div>
    </div>
  );
}
