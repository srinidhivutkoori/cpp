import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FileText, Search, Filter, Star, Tag } from 'lucide-react';
import toast from 'react-hot-toast';
import { getPapers } from '../api';

const statusConfig = {
  submitted: { color: 'bg-blue-100 text-blue-700', label: 'Submitted' },
  under_review: { color: 'bg-amber-100 text-amber-700', label: 'Under Review' },
  accepted: { color: 'bg-green-100 text-green-700', label: 'Accepted' },
  rejected: { color: 'bg-red-100 text-red-700', label: 'Rejected' },
  revision_required: { color: 'bg-purple-100 text-purple-700', label: 'Revision Required' },
  withdrawn: { color: 'bg-gray-100 text-gray-700', label: 'Withdrawn' },
  published: { color: 'bg-emerald-100 text-emerald-700', label: 'Published' },
};

function StatusBadge({ status }) {
  const cfg = statusConfig[status] || statusConfig.submitted;
  return (
    <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${cfg.color}`}>
      {cfg.label}
    </span>
  );
}

export default function Papers() {
  const [papers, setPapers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    loadPapers();
  }, []);

  const loadPapers = async () => {
    try {
      const res = await getPapers();
      setPapers(res.data.papers || res.data || []);
    } catch {
      toast.error('Failed to load papers');
    } finally {
      setLoading(false);
    }
  };

  const filtered = papers.filter((p) => {
    const matchSearch =
      !search ||
      p.title?.toLowerCase().includes(search.toLowerCase()) ||
      (Array.isArray(p.authors) ? p.authors.join(' ') : p.authors || '')
        .toLowerCase()
        .includes(search.toLowerCase());
    const matchStatus = statusFilter === 'all' || p.status === statusFilter;
    return matchSearch && matchStatus;
  });

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="skeleton h-8 w-48 mb-8" />
        <div className="skeleton h-12 w-full mb-4 rounded-lg" />
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="skeleton h-32 rounded-xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Papers</h1>
        <p className="text-gray-500 mt-1">Browse and manage submitted papers</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search papers by title or author..."
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="relative">
          <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="pl-10 pr-8 py-2.5 bg-white border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none"
          >
            <option value="all">All Statuses</option>
            <option value="submitted">Submitted</option>
            <option value="under_review">Under Review</option>
            <option value="accepted">Accepted</option>
            <option value="rejected">Rejected</option>
            <option value="revision_required">Revision Required</option>
          </select>
        </div>
      </div>

      {/* Paper List */}
      {filtered.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p className="text-gray-500">{search || statusFilter !== 'all' ? 'No papers match your filters' : 'No papers submitted yet'}</p>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((paper) => (
            <Link
              key={paper.id || paper._id}
              to={`/papers/${paper.id || paper._id}`}
              className="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <h3 className="text-base font-semibold text-gray-900 mb-1">{paper.title}</h3>
                  <p className="text-sm text-gray-500 mb-3">
                    {Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors || 'Unknown'}
                  </p>

                  <div className="flex flex-wrap items-center gap-2">
                    {paper.keywords && (Array.isArray(paper.keywords) ? paper.keywords : paper.keywords.split(',')).map((kw, idx) => (
                      <span key={idx} className="inline-flex items-center gap-1 px-2 py-0.5 bg-gray-100 text-gray-600 text-xs font-medium rounded-md">
                        <Tag className="w-3 h-3" />
                        {typeof kw === 'string' ? kw.trim() : kw}
                      </span>
                    ))}
                    {paper.score !== undefined && paper.score !== null && (
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-50 text-amber-700 text-xs font-medium rounded-md">
                        <Star className="w-3 h-3" />
                        Score: {paper.score}/10
                      </span>
                    )}
                  </div>
                </div>

                <StatusBadge status={paper.status} />
              </div>
            </Link>
          ))}
        </div>
      )}

      <div className="mt-4 text-sm text-gray-400">
        Showing {filtered.length} of {papers.length} papers
      </div>
    </div>
  );
}
