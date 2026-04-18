import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  FileText, Download, Star, MessageSquare, User, Calendar,
  Tag, Building2, Loader2, Trash2, Edit3, ChevronLeft, Send
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../auth';
import {
  getPaper, getReviews, submitReview, updatePaperStatus, deletePaper, updatePaper
} from '../api';

const statusConfig = {
  submitted: { color: 'bg-blue-100 text-blue-700', label: 'Submitted' },
  under_review: { color: 'bg-amber-100 text-amber-700', label: 'Under Review' },
  accepted: { color: 'bg-green-100 text-green-700', label: 'Accepted' },
  rejected: { color: 'bg-red-100 text-red-700', label: 'Rejected' },
  revision_required: { color: 'bg-purple-100 text-purple-700', label: 'Revision Required' },
};

const recommendationConfig = {
  accept: { color: 'bg-green-100 text-green-700', label: 'Accept' },
  reject: { color: 'bg-red-100 text-red-700', label: 'Reject' },
  revision: { color: 'bg-purple-100 text-purple-700', label: 'Revision Required' },
  minor_revision: { color: 'bg-amber-100 text-amber-700', label: 'Minor Revision' },
  major_revision: { color: 'bg-orange-100 text-orange-700', label: 'Major Revision' },
};

function StatusBadge({ status }) {
  const cfg = statusConfig[status] || statusConfig.submitted;
  return (
    <span className={`px-3 py-1 text-sm font-medium rounded-full ${cfg.color}`}>
      {cfg.label}
    </span>
  );
}

export default function PaperDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [paper, setPaper] = useState(null);
  const [reviews, setReviews] = useState([]);
  const [loading, setLoading] = useState(true);

  // Review form
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewForm, setReviewForm] = useState({ score: 5, recommendation: 'accept', comments: '' });
  const [reviewLoading, setReviewLoading] = useState(false);

  // Status update
  const [newStatus, setNewStatus] = useState('');
  const [statusLoading, setStatusLoading] = useState(false);

  // Delete
  const [deleteLoading, setDeleteLoading] = useState(false);

  useEffect(() => {
    loadPaper();
    loadReviews();
  }, [id]);

  const loadPaper = async () => {
    try {
      const res = await getPaper(id);
      const p = res.data.paper || res.data;
      setPaper(p);
      setNewStatus(p.status || '');
      // getPaper includes reviews inline
      if (p.reviews) {
        setReviews(p.reviews);
      }
    } catch {
      toast.error('Failed to load paper');
      navigate('/papers');
    } finally {
      setLoading(false);
    }
  };

  const loadReviews = async () => {
    try {
      const res = await getReviews(id);
      setReviews(res.data.reviews || res.data || []);
    } catch {
      // may not have reviews
    }
  };

  const handleSubmitReview = async (e) => {
    e.preventDefault();
    if (!reviewForm.comments.trim()) {
      toast.error('Please add comments');
      return;
    }
    setReviewLoading(true);
    try {
      await submitReview(id, reviewForm);
      toast.success('Review submitted!');
      setShowReviewForm(false);
      setReviewForm({ score: 5, recommendation: 'accept', comments: '' });
      loadReviews();
      loadPaper();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to submit review');
    } finally {
      setReviewLoading(false);
    }
  };

  const handleStatusUpdate = async () => {
    if (!newStatus) return;
    setStatusLoading(true);
    try {
      await updatePaperStatus(id, newStatus);
      toast.success('Status updated!');
      loadPaper();
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to update status');
    } finally {
      setStatusLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to withdraw this paper?')) return;
    setDeleteLoading(true);
    try {
      await deletePaper(id);
      toast.success('Paper withdrawn');
      navigate('/papers');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to withdraw paper');
    } finally {
      setDeleteLoading(false);
    }
  };

  const handleResubmit = () => {
    navigate(`/papers/submit?edit=${id}`);
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="skeleton h-6 w-24 mb-6" />
        <div className="skeleton h-10 w-96 mb-4" />
        <div className="skeleton h-64 rounded-xl" />
      </div>
    );
  }

  if (!paper) return null;

  const isAuthor = user?.role === 'author';
  const isReviewer = user?.role === 'reviewer';
  const isAdmin = user?.role === 'admin';

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back */}
      <button
        onClick={() => navigate('/papers')}
        className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700 mb-6"
      >
        <ChevronLeft className="w-4 h-4" />
        Back to Papers
      </button>

      {/* Paper Header */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8 mb-6">
        <div className="flex items-start justify-between gap-4 mb-4">
          <h1 className="text-2xl font-bold text-gray-900">{paper.title}</h1>
          <StatusBadge status={paper.status} />
        </div>

        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-6">
          <div className="flex items-center gap-1.5">
            <User className="w-4 h-4" />
            <span>{Array.isArray(paper.authors) ? paper.authors.join(', ') : paper.authors || 'Unknown'}</span>
          </div>
          {paper.conferenceId && (
            <div className="flex items-center gap-1.5">
              <Building2 className="w-4 h-4" />
              <span>Conference: {paper.conferenceId}</span>
            </div>
          )}
          {paper.createdAt && (
            <div className="flex items-center gap-1.5">
              <Calendar className="w-4 h-4" />
              <span>{new Date(paper.createdAt).toLocaleDateString()}</span>
            </div>
          )}
        </div>

        {/* Keywords */}
        {paper.keywords && (
          <div className="flex flex-wrap gap-1.5 mb-6">
            {(Array.isArray(paper.keywords) ? paper.keywords : paper.keywords.split(',')).map((kw, idx) => (
              <span key={idx} className="inline-flex items-center gap-1 px-2.5 py-1 bg-purple-50 text-purple-700 text-xs font-medium rounded-md">
                <Tag className="w-3 h-3" />
                {typeof kw === 'string' ? kw.trim() : kw}
              </span>
            ))}
          </div>
        )}

        {/* Abstract */}
        <div className="mb-6">
          <h2 className="text-sm font-semibold text-gray-700 uppercase tracking-wide mb-2">Abstract</h2>
          <p className="text-gray-600 text-sm leading-relaxed whitespace-pre-wrap">{paper.abstract}</p>
        </div>

        {/* PDF download */}
        {paper.pdfUrl && (
          <a
            href={paper.pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors"
          >
            <Download className="w-4 h-4" />
            Download PDF
          </a>
        )}

        {/* Author actions */}
        {isAuthor && (
          <div className="flex items-center gap-3 mt-6 pt-6 border-t border-gray-200">
            {paper.status === 'revision_required' && (
              <button
                onClick={handleResubmit}
                className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors"
              >
                <Edit3 className="w-4 h-4" />
                Edit & Resubmit
              </button>
            )}
            <button
              onClick={handleDelete}
              disabled={deleteLoading}
              className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg text-sm font-medium hover:bg-red-100 disabled:opacity-50 transition-colors"
            >
              {deleteLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Trash2 className="w-4 h-4" />}
              Withdraw Paper
            </button>
          </div>
        )}

        {/* Admin status update */}
        {isAdmin && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Update Status</h3>
            <div className="flex items-center gap-3">
              <select
                value={newStatus}
                onChange={(e) => setNewStatus(e.target.value)}
                className="px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white"
              >
                <option value="submitted">Submitted</option>
                <option value="under_review">Under Review</option>
                <option value="accepted">Accepted</option>
                <option value="rejected">Rejected</option>
                <option value="revision_required">Revision Required</option>
              </select>
              <button
                onClick={handleStatusUpdate}
                disabled={statusLoading}
                className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {statusLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                Update Status
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Reviews Section */}
      <div className="bg-white rounded-xl border border-gray-200 mb-6">
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900">Reviews ({reviews.length})</h2>
          {isReviewer && !showReviewForm && (
            <button
              onClick={() => setShowReviewForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              <MessageSquare className="w-4 h-4" />
              Submit Review
            </button>
          )}
        </div>

        {reviews.length === 0 && !showReviewForm ? (
          <div className="px-6 py-12 text-center">
            <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
            <p className="text-gray-500">No reviews yet</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {reviews.map((review, idx) => {
              const recCfg = recommendationConfig[review.recommendation] || recommendationConfig.accept;
              return (
                <div key={review.id || review._id || idx} className="px-6 py-5">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                        <User className="w-4 h-4 text-gray-500" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{review.reviewerName || review.reviewer_name || 'Reviewer'}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-amber-50 text-amber-700 text-xs font-medium rounded-md">
                        <Star className="w-3 h-3" />
                        {review.score}/10
                      </span>
                      <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${recCfg.color}`}>
                        {recCfg.label}
                      </span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">{review.comments}</p>
                </div>
              );
            })}
          </div>
        )}

        {/* Review Form */}
        {showReviewForm && (
          <div className="px-6 py-5 border-t border-gray-200 bg-gray-50 rounded-b-xl">
            <h3 className="text-sm font-semibold text-gray-900 mb-4">Write Your Review</h3>
            <form onSubmit={handleSubmitReview} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Score: <span className="text-blue-600 font-bold">{reviewForm.score}</span>/10
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={reviewForm.score}
                  onChange={(e) => setReviewForm({ ...reviewForm, score: parseInt(e.target.value) })}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>1</span>
                  <span>5</span>
                  <span>10</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Recommendation</label>
                <select
                  value={reviewForm.recommendation}
                  onChange={(e) => setReviewForm({ ...reviewForm, recommendation: e.target.value })}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white"
                >
                  <option value="accept">Accept</option>
                  <option value="revision">Revision Required</option>
                  <option value="reject">Reject</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Comments *</label>
                <textarea
                  value={reviewForm.comments}
                  onChange={(e) => setReviewForm({ ...reviewForm, comments: e.target.value })}
                  rows={5}
                  className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  placeholder="Provide detailed feedback on the paper..."
                />
              </div>

              <div className="flex justify-end gap-3">
                <button type="button" onClick={() => setShowReviewForm(false)} className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={reviewLoading}
                  className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                >
                  {reviewLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  {reviewLoading ? 'Submitting...' : 'Submit Review'}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
