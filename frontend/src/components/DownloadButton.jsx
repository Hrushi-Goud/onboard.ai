import { useState } from 'react';

export default function DownloadButton({ report, repoUrl }) {
  const [isDownloading, setIsDownloading] = useState(false);

  async function handleDownload() {
    setIsDownloading(true);
    try {
      const response = await fetch('http://localhost:8000/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: repoUrl, ...report }),
      });

      if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || 'Download failed.');
      }

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = 'onboarding-report.md';
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err.message || 'Could not download the report.');
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <div className="download-bar">
      <button
        className="btn-download"
        onClick={handleDownload}
        disabled={isDownloading}
      >
        {isDownloading ? 'Downloading…' : '⬇ Download Report (.md)'}
      </button>
    </div>
  );
}
