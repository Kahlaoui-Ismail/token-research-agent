import { useState, useRef } from 'react'
import Header from './components/Header'
import SearchCard from './components/SearchCard'
import ProgressCard from './components/ProgressCard'
import ResultCard from './components/ResultCard'
import ErrorCard from './components/ErrorCard'

const STEP_LABELS = [
  'Detecting chain…',
  'Chain detected',
  'Fetching on-chain & market data…',
  'Running AI security analysis…',
]

function initSteps() {
  return STEP_LABELS.map(label => ({ label, state: 'pending' }))
}

export default function App() {
  const [address, setAddress] = useState('')
  const [status, setStatus]   = useState('idle') // idle | loading | done | error
  const [steps, setSteps]     = useState(initSteps)
  const [report, setReport]   = useState(null)
  const [error, setError]     = useState(null)
  const esRef = useRef(null)

  function activateStep(message) {
    setSteps(prev => {
      // Mark current active step as done
      const next = prev.map(s =>
        s.state === 'active' ? { ...s, state: 'done' } : s
      )
      // Find the matching step by keyword, else the first pending one
      const idx = STEP_LABELS.findIndex(label =>
        message.toLowerCase().includes(
          label.replace('…', '').trim().toLowerCase().split(' ')[0]
        )
      )
      const targetIdx = idx >= 0 ? idx : next.findIndex(s => s.state === 'pending')
      if (targetIdx >= 0) {
        next[targetIdx] = { ...next[targetIdx], label: message, state: 'active' }
      }
      return next
    })
  }

  function finishSteps() {
    setSteps(prev => prev.map(s => ({ ...s, state: 'done' })))
  }

  function startAnalysis(addr) {
    const trimmed = (addr ?? address).trim()
    if (!trimmed) return

    if (esRef.current) { esRef.current.close(); esRef.current = null }

    setStatus('loading')
    setSteps(initSteps())
    setReport(null)
    setError(null)

    const apiBase = import.meta.env.VITE_API_URL ?? ''
    const url = `${apiBase}/analyze/stream?address=${encodeURIComponent(trimmed)}`
    const es = new EventSource(url)
    esRef.current = es

    es.onmessage = (e) => {
      let payload
      try { payload = JSON.parse(e.data) } catch { return }

      if (payload.type === 'status') {
        activateStep(payload.message)
      } else if (payload.type === 'result') {
        finishSteps()
        setTimeout(() => {
          setStatus('done')
          setReport(payload.data)
        }, 400)
        es.close()
      } else if (payload.type === 'error') {
        setStatus('error')
        setError(payload.message)
        es.close()
      }
    }

    es.onerror = () => {
      setStatus('error')
      setError('Connection lost. Check that the server is running.')
      es.close()
    }
  }

  return (
    <div className="page">
      <div className="container">
        <Header />

        <SearchCard
          address={address}
          setAddress={setAddress}
          onAnalyze={startAnalysis}
          loading={status === 'loading'}
        />

        {status === 'loading' && <ProgressCard steps={steps} />}
        {status === 'error'   && <ErrorCard message={error} />}
        {status === 'done' && report && <ResultCard report={report} />}

        <footer className="footer">
          Powered by Claude AI · Data from DexScreener, Etherscan, Honeypot.is, Solscan, RugCheck
        </footer>
      </div>
    </div>
  )
}
