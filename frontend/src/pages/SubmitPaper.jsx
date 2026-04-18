import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileText, Plus, X, Upload, Loader2, UserPlus, Tag
} from 'lucide-react';
import toast from 'react-hot-toast';
import { submitPaper, getConferences } from '../api';

export default function SubmitPaper() {
  const navigate = useNavigate();
  const [conferences, setConferences] = useState([]);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    title: '',
    abstract: '',
    conferenceId: '',
  });
  const [authors, setAuthors] = useState(['']);
  const [keywords, setKeywords] = useState(['']);
  const [file, setFile] = useState(null);

  useEffect(() => {
    loadConferences();
  }, []);

  const loadConferences = async () => {
    try {
      const res = await getConferences();
      setConferences(res.data.conferences || res.data || []);
    } catch {
      // ignore
    }
  };

  const addAuthor = () => setAuthors([...authors, '']);
  const removeAuthor = (idx) => {
    if (authors.length <= 1) return;
    setAuthors(authors.filter((_, i) => i !== idx));
  };
  const updateAuthor = (idx, val) => {
    const updated = [...authors];
    updated[idx] = val;
    setAuthors(updated);
  };

  const addKeyword = () => setKeywords([...keywords, '']);
  const removeKeyword = (idx) => {
    if (keywords.length <= 1) return;
    setKeywords(keywords.filter((_, i) => i !== idx));
  };
  const updateKeyword = (idx, val) => {
    const updated = [...keywords];
    updated[idx] = val;
    setKeywords(updated);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!form.title || !form.abstract) {
      toast.error('Title and abstract are required');
      return;
    }
    const filteredAuthors = authors.filter((a) => a.trim());
    if (filteredAuthors.length === 0) {
      toast.error('At least one author is required');
      return;
    }

    setLoading(true);
    try {
      const payload = {
        title: form.title,
        abstract: form.abstract,
        conferenceId: form.conferenceId,
        authors: filteredAuthors,
        keywords: keywords.filter((k) => k.trim()).map((k) => k.trim()),
      };

      if (file) {
        const reader = new FileReader();
        const base64 = await new Promise((resolve) => {
          reader.onload = () => resolve(reader.result.split(',')[1]);
          reader.readAsDataURL(file);
        });
        payload.pdfBase64 = base64;
      }

      await submitPaper(payload);
      toast.success('Paper submitted successfully!');
      navigate('/papers');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Submit Paper</h1>
        <p className="text-gray-500 mt-1">Submit your research paper for review</p>
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Title *</label>
            <input
              type="text"
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter paper title"
            />
          </div>

          {/* Abstract */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Abstract *</label>
            <textarea
              value={form.abstract}
              onChange={(e) => setForm({ ...form, abstract: e.target.value })}
              rows={6}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="Provide a summary of your paper"
            />
          </div>

          {/* Authors */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-sm font-medium text-gray-700">Authors *</label>
              <button type="button" onClick={addAuthor} className="flex items-center gap-1 text-xs text-blue-600 font-medium hover:text-blue-700">
                <Plus className="w-3.5 h-3.5" />
                Add Author
              </button>
            </div>
            <div className="space-y-2">
              {authors.map((author, idx) => (
                <div key={idx} className="flex gap-2">
                  <div className="relative flex-1">
                    <UserPlus className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={author}
                      onChange={(e) => updateAuthor(idx, e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder={`Author ${idx + 1}`}
                    />
                  </div>
                  {authors.length > 1 && (
                    <button type="button" onClick={() => removeAuthor(idx)} className="p-2.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Keywords */}
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-sm font-medium text-gray-700">Keywords</label>
              <button type="button" onClick={addKeyword} className="flex items-center gap-1 text-xs text-blue-600 font-medium hover:text-blue-700">
                <Plus className="w-3.5 h-3.5" />
                Add Keyword
              </button>
            </div>
            <div className="space-y-2">
              {keywords.map((kw, idx) => (
                <div key={idx} className="flex gap-2">
                  <div className="relative flex-1">
                    <Tag className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={kw}
                      onChange={(e) => updateKeyword(idx, e.target.value)}
                      className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder={`Keyword ${idx + 1}`}
                    />
                  </div>
                  {keywords.length > 1 && (
                    <button type="button" onClick={() => removeKeyword(idx)} className="p-2.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Conference */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Conference</label>
            <select
              value={form.conferenceId}
              onChange={(e) => setForm({ ...form, conferenceId: e.target.value })}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 appearance-none bg-white"
            >
              <option value="">Select a conference (optional)</option>
              {conferences.map((c) => (
                <option key={c.id || c._id} value={c.id || c._id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Upload PDF</label>
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
              {file ? (
                <div className="flex items-center justify-center gap-2">
                  <FileText className="w-5 h-5 text-blue-600" />
                  <span className="text-sm text-gray-700 font-medium">{file.name}</span>
                  <button type="button" onClick={() => setFile(null)} className="p-1 text-gray-400 hover:text-red-500">
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <label className="cursor-pointer">
                  <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">Click to upload or drag and drop</p>
                  <p className="text-xs text-gray-400 mt-1">PDF files only</p>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setFile(e.target.files[0] || null)}
                    className="hidden"
                  />
                </label>
              )}
            </div>
          </div>

          {/* Submit */}
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={() => navigate('/papers')} className="px-4 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2.5 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <FileText className="w-4 h-4" />}
              {loading ? 'Submitting...' : 'Submit Paper'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
