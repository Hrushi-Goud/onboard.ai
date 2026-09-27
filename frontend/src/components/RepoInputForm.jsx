import { useState } from 'react';

export default function RepoInputForm({ onSubmit, isLoading }) {
  const [url, setUrl] = useState('');

  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = url.trim();
    if (trimmed) {
      onSubmit(trimmed);
    }
  }

  return (
    <form className="repo-form" onSubmit={handleSubmit}>
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://github.com/owner/repo"
        required
        disabled={isLoading}
        aria-label="GitHub repository URL"
      />
      <button type="submit" className="btn-analyze" disabled={isLoading || !url.trim()}>
        {isLoading ? 'Analyzing…' : 'Analyze'}
      </button>
    </form>
  );
}
