import { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

mermaid.initialize({ startOnLoad: false, theme: 'default' });

export default function MermaidDiagram({ chart }) {
  const ref = useRef(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    if (!chart || !ref.current) return;
    setError(false);
    const id = 'mermaid-' + Math.random().toString(36).slice(2);
    mermaid.render(id, chart)
      .then(({ svg }) => { ref.current.innerHTML = svg; })
      .catch(() => setError(true));
  }, [chart]);

  if (error) return <pre><code>{chart}</code></pre>;
  return <div ref={ref} />;
}
