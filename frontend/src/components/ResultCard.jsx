import { useEffect, useState } from 'react'

function scoreTier(score) {
  if (score >= 75) return 'safe'
  if (score >= 50) return 'caution'
  if (score >= 25) return 'risky'
  return 'scam'
}

export default function ResultCard({ report }) {
  const tier = scoreTier(report.risk_score)

  // Animate the score bar after mount
  const [fillWidth, setFillWidth] = useState(0)
  useEffect(() => {
    const id = requestAnimationFrame(() =>
      requestAnimationFrame(() => setFillWidth(report.risk_score))
    )
    return () => cancelAnimationFrame(id)
  }, [report.risk_score])

  return (
    <div className="result-card">
      <div className="result-header">
        <div>
          <span className="token-name">{report.token_name || 'Unknown Token'}</span>
          <span className={`token-chain chain-${report.chain.toLowerCase()}`}>
            {report.chain}
          </span>
        </div>
        <div className="score-badge">
          <div className={`score-number text-${tier}`}>{report.risk_score}</div>
          <div className="score-right">
            <div className={`score-label text-${tier}`}>{report.risk_label}</div>
            <div className="score-sub">Risk score / 100</div>
            <div className="score-meter">
              <div
                className={`score-fill fill-${tier}`}
                style={{ width: `${fillWidth}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="result-body">
        <div>
          <div className="section-title">🚩 Red Flags</div>
          <div className="pills">
            {report.red_flags?.length > 0
              ? report.red_flags.map((f, i) => (
                  <span key={i} className="pill pill-red">{f}</span>
                ))
              : <span className="pill pill-none">None detected</span>
            }
          </div>
        </div>

        <hr className="divider" />

        <div>
          <div className="section-title">✅ Positive Signals</div>
          <div className="pills">
            {report.positive_signals?.length > 0
              ? report.positive_signals.map((s, i) => (
                  <span key={i} className="pill pill-green">{s}</span>
                ))
              : <span className="pill pill-none">None detected</span>
            }
          </div>
        </div>

        <hr className="divider" />

        <div>
          <div className="section-title">On-Chain Summary</div>
          <div className="prose">{report.on_chain_summary || '—'}</div>
        </div>

        <div>
          <div className="section-title">Verdict</div>
          <div className="prose">{report.verdict || '—'}</div>
        </div>
      </div>
    </div>
  )
}
