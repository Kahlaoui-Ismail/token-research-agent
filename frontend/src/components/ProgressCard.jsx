function StepIcon({ state }) {
  if (state === 'active') return <span className="spinner" />
  if (state === 'done')   return <span className="check">✓</span>
  return <span className="dot" />
}

export default function ProgressCard({ steps }) {
  return (
    <div className="progress-card">
      <div className="progress-title">Analysis in progress</div>
      <ul className="progress-steps">
        {steps.map((step, i) => (
          <li
            key={i}
            className={`step${step.state === 'active' ? ' active' : ''}${step.state === 'done' ? ' done' : ''}`}
          >
            <span className="step-icon">
              <StepIcon state={step.state} />
            </span>
            <span>{step.label}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
