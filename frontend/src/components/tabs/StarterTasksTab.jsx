export default function StarterTasksTab({ tasks }) {
  return (
    <div>
      <h2>Starter Tasks</h2>
      <div className="card-list">
        {tasks.map((task, i) => (
          <div key={i} className="task-card">
            <h3>{task.title}</h3>
            <p>{task.description}</p>
            <div className="affected-files">
              {task.files.map((file) => (
                <span key={file} className="file-chip">{file}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
