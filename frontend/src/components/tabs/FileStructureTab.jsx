export default function FileStructureTab({ analysis }) {
  return (
    <div>
      <h2>File Structure</h2>
      <ul className="file-list">
        {analysis.file_structure.map((file) => (
          <li key={file.path} className="file-item">
            <span className="file-path">{file.path}</span>
            <span className="file-purpose">{file.purpose}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
