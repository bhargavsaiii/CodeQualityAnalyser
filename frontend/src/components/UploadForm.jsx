import { useState } from 'react';
import axios from 'axios';

function UploadForm({ setReport }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file');
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      console.log('API Response:', JSON.stringify(response.data, null, 2)); // Detailed logging
      setReport(response.data);
      setError(null);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Unknown error';
      setError(`Failed to analyze file: ${errorMessage}`);
      console.error('API Error:', err, 'Response:', err.response?.data); // Detailed error logging
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4">
      <div className="mb-3">
        <label htmlFor="fileInput" className="form-label">Upload Python File (.py)</label>
        <input
          type="file"
          id="fileInput"
          className="form-control"
          onChange={(e) => setFile(e.target.files[0])}
          accept=".py"
        />
      </div>
      {error && <div className="alert alert-danger">{error}</div>}
      {loading && (
        <div className="spinner-border text-primary mt-3" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      )}
      <button type="submit" className="btn btn-primary" disabled={loading}>
        Analyze
      </button>
    </form>
  );
}

export default UploadForm;