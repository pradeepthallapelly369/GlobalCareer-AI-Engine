import React, { useState, useEffect } from 'react';

export default function App() {
  const [tab, setTab] = useState('swarm');
  const [symbol, setSymbol] = useState('NIFTY');
  const [chainData, setChainData] = useState(null);
  const [brokerStatus, setBrokerStatus] = useState(null);
  const [strategyKey, setStrategyKey] = useState('SHORT_STRADDLE');
  const [strategyResult, setStrategyResult] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [funds, setFunds] = useState(null);
  const [positions, setPositions] = useState([]);
  const [marketTicks, setMarketTicks] = useState({});

  // Fyers Modal State
  const [showFyersModal, setShowFyersModal] = useState(false);
  const [fyersAppId, setFyersAppId] = useState('');
  const [fyersSecretKey, setFyersSecretKey] = useState('');
  const [fyersAccessToken, setFyersAccessToken] = useState('');
  const [fyersMsg, setFyersMsg] = useState('');

  // MiroFish Swarm State
  const [swarmSimulating, setSwarmSimulating] = useState(false);
  const [swarmResults, setSwarmResults] = useState(null);

  // Arya AI Options Co-Pilot State
  const [chatQuery, setChatQuery] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [tradeMode, setTradeMode] = useState('paper');
  const [executionMessage, setExecutionMessage] = useState('');
  const [chatLogs, setChatLogs] = useState([
    {
      sender: 'agent',
      agent: 'Arya AI ⚡',
      text: 'Greetings Trader! I am Arya AI, your Options Quantitative Specialist. Ask me for real-time Greeks analysis or run the MiroFish Swarm Sandbox to simulate market sentiment before executing paper/real trades!'
    }
  ]);

  useEffect(() => {
    fetchBrokerStatus();
    fetchChain('NIFTY');
    fetchStrategies();
    fetchFunds();
    fetchMarketTicks();

    // 3-second live tick update interval
    const interval = setInterval(() => {
      fetchMarketTicks();
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchMarketTicks = async () => {
    try {
      const r = await fetch('/api/market/ticks');
      const d = await r.json();
      if (d.ticks) setMarketTicks(d.ticks);
    } catch (e) {}
  };

  const fetchBrokerStatus = async () => {
    try {
      const r = await fetch('/api/broker/status');
      const d = await r.json();
      setBrokerStatus(d);
      if (d?.fyers?.client_id) setFyersAppId(d.fyers.client_id);
    } catch (e) {}
  };

  const fetchFunds = async () => {
    try {
      const r = await fetch('/api/broker/funds');
      setFunds(await r.json());
    } catch (e) {}
  };

  const fetchStrategies = async () => {
    try {
      const r = await fetch('/api/options/strategies');
      const d = await r.json();
      setStrategies(d.strategies || []);
    } catch (e) {}
  };

  const fetchChain = async (sym) => {
    setLoading(true);
    try {
      const r = await fetch(`/api/options/chain/${sym}`);
      const d = await r.json();
      if (d.status === 'success') setChainData(d);
    } catch (e) {}
    setLoading(false);
  };

  const handleSaveFyersCreds = async (e) => {
    e.preventDefault();
    setFyersMsg('Saving credentials...');
    try {
      const r = await fetch('/api/broker/fyers/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_id: fyersAppId,
          secret_key: fyersSecretKey,
          access_token: fyersAccessToken,
        }),
      });
      const d = await r.json();
      setFyersMsg(d.message || 'Fyers Credentials Updated!');
      fetchBrokerStatus();
      fetchFunds();
    } catch (err) {
      setFyersMsg('Error: ' + err.message);
    }
  };

  const runSwarmSimulation = async () => {
    setSwarmSimulating(true);
    try {
      const r = await fetch('/api/agent/swarm/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: symbol,
          spot_price: chainData?.spot_price || 24628.5,
        }),
      });
      const d = await r.json();
      if (d.status === 'success') {
        setSwarmResults(d);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setSwarmSimulating(false);
    }
  };

  const buildStrategy = async () => {
    if (!chainData) return;
    try {
      const r = await fetch('/api/options/strategy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_key: strategyKey,
          spot_price: chainData.spot_price,
          lot_size: chainData.lot_size,
          strike_step: chainData.strike_step,
        }),
      });
      const d = await r.json();
      if (d.status === 'success') setStrategyResult(d.data);
    } catch (e) {}
  };

  const executePaperTrade = async () => {
    if (!strategyResult) return;
    try {
      const r = await fetch('/api/options/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          legs: strategyResult.legs,
          lot_size: strategyResult.lot_size,
          mode: tradeMode,
          broker: 'fyers',
        }),
      });
      const d = await r.json();
      setExecutionMessage(d.message || 'Trade Executed!');
      fetchPositions();
    } catch (e) {
      alert('Error: ' + e);
    }
  };

  const handleSendChat = async (e, customPrompt = null) => {
    if (e) e.preventDefault();
    const query = customPrompt || chatQuery;
    if (!query.trim()) return;

    setChatLogs((prev) => [...prev, { sender: 'user', text: query }]);
    if (!customPrompt) setChatQuery('');
    setChatLoading(true);

    try {
      const r = await fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: query, agent: 'arya' }),
      });
      const data = await r.json();
      setChatLogs((prev) => [
        ...prev,
        {
          sender: 'agent',
          agent: 'Arya AI ⚡',
          text: data.reply,
          trade_action: data.trade_action,
        },
      ]);
    } catch (err) {
      console.error(err);
    } finally {
      setChatLoading(false);
    }
  };

  const handleExecuteAgentTrade = async (actionObj) => {
    setExecutionMessage('');
    try {
      const r = await fetch('/api/agent/execute', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: symbol,
          action: 'SELL',
          mode: tradeMode,
          broker: 'fyers',
          strategy: actionObj?.strategy || 'SHORT_STRADDLE',
          qty: 25,
        }),
      });
      const d = await r.json();
      setExecutionMessage(d.message || 'Agent Trade Filled!');
      fetchPositions();
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPositions = async () => {
    try {
      const r = await fetch('/api/broker/positions');
      const d = await r.json();
      setPositions(d.positions || []);
    } catch (e) {}
  };

  const tabs = [
    { id: 'swarm', label: '🐟 MiroFish Swarm Sandbox' },
    { id: 'copilot', label: '⚡ Arya Options AI Co-Pilot' },
    { id: 'chain', label: 'Option Chain' },
    { id: 'strategy', label: 'Strategy Builder' },
    { id: 'positions', label: 'Positions & P&L' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Real-time Ticker Bar */}
      <div style={{ background: '#04060A', borderBottom: '1px solid var(--panel-border)', padding: '6px 28px', fontSize: '0.78rem' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, overflowX: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 20 }}>
            <span style={{ color: 'var(--accent-orange)', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em' }}>LIVE NSE TICKS:</span>
            {Object.keys(marketTicks).length > 0 ? (
              Object.entries(marketTicks).map(([k, t]) => (
                <div key={k} style={{ display: 'flex', alignItems: 'center', gap: 6 }} className="mono">
                  <span style={{ color: 'var(--text-secondary)', fontWeight: 700 }}>{t.name}:</span>
                  <span style={{ fontWeight: 800, color: t.last_tick_direction === 'UP' ? 'var(--bull-green)' : 'var(--bear-red)' }}>
                    ₹{t.price?.toLocaleString()}
                  </span>
                  <span style={{ fontSize: '0.7rem', color: t.change >= 0 ? 'var(--bull-green)' : 'var(--bear-red)' }}>
                    {t.change >= 0 ? '+' : ''}{t.change} ({t.change_pct}%)
                  </span>
                </div>
              ))
            ) : (
              <span style={{ color: 'var(--text-muted)' }}>Connecting to Live Tick Stream...</span>
            )}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-muted)' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--bull-green)', display: 'inline-block' }}></span>
            <span>Tick Stream Active</span>
          </div>
        </div>
      </div>

      {/* Main Header */}
      <header className="glass-panel" style={{ borderRadius: 0, borderTop: 0, borderLeft: 0, borderRight: 0, padding: '16px 28px' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{ width: 44, height: 44, borderRadius: 12, background: 'linear-gradient(135deg,#FF9800 0%,#FF5722 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 18px rgba(255,152,0,0.5)', fontWeight: 900, fontSize: '1.3rem', color: '#000' }}>⚡</div>
            <div>
              <h1 style={{ fontSize: '1.45rem', fontWeight: 800, background: 'linear-gradient(90deg,#FFF 0%,#FF9800 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>BharatAlpha Trade</h1>
              <p style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Swarm Intelligence & Options Trading Terminal (NSE F&O)</p>
            </div>
          </div>
          <div style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
            <div className="glass-panel" style={{ padding: '6px 14px', fontSize: '0.82rem' }}>
              <span style={{ color: 'var(--text-secondary)', fontWeight: 600, marginRight: 6 }}>Symbol:</span>
              <span className="mono" style={{ fontWeight: 700, color: 'var(--accent-orange)' }}>{symbol} ₹{chainData?.spot_price || '—'}</span>
            </div>
            <select className="search-input" style={{ width: 140 }} value={symbol} onChange={e => { setSymbol(e.target.value); fetchChain(e.target.value); }}>
              <option value="NIFTY">NIFTY 50</option>
              <option value="BANKNIFTY">BANK NIFTY</option>
            </select>
            
            <button className="btn-secondary" onClick={() => setShowFyersModal(true)} style={{ padding: '6px 14px', fontSize: '0.8rem', borderColor: brokerStatus?.fyers?.connected ? 'var(--bull-green)' : 'var(--panel-border)' }}>
              {brokerStatus?.fyers?.connected ? '🟢 Fyers Connected' : '🔑 Connect Fyers Broker'}
            </button>

            <div className="glass-panel" style={{ padding: '6px 14px', fontSize: '0.78rem' }}>
              <span style={{ color: 'var(--accent-orange)', fontWeight: 600 }}>Margin: ₹{funds?.available_margin ? funds.available_margin.toLocaleString() : '5,00,000'}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav style={{ background: 'rgba(10,14,22,0.95)', borderBottom: '1px solid var(--panel-border)', padding: '0 28px' }}>
        <div style={{ maxWidth: 1400, margin: '0 auto', display: 'flex', gap: 8 }}>
          {tabs.map(t => (
            <button key={t.id} onClick={() => { setTab(t.id); if (t.id === 'positions') fetchPositions(); }}
              style={{
                display: 'flex', alignItems: 'center', gap: 8, padding: '14px 20px', background: 'none', border: 'none',
                borderBottom: tab === t.id ? '3px solid var(--accent-orange)' : '3px solid transparent',
                color: tab === t.id ? 'var(--accent-orange)' : 'var(--text-secondary)', fontWeight: tab === t.id ? 700 : 500, fontSize: '0.9rem', cursor: 'pointer'
              }}>
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      {/* Main Content Body */}
      <main style={{ maxWidth: 1400, margin: '28px auto', padding: '0 28px', flex: 1, width: '100%' }}>

        {/* MIROFISH SWARM SANDBOX TAB */}
        {tab === 'swarm' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div className="glass-panel" style={{ padding: 24, background: 'linear-gradient(135deg, rgba(255,152,0,0.08) 0%, rgba(15,20,32,0.9) 100%)', borderLeft: '4px solid var(--accent-orange)' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
                <div>
                  <h2 style={{ fontSize: '1.45rem', fontWeight: 800 }}>MiroFish Swarm Intelligence Trading Sandbox</h2>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginTop: 4 }}>
                    Multi-agent parallel simulation engine (Chanakya, Arya, Vikram, Kautilya). Rehearses market sentiment & stress tests option strategies in a sandbox.
                  </p>
                </div>
                <button className="btn-primary" onClick={runSwarmSimulation} disabled={swarmSimulating} style={{ background: 'linear-gradient(135deg,#FF9800,#FF5722)', padding: '12px 24px', fontSize: '0.95rem' }}>
                  {swarmSimulating ? '⏳ Simulating Swarm Sandbox...' : '🚀 Run MiroFish Swarm Simulation'}
                </button>
              </div>
            </div>

            {/* Swarm Agent Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
              {[
                { name: 'Chanakya AI', role: 'Macro & News Sentiment', avatar: '🧠', color: '#FF9800', desc: 'Analyzes FII/DII net flows, RBI rates, and global indices.' },
                { name: 'Arya AI', role: 'Options Quant & Greeks', avatar: '⚡', color: '#00E676', desc: 'Calculates Black-Scholes Greeks, IV Skew, and Max Pain.' },
                { name: 'Vikram AI', role: 'Technical & Momentum', avatar: '📊', color: '#29B6F6', desc: 'Tracks CPR levels, RSI breakouts, VWAP, and price action.' },
                { name: 'Kautilya AI', role: 'Chief Risk Guardian', avatar: '🛡️', color: '#E91E63', desc: 'Enforces risk limits, stop-loss thresholds, and hedging.' },
              ].map((ag, idx) => (
                <div key={idx} className="glass-panel" style={{ padding: 16, borderTop: `3px solid ${ag.color}` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                    <span style={{ fontSize: '1.4rem' }}>{ag.avatar}</span>
                    <div>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: ag.color }}>{ag.name}</h4>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{ag.role}</div>
                    </div>
                  </div>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{ag.desc}</p>
                </div>
              ))}
            </div>

            {/* Simulation Results Display */}
            {swarmResults ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
                
                {/* Consensus Gauge & Breakdown */}
                <div className="glass-panel" style={{ padding: 24 }}>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: 16 }}>Swarm Prediction & Probability Breakdown</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: 24, alignItems: 'center' }}>
                    <div>
                      <div style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--accent-orange)', marginBottom: 8 }}>
                        {swarmResults.final_consensus?.consensus_summary}
                      </div>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: 16 }}>
                        Target Strike Range: <strong className="mono" style={{ color: '#FFF' }}>{swarmResults.final_consensus?.target_range}</strong> | PCR: <strong>{swarmResults.final_consensus?.pcr}</strong> | VIX: <strong>{swarmResults.final_consensus?.vix}</strong>
                      </p>

                      {/* Probability Bars */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                            <span>Bullish Probability</span>
                            <span className="mono" style={{ color: 'var(--bull-green)', fontWeight: 700 }}>{swarmResults.final_consensus?.probabilities?.bullish}%</span>
                          </div>
                          <div style={{ height: 10, borderRadius: 5, background: 'rgba(255,255,255,0.05)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${swarmResults.final_consensus?.probabilities?.bullish}%`, background: 'var(--bull-green)' }}></div>
                          </div>
                        </div>

                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: 4 }}>
                            <span>Bearish Probability</span>
                            <span className="mono" style={{ color: 'var(--bear-red)', fontWeight: 700 }}>{swarmResults.final_consensus?.probabilities?.bearish}%</span>
                          </div>
                          <div style={{ height: 10, borderRadius: 5, background: 'rgba(255,255,255,0.05)', overflow: 'hidden' }}>
                            <div style={{ height: '100%', width: `${swarmResults.final_consensus?.probabilities?.bearish}%`, background: 'var(--bear-red)' }}></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Action Execution Box */}
                    <div className="glass-panel" style={{ padding: 20, textAlign: 'center', background: 'rgba(20,28,45,0.95)', border: '1px solid var(--accent-orange)' }}>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Recommended Strategy</div>
                      <div style={{ fontSize: '1.25rem', fontWeight: 800, color: 'var(--accent-orange)', margin: '8px 0' }}>
                        {swarmResults.final_consensus?.strategy_name}
                      </div>
                      <div style={{ fontSize: '0.82rem', color: 'var(--bull-green)', fontWeight: 700, marginBottom: 16 }}>
                        Max Profit: ₹{swarmResults.final_consensus?.max_profit?.toLocaleString()}
                      </div>
                      <button className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={() => handleExecuteAgentTrade({ strategy: swarmResults.final_consensus?.recommended_strategy })}>
                        ⚡ Execute Swarm Trade ({tradeMode.toUpperCase()})
                      </button>
                    </div>
                  </div>
                </div>

                {/* Round-by-Round Swarm Logs */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Round-by-Round Agent Replay Logs</h3>
                  {swarmResults.rounds?.map((rd, rIdx) => (
                    <div key={rIdx} className="glass-panel" style={{ padding: 20 }}>
                      <h4 style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-orange)', marginBottom: 12 }}>{rd.title}</h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                        {rd.logs?.map((lg, lIdx) => (
                          <div key={lIdx} style={{ padding: 12, borderRadius: 8, background: 'rgba(5,8,14,0.6)', borderLeft: `3px solid ${lg.color}` }}>
                            <div style={{ fontSize: '0.78rem', fontWeight: 700, color: lg.color, marginBottom: 4 }}>
                              {lg.avatar} {lg.agent} ({lg.role})
                            </div>
                            <div style={{ fontSize: '0.88rem', whiteSpace: 'pre-line' }}>{lg.message}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>

              </div>
            ) : (
              <div className="glass-panel" style={{ padding: 60, textAlign: 'center', color: 'var(--text-muted)' }}>
                Click <strong>"Run MiroFish Swarm Simulation"</strong> above to trigger the parallel sandbox prediction engine!
              </div>
            )}

          </div>
        )}

        {/* ARYA AI CO-PILOT TAB */}
        {tab === 'copilot' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Arya AI Options Quantitative Assistant</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Real-time Black-Scholes Greeks analysis, delta-neutral strategies, and 1-click execution.</p>
              </div>

              <div className="glass-panel" style={{ padding: 6, display: 'flex', gap: 8 }}>
                <button className={tradeMode === 'paper' ? 'btn-primary' : 'btn-secondary'} onClick={() => setTradeMode('paper')} style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                  📄 Paper Mode (₹5L Capital)
                </button>
                <button className={tradeMode === 'real' ? 'btn-primary' : 'btn-secondary'} onClick={() => setTradeMode('real')} style={{ padding: '6px 12px', fontSize: '0.8rem', background: tradeMode === 'real' ? 'linear-gradient(135deg,#FF9800,#F44336)' : 'none' }}>
                  🔴 Live Broker (Fyers)
                </button>
              </div>
            </div>

            {executionMessage && (
              <div className="glass-panel" style={{ padding: 12, background: 'rgba(0,230,118,0.1)', border: '1px solid var(--bull-green)', color: 'var(--bull-green)', fontWeight: 700, fontSize: '0.88rem' }}>
                {executionMessage}
              </div>
            )}

            {/* Chat Box */}
            <div className="glass-panel" style={{ padding: 24, display: 'flex', flexDirection: 'column', height: 480 }}>
              <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16, paddingBottom: 16 }}>
                {chatLogs.map((m, i) => (
                  <div key={i} style={{ alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%' }}>
                    <div style={{
                      background: m.sender === 'user' ? 'rgba(255,152,0,0.15)' : 'rgba(20,28,45,0.9)',
                      border: m.sender === 'user' ? '1px solid rgba(255,152,0,0.4)' : '1px solid var(--panel-border)',
                      borderRadius: 12, padding: 14
                    }}>
                      <div style={{ fontSize: '0.75rem', color: m.sender === 'user' ? 'var(--accent-orange)' : '#FFC107', fontWeight: 700, marginBottom: 4 }}>
                        {m.sender === 'user' ? 'You' : m.agent}
                      </div>
                      <div style={{ fontSize: '0.9rem', whiteSpace: 'pre-line', lineHeight: 1.5 }}>
                        {m.text}
                      </div>
                      {m.trade_action && (
                        <div style={{ marginTop: 12, paddingTop: 10, borderTop: '1px solid rgba(255,255,255,0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--accent-orange)' }}>
                            Strategy: {m.trade_action.strategy} ({symbol})
                          </span>
                          <button className="btn-primary" style={{ padding: '6px 14px', fontSize: '0.8rem', background: 'linear-gradient(135deg,#FF9800,#FF5722)' }} onClick={() => handleExecuteAgentTrade(m.trade_action)}>
                            ⚡ Execute {tradeMode.toUpperCase()} Trade
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
                {chatLoading && <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Analyzing Options Greeks & IV Rank...</div>}
              </div>

              <div style={{ display: 'flex', gap: 8, paddingBottom: 12, overflowX: 'auto' }}>
                {[
                  "What option strategy should I run on NIFTY today?",
                  "Recommend an Iron Condor setup",
                  "Show ATM Straddle Greeks & Decay"
                ].map((p, idx) => (
                  <button key={idx} className="btn-secondary" style={{ padding: '4px 10px', fontSize: '0.75rem', whiteSpace: 'nowrap' }} onClick={(e) => handleSendChat(e, p)}>
                    💡 {p}
                  </button>
                ))}
              </div>

              <form onSubmit={handleSendChat} style={{ display: 'flex', gap: 8 }}>
                <input type="text" className="search-input" placeholder="Ask Arya AI for option strategy suggestions or market questions..." value={chatQuery} onChange={e => setChatQuery(e.target.value)} />
                <button type="submit" className="btn-primary" disabled={chatLoading} style={{ background: 'linear-gradient(135deg,#FF9800,#FF5722)' }}>
                  Ask Arya
                </button>
              </form>
            </div>
          </div>
        )}

        {/* OPTION CHAIN TAB */}
        {tab === 'chain' && chainData && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>{chainData.symbol} Live Option Chain</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Expiry: {chainData.expiry} | DTE: {chainData.days_to_expiry} days | Lot: {chainData.lot_size} | Source: {chainData.source}</p>
              </div>
            </div>
            <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
              <div style={{ overflowX: 'auto' }}>
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th colSpan="6" style={{ textAlign: 'center', color: 'var(--bull-green)', borderRight: '2px solid var(--panel-border)' }}>CALLS</th>
                      <th style={{ textAlign: 'center', color: 'var(--accent-orange)' }}>STRIKE</th>
                      <th colSpan="6" style={{ textAlign: 'center', color: 'var(--bear-red)' }}>PUTS</th>
                    </tr>
                    <tr>
                      <th>OI</th><th>Vol</th><th>IV%</th><th>LTP</th><th>Delta</th><th style={{ borderRight: '2px solid var(--panel-border)' }}>Theta</th>
                      <th style={{ textAlign: 'center' }}>₹</th>
                      <th>Delta</th><th>Theta</th><th>LTP</th><th>IV%</th><th>Vol</th><th>OI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {chainData.chain.map((row, i) => {
                      const isATM = row.moneyness === 'ATM';
                      return (
                        <tr key={i} className={isATM ? 'atm-row' : ''}>
                          <td className="mono">{(row.ce_oi / 1000).toFixed(0)}K</td>
                          <td className="mono">{(row.ce_volume / 1000).toFixed(0)}K</td>
                          <td className="mono" style={{ color: 'var(--accent-orange)' }}>{row.ce_iv}%</td>
                          <td className="mono" style={{ fontWeight: 700 }}>{row.ce_ltp}</td>
                          <td className="mono" style={{ color: 'var(--bull-green)' }}>{row.ce_delta}</td>
                          <td className="mono" style={{ color: 'var(--bear-red)', borderRight: '2px solid var(--panel-border)' }}>{row.ce_theta}</td>
                          <td className="mono" style={{ textAlign: 'center', fontWeight: 800, color: isATM ? 'var(--accent-orange)' : 'var(--text-primary)', fontSize: '0.9rem' }}>{row.strike}</td>
                          <td className="mono" style={{ color: 'var(--bull-green)' }}>{row.pe_delta}</td>
                          <td className="mono" style={{ color: 'var(--bear-red)' }}>{row.pe_theta}</td>
                          <td className="mono" style={{ fontWeight: 700 }}>{row.pe_ltp}</td>
                          <td className="mono" style={{ color: 'var(--accent-orange)' }}>{row.pe_iv}%</td>
                          <td className="mono">{(row.pe_volume / 1000).toFixed(0)}K</td>
                          <td className="mono">{(row.pe_oi / 1000).toFixed(0)}K</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* STRATEGY BUILDER TAB */}
        {tab === 'strategy' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Options Strategy Builder & Payoff Analyzer</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: 24 }}>
              <div className="glass-panel" style={{ padding: 24, display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>Select Strategy</label>
                  <select className="search-input" value={strategyKey} onChange={e => setStrategyKey(e.target.value)}>
                    {strategies.map(s => (<option key={s.key} value={s.key}>{s.name} — {s.view}</option>))}
                  </select>
                </div>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{strategies.find(s => s.key === strategyKey)?.description}</div>
                <div className="glass-panel" style={{ padding: 12 }}>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Spot Price</div>
                  <div className="mono" style={{ fontSize: '1.3rem', fontWeight: 800 }}>₹{chainData?.spot_price || 24628.5}</div>
                </div>
                <button className="btn-primary" onClick={buildStrategy}>Build & Analyze Strategy</button>
                {strategyResult && (
                  <button className="btn-secondary" onClick={executePaperTrade} style={{ borderColor: 'var(--accent-orange)' }}>
                    📄 Execute Paper Trade
                  </button>
                )}
              </div>

              {strategyResult ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                  <div className="glass-panel" style={{ padding: 24, borderLeft: '4px solid var(--accent-orange)' }}>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: 16 }}>{strategyResult.name} — Payoff Analysis</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 16 }}>
                      <div className="glass-panel" style={{ padding: 14 }}>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Max Profit</div>
                        <div className="mono" style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--bull-green)' }}>₹{strategyResult.max_profit?.toLocaleString()}</div>
                      </div>
                      <div className="glass-panel" style={{ padding: 14 }}>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Max Loss</div>
                        <div className="mono" style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--bear-red)' }}>₹{strategyResult.max_loss?.toLocaleString()}</div>
                      </div>
                      <div className="glass-panel" style={{ padding: 14 }}>
                        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Net Premium</div>
                        <div className="mono" style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--accent-orange)' }}>₹{strategyResult.net_premium_total}</div>
                      </div>
                    </div>
                  </div>

                  <div className="glass-panel" style={{ padding: 24 }}>
                    <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: 12 }}>Payoff at Expiry</h4>
                    <div style={{ height: 200, display: 'flex', alignItems: 'flex-end', gap: 2, background: 'rgba(5,8,14,0.6)', borderRadius: 8, padding: 16, position: 'relative' }}>
                      {strategyResult.payoff_curve?.map((pt, i) => {
                        const maxAbs = Math.max(...strategyResult.payoff_curve.map(p => Math.abs(p.pnl)), 1);
                        const h = Math.abs(pt.pnl) / maxAbs * 80;
                        return (<div key={i} title={`₹${pt.price}: P&L ₹${pt.pnl}`} style={{ flex: 1, height: `${h}%`, background: pt.pnl >= 0 ? 'var(--bull-green)' : 'var(--bear-red)', opacity: 0.8, borderRadius: 1 }} />);
                      })}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="glass-panel" style={{ padding: 40, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                  Select a strategy and click "Build & Analyze" to see payoff analysis.
                </div>
              )}
            </div>
          </div>
        )}

        {/* POSITIONS TAB */}
        {tab === 'positions' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Open Positions & P&L Ledger</h2>
            {positions.length > 0 ? (
              <div className="glass-panel" style={{ padding: 0, overflow: 'hidden' }}>
                <table className="custom-table">
                  <thead><tr><th>ID</th><th>Action</th><th>Symbol</th><th>Type</th><th>Strike</th><th>Qty</th><th>Entry Premium</th><th>Status</th><th>Time</th></tr></thead>
                  <tbody>
                    {positions.map((p, i) => (
                      <tr key={i}>
                        <td className="mono" style={{ color: 'var(--text-muted)' }}>{p.id || `POS_${i + 1}`}</td>
                        <td><span className={`badge ${p.action === 'SELL' ? 'badge-bear' : 'badge-bull'}`}>{p.action}</span></td>
                        <td className="mono" style={{ fontWeight: 700 }}>{p.symbol || 'NIFTY'}</td>
                        <td className="mono">{p.type}</td>
                        <td className="mono" style={{ fontWeight: 700 }}>₹{p.strike}</td>
                        <td className="mono">{p.qty}</td>
                        <td className="mono">₹{p.entry_premium || p.premium}</td>
                        <td><span className="badge badge-gold">{p.status}</span></td>
                        <td style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.time || p.timestamp?.slice(0, 19)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="glass-panel" style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
                No open positions. Execute a strategy from the MiroFish Swarm, Strategy Builder, or Arya AI tab.
              </div>
            )}
          </div>
        )}

      </main>

      {/* FYERS ACCOUNT SETUP MODAL */}
      {showFyersModal && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(8px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 999, padding: 20 }}>
          <div className="glass-panel" style={{ maxWidth: 500, width: '100%', padding: 28, position: 'relative' }}>
            <button onClick={() => setShowFyersModal(false)} style={{ position: 'absolute', top: 16, right: 16, background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1.2rem', cursor: 'pointer' }}>✕</button>

            <h3 style={{ fontSize: '1.3rem', fontWeight: 800, marginBottom: 8, color: 'var(--accent-orange)' }}>
              🔑 Fyers Broker Integration Setup
            </h3>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 20 }}>
              Enter your Fyers App Credentials from <a href="https://myapi.fyers.in/dashboard" target="_blank" rel="noreferrer" style={{ color: 'var(--accent-orange)' }}>myapi.fyers.in</a> to connect live trading.
            </p>

            {fyersMsg && (
              <div style={{ padding: 10, borderRadius: 6, background: 'rgba(255,152,0,0.15)', border: '1px solid var(--accent-orange)', fontSize: '0.82rem', marginBottom: 16, color: 'var(--accent-orange)' }}>
                {fyersMsg}
              </div>
            )}

            <form onSubmit={handleSaveFyersCreds} style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>FYERS_APP_ID (e.g. XX1234-100)</label>
                <input type="text" className="search-input" placeholder="Your Fyers App ID" value={fyersAppId} onChange={e => setFyersAppId(e.target.value)} required />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>FYERS_SECRET_KEY</label>
                <input type="password" className="search-input" placeholder="Your Fyers Secret Key" value={fyersSecretKey} onChange={e => setFyersSecretKey(e.target.value)} required />
              </div>

              <div>
                <label style={{ fontSize: '0.78rem', color: 'var(--text-muted)', display: 'block', marginBottom: 4 }}>FYERS_ACCESS_TOKEN (Optional if pre-generated)</label>
                <input type="text" className="search-input" placeholder="Daily Access Token" value={fyersAccessToken} onChange={e => setFyersAccessToken(e.target.value)} />
              </div>

              <button type="submit" className="btn-primary" style={{ marginTop: 8, justifyContent: 'center' }}>
                💾 Save Credentials & Connect Fyers
              </button>

              <button type="button" className="btn-secondary" style={{ marginTop: 6, justifyContent: 'center', borderColor: 'var(--bull-green)', color: 'var(--bull-green)', fontWeight: 700 }} onClick={async () => {
                try {
                  const r = await fetch('/api/broker/login/fyers');
                  const d = await r.json();
                  if (d.url) { window.location.href = d.url; } else { alert(d.error || 'Error getting login URL'); }
                } catch(err) { alert(err.message); }
              }}>
                ⚡ Authorize Daily Fyers Token (OAuth Login)
              </button>
            </form>
          </div>
        </div>
      )}

      <footer style={{ background: 'rgba(5,8,14,0.95)', borderTop: '1px solid var(--panel-border)', padding: '20px 28px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
        BharatAlpha Trade ⚡ — Swarm Intelligence Options & Futures Terminal | MiroFish + Fyers Broker Integration
      </footer>

    </div>
  );
}
