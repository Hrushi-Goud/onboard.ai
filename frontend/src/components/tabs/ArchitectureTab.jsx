import MarkdownRenderer from '../MarkdownRenderer';
import MermaidDiagram from '../MermaidDiagram';

export default function ArchitectureTab({ architecture }) {
  return (
    <div>
      <h2>Architecture</h2>
      <MarkdownRenderer>{architecture.explanation}</MarkdownRenderer>
      <MermaidDiagram chart={architecture.mermaid} />
    </div>
  );
}
