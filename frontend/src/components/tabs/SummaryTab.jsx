export default function SummaryTab({ analysis }) {
  return (
    <div>
      <h2>Project Summary</h2>
      <p>{analysis.summary}</p>
    </div>
  );
}
