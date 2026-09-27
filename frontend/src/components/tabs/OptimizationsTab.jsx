export default function OptimizationsTab({ optimizations }) {
  return (
    <div>
      <h2>Optimizations</h2>
      <div className="card-list">
        {optimizations.map((opt, i) => (
          <div key={i} className="opt-card">
            <h3>{opt.suggestion}</h3>
            <p>{opt.rationale}</p>
            <div className="affected-files">
              {opt.files.map((file) => (
                <span key={file} className="file-chip">{file}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
