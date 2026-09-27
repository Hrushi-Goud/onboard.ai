import { useState } from 'react';
import './App.css';
import RepoInputForm from './components/RepoInputForm';
import DownloadButton from './components/DownloadButton';
import SummaryTab from './components/tabs/SummaryTab';
import ArchitectureTab from './components/tabs/ArchitectureTab';
import FileStructureTab from './components/tabs/FileStructureTab';
import SetupTab from './components/tabs/SetupTab';
import StarterTasksTab from './components/tabs/StarterTasksTab';
import OptimizationsTab from './components/tabs/OptimizationsTab';

const ERROR_MESSAGES = {
  503: 'Could not reach GitHub. Check the URL and try again.',
  502: 'AI analysis failed. Please try again.',
};

export default function App() {
  const [repoUrl, setRepoUrl] = useState('');
  const [report, setReport] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  async function handleSubmit(url) {
    setRepoUrl(url);
    setReport(null);
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/analyze-all', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ repo_url: url }),
      });

      if (!response.ok) {
        const override = ERROR_MESSAGES[response.status];
        if (override) {
          throw new Error(override);
        }
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || `Request failed with status ${response.status}.`);
      }

      const data = await response.json();
      setReport(data);
    } catch (err) {
      if (err instanceof TypeError) {
        setError('Could not connect to the backend. Make sure it is running on http://localhost:8000.');
      } else {
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={report ? 'page has-report' : 'page'}>
      {/* ── Hero ── */}
      <div className="hero">
        <div className="hero-inner">
          <h1 className="wordmark">
            Onboard<span className="accent">.ai</span>
          </h1>
          <p className="tagline">
            Paste a GitHub URL. Get a full onboarding report in seconds.
          </p>
          <RepoInputForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>
      </div>

      {/* ── Main content area ── */}
      <main className="main-content">
        {isLoading && (
          <div className="loading-state">
            <div className="loading-spinner" />
            <p>Analyzing repository — this may take a moment…</p>
          </div>
        )}

        {error && (
          <div className="error-banner" role="alert">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        {report && (
          <div className="report-sections">
            <section className="report-section">
              <div className="section-label">01</div>
              <h2 className="section-heading">Summary</h2>
              <div className="section-body">
                <SummaryTab analysis={report.analysis} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-label">02</div>
              <h2 className="section-heading">Architecture</h2>
              <div className="section-body">
                <ArchitectureTab architecture={report.architecture} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-label">03</div>
              <h2 className="section-heading">File Structure</h2>
              <div className="section-body">
                <FileStructureTab analysis={report.analysis} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-label">04</div>
              <h2 className="section-heading">Setup Guide</h2>
              <div className="section-body">
                <SetupTab setupGuide={report.setup_guide} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-label">05</div>
              <h2 className="section-heading">Starter Tasks</h2>
              <div className="section-body">
                <StarterTasksTab tasks={report.starter_tasks_and_optimizations.starter_tasks} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-label">06</div>
              <h2 className="section-heading">Optimizations</h2>
              <div className="section-body">
                <OptimizationsTab optimizations={report.starter_tasks_and_optimizations.optimizations} />
              </div>
            </section>

            <div className="download-row">
              <DownloadButton report={report} repoUrl={repoUrl} />
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
