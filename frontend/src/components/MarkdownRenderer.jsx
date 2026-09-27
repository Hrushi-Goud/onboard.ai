import ReactMarkdown from 'react-markdown';

export default function MarkdownRenderer({ children }) {
  if (!children) return null;
  return <ReactMarkdown>{children}</ReactMarkdown>;
}
