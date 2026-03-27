import { useState, useEffect } from 'react';
import {
  Building2, Calendar, Clock, Tag, Plus, X, Loader2, AlertCircle
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../auth';
import { getConferences, createConference } from '../api';

export default function Conferences() {
  const { user } = useAuth();
  const [conferences, setConferences] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    name: '',
    description: '',
    start_date: '',
    end_date: '',
    submission_deadline: '',
    topics: '',
  });

  useEffect(() => {
    loadConferences();
  }, []);

  const loadConferences = async () => {
    try {
      const res = await getConferences();
      setConferences(res.data.conferences || res.data || []);
    } catch {
      toast.error('Failed to load conferences');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!form.name || !form.start_date || !form.end_date || !form.submission_deadline) {
      toast.error('Please fill in required fields');
      return;
    }
    setCreating(true);
    try {
      const payload = {
        ...form,
        topics: form.topics.split(',').map((t) => t.trim()).filter(Boolean),
      };
      await createConference(payload);
      toast.success('Conference created!');
      setShowModal(false);
      setForm({ name: '', description: '', start_date: '', end_date: '', submission_deadline: '', topics: '' });
      loadConferences();
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to create conference');
    } finally {
      setCreating(false);
    }
  };

  const isDeadlinePassed = (deadline) => {
    if (!deadline) return false;
    return new Date(deadline) < new Date();
  };

  const formatDate = (d) => {
    if (!d) return '';
    return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="skeleton h-8 w-48 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="skeleton h-56 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Conferences</h1>
          <p className="text-gray-500 mt-1">Browse academic conferences and their submission deadlines</p>
        </div>
        {user?.role === 'admin' && (
          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Create Conference
          </button>
        )}
      </div>

      {conferences.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <Building2 className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">No conferences available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {conferences.map((conf) => {
            const closed = isDeadlinePassed(conf.submission_deadline);
            return (
              <div key={conf.id || conf._id} className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 leading-tight">{conf.name}</h3>
                  <span className={`shrink-0 ml-2 px-2.5 py-1 text-xs font-medium rounded-full ${closed ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}`}>
                    {closed ? 'Closed' : 'Open'}
                  </span>
                </div>

                {conf.description && (
                  <p className="text-sm text-gray-500 mb-4 line-clamp-2">{conf.description}</p>
                )}

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <Calendar className="w-4 h-4 text-gray-400" />
                    <span>{formatDate(conf.start_date)} - {formatDate(conf.end_date)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className={`w-4 h-4 ${closed ? 'text-red-400' : 'text-amber-400'}`} />
                    <span className={closed ? 'text-red-600' : 'text-gray-600'}>
                      Deadline: {formatDate(conf.submission_deadline)}
                    </span>
                  </div>
                </div>

                {conf.topics && conf.topics.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {(Array.isArray(conf.topics) ? conf.topics : [conf.topics]).map((topic, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 bg-purple-50 text-purple-700 text-xs font-medium rounded-md">
                        <Tag className="w-3 h-3" />
                        {topic}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
          <div className="bg-white rounded-xl shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Create Conference</h2>
              <button onClick={() => setShowModal(false)} className="p-1 text-gray-400 hover:text-gray-600 rounded">
                <X className="w-5 h-5" />
              </button>
            </div>
            <form onSubmit={handleCreate} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Name *</label>
                <input
                  type="text"
                  value={form.name}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g. ICML 2026"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                <textarea
                  value={form.description}
                  onChange={(e) => setForm({ ...form, description: e.target.value })}
                  rows={3}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  placeholder="Brief description of the conference"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
                  <input
                    type="date"
                    value={form.start_date}
                    onChange={(e) => setForm({ ...form, start_date: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date *</label>
                  <input
                    type="date"
                    value={form.end_date}
                    onChange={(e) => setForm({ ...form, end_date: e.target.value })}
                    className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Submission Deadline *</label>
                <input
                  type="date"
                  value={form.submission_deadline}
                  onChange={(e) => setForm({ ...form, submission_deadline: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Topics</label>
                <input
                  type="text"
                  value={form.topics}
                  onChange={(e) => setForm({ ...form, topics: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Comma-separated, e.g. AI, ML, NLP"
                />
              </div>
              <div className="flex justify-end gap-3 pt-2">
                <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                  Cancel
                </button>
                <button type="submit" disabled={creating} className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors">
                  {creating ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                  {creating ? 'Creating...' : 'Create Conference'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
