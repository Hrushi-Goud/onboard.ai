export default function SetupTab({ setupGuide }) {
  return (
    <div>
      <h2>Setup Guide</h2>

      <h3>Prerequisites</h3>
      <ul>
        {setupGuide.prerequisites.map((item, i) => (
          <li key={i}>{item}</li>
        ))}
      </ul>

      <h3>Steps</h3>
      <ol className="steps-list">
        {setupGuide.steps.map((step, i) => (
          <li key={i}>{step}</li>
        ))}
      </ol>

      <h3>Environment Variables</h3>
      <div>
        {setupGuide.environment_variables.map((envVar, i) => (
          <div key={i} className="env-var">{envVar}</div>
        ))}
      </div>

      <h3>Verification</h3>
      <div className="verification-box">{setupGuide.verification}</div>
    </div>
  );
}
