export default function ArchitectureTab({ architecture }) {
  return (
    <div>
      <h2>Architecture</h2>
      <p style={{ whiteSpace: 'pre-wrap' }}>{architecture.explanation}</p>
      {/* Person 4 will mount MermaidDiagram here */}
      <div id="mermaid-container" data-mermaid={architecture.mermaid}>
        <div className="mermaid-placeholder">
          Architecture diagram will be rendered here (Mermaid — Person 4).
        </div>
      </div>
    </div>
  );
}
