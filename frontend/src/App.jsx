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
      const response = await fetch(`${import.meta.env.VITE_API_URL}/analyze-all`, {
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
        setError('Could not connect to the backend.');
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
          <div className="feature-pills">
            <span className="feature-pill">Summary</span>
            <span className="feature-pill">Architecture</span>
            <span className="feature-pill">File Structure</span>
            <span className="feature-pill">Setup Guide</span>
            <span className="feature-pill">Starter Tasks</span>
            <span className="feature-pill">Optimizations</span>
          </div>
          <RepoInputForm onSubmit={handleSubmit} isLoading={isLoading} />
          {isLoading && (
            <div className="loading-state">
              <div className="loading-spinner" />
              <p>Analyzing repository — this may take a moment…</p>
            </div>
          )}
          {!isLoading && !report && !error && (
            <div className="how-it-works">
              <p className="hiw-heading">How it works</p>
              <div className="hiw-grid">
                <div className="hiw-card">
                  <div className="hiw-num">01</div>
                  <div className="hiw-title">Paste a URL</div>
                  <div className="hiw-desc">Drop any public GitHub repository URL into the box.</div>
                </div>
                <div className="hiw-card">
                  <div className="hiw-num">02</div>
                  <div className="hiw-title">Analyse</div>
                  <div className="hiw-desc">The AI reads the code, structure, and documentation.</div>
                </div>
                <div className="hiw-card">
                  <div className="hiw-num">03</div>
                  <div className="hiw-title">Get a report</div>
                  <div className="hiw-desc">Receive a full onboarding report ready to share.</div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* ── Main content area ── */}
      {(error || report) && (
      <main className="main-content">
        {error && (
          <div className="error-banner" role="alert">
            <span className="error-icon">⚠</span>
            {error}
          </div>
        )}

        {report && (
          <div className="report-sections">
            <section className="report-section">
              <div className="section-header">
                <div className="section-label">01</div>
                <h2 className="section-heading">Summary</h2>
              </div>
              <div className="section-body">
                <SummaryTab analysis={report.analysis} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-header">
                <div className="section-label">02</div>
                <h2 className="section-heading">Architecture</h2>
              </div>
              <div className="section-body">
                <ArchitectureTab architecture={report.architecture} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-header">
                <div className="section-label">03</div>
                <h2 className="section-heading">File Structure</h2>
              </div>
              <div className="section-body">
                <FileStructureTab analysis={report.analysis} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-header">
                <div className="section-label">04</div>
                <h2 className="section-heading">Setup Guide</h2>
              </div>
              <div className="section-body">
                <SetupTab setupGuide={report.setup_guide} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-header">
                <div className="section-label">05</div>
                <h2 className="section-heading">Starter Tasks</h2>
              </div>
              <div className="section-body">
                <StarterTasksTab tasks={report.starter_tasks_and_optimizations.starter_tasks} />
              </div>
            </section>

            <section className="report-section">
              <div className="section-header">
                <div className="section-label">06</div>
                <h2 className="section-heading">Optimizations</h2>
              </div>
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
      )}

      {/* ── Footer ── */}
      <footer className="site-footer">
        <div className="footer-inner">
          <span className="footer-brand">Onboard<span className="footer-accent">.ai</span></span>
          <span className="footer-sep">·</span>
          <span className="footer-copy">MIT License © {new Date().getFullYear()}</span>
          <span className="footer-sep">·</span>
          <span className="footer-copy">Built for developers, by developers</span>
        </div>
      </footer>
    </div>
  );
}
