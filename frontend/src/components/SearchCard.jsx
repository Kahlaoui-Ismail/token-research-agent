const TRY_TOKENS = [
  { label: 'USDC', chain: 'ETH', address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48' },
  { label: 'PEPE', chain: 'ETH', address: '0x6982508145454Ce325dDbE47a25d4ec3d2311933' },
  { label: 'BONK', chain: 'SOL', address: 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263' },
]

function detectChain(addr) {
  const s = addr.trim()
  if (s.toLowerCase().startsWith('0x') && s.length === 42) return 'ETH'
  if (s.length >= 32 && s.length <= 44 && /^[1-9A-HJ-NP-Za-km-z]+$/.test(s)) return 'SOL'
  return null
}

export default function SearchCard({ address, setAddress, onAnalyze, loading }) {
  const chain = detectChain(address)

  function handleKeyDown(e) {
    if (e.key === 'Enter') onAnalyze(address)
  }

  function tryToken(addr) {
    setAddress(addr)
    onAnalyze(addr)
  }

  let chainHint
  if (chain === 'ETH') {
    chainHint = <span>Detected: <span className="chain-badge chain-eth">Ethereum</span></span>
  } else if (chain === 'SOL') {
    chainHint = <span>Detected: <span className="chain-badge chain-sol">Solana</span></span>
  } else {
    chainHint = <span>Paste an address to auto-detect chain.</span>
  }

  return (
    <div className="search-card">
      <div className="input-row">
        <input
          className="address-input"
          type="text"
          placeholder="Paste token address…  0x… or base58"
          autoComplete="off"
          spellCheck="false"
          value={address}
          onChange={e => setAddress(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
        />
        <button
          className="btn-analyze"
          onClick={() => onAnalyze(address)}
          disabled={loading}
        >
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </div>

      <div className="chain-hint">{chainHint}</div>

      <div className="try-tokens">
        <span className="try-label">Try:</span>
        {TRY_TOKENS.map(t => (
          <button
            key={t.address}
            className="try-chip"
            onClick={() => tryToken(t.address)}
            disabled={loading}
          >
            <span className="try-chip-tag">{t.label}</span> {t.chain}
          </button>
        ))}
      </div>
    </div>
  )
}
