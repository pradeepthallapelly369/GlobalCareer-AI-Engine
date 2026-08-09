import React, { useState } from 'react';
import './App.css';
import './index.css';

const DEFAULT_FII = {
  bio: "Managing Director at a London-based Emerging Markets Hedge Fund. Focused on alpha generation in South Asian equities. Always watching the US Fed.",
  persona: "Arthur is a 45-year-old Managing Director at 'Thames Capital,' a fictitious London-based hedge fund specializing in emerging markets with a heavy portfolio weight in Indian equities (Nifty 50). He has 20 years of experience in global macro trading.\n\nBackground: Arthur started his career during the 2008 financial crisis, making him inherently risk-averse and highly sensitive to liquidity drains. He currently manages a $500M portfolio heavily exposed to Indian Financials and IT blue-chips.\n\nCharacter Traits: He is an INTJ—analytical, unsentimental, and data-driven. He expresses himself professionally but can be ruthlessly blunt about valuations when speaking with other market participants.\n\nBehavioral Logic: Arthur completely ignores 'retail hype' and focuses strictly on macroeconomic indicators: US Treasury yields, the RBI repo rate, the DXY (US Dollar Index), and FII/DII flow data. If the US Fed signals higher interest rates, Arthur's immediate reflex is to sell Indian equities to protect against currency depreciation (INR dropping against USD).\n\nStance & Views: He believes Indian mid-caps are currently dangerously overvalued, driven by irrational retail exuberance through SIPs. He is constantly looking for an excuse to short the mid-cap index. He will aggressively debate domestic investors who claim 'India is decoupled from global markets.'\n\nPersonal Memory: Arthur has been net-selling his positions in Indian IT stocks over the past two weeks due to weak guidance from TCS and Infosys. He is currently hoarding cash, waiting to see if the RBI will hike rates by 50 basis points before deploying capital back into the banking sector.",
  age: 45,
  gender: "male",
  mbti: "INTJ",
  country: "United Kingdom",
  profession: "FII Hedge Fund Manager",
  interested_topics: "Global Macroeconomics, US Federal Reserve Rates, Indian Banking Sector, USD/INR Currency Pair, Emerging Market Valuations"
};

const DEFAULT_RETAIL = {
  bio: "Software Engineer by day, Option Buyer by passion. Believes in the 'India Growth Story'. Every dip is a buying opportunity! 🚀",
  persona: "Rahul is a 28-year-old software developer based in Bengaluru. He grew up during the post-COVID bull run, meaning he has never experienced a prolonged, multi-year bear market. He trades actively using modern discount broker apps.\n\nBackground: He allocates 40% of his monthly salary to aggressive SIPs (Systematic Investment Plans) in Small and Mid-cap mutual funds, but uses his bonus money to trade high-risk Nifty and BankNifty weekly options.\n\nCharacter Traits: He is an ESTP—action-oriented, risk-tolerant, and highly susceptible to FOMO (Fear Of Missing Out). He is an optimist who gets easily excited by green market days and tends to panic-hold (rather than stop-loss) during red days, hoping for a quick V-shaped recovery.\n\nBehavioral Logic: Rahul gets most of his financial news from 'Finfluencers' on YouTube and Twitter, rather than reading dense RBI policy documents. He largely ignores global macroeconomic indicators like US bond yields. His trading style is purely momentum and sentiment-driven. If he sees consecutive green candles or a breakout on a chart, he buys heavily.\n\nStance & Views: He is a permabull. He strongly believes that 'India is decoupled from the world' and that domestic retail power will easily absorb any foreign selling. He mocks cautious institutional investors, often proudly posting screenshots of his profitable trades online.\n\nPersonal Memory: Rahul is currently sitting on a heavy loss in his IT sector portfolio due to recent poor earnings, but he refuses to sell. In the face of a potential RBI rate hike, his immediate reaction will be to wait for the market to drop, and then buy call options at the bottom, anticipating a massive short-covering rally.",
  age: 28,
  gender: "male",
  mbti: "ESTP",
  country: "India",
  profession: "Retail F&O Trader / Software Engineer",
  interested_topics: "BankNifty Weekly Options, Small and Mid-cap Breakouts, Discount Broking Apps, Technical Chart Patterns, FinTwit Sentiments"
};

const EMPTY_AGENT = {
  bio: "",
  persona: "",
  age: 30,
  gender: "other",
  mbti: "INTJ",
  country: "Unknown",
  profession: "",
  interested_topics: ""
};

function App() {
  const [agent, setAgent] = useState(DEFAULT_RETAIL);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setAgent({
      ...agent,
      [name]: name === 'age' ? parseInt(value) || 0 : value
    });
  };

  const handleCopy = () => {
    const dataToExport = {
      ...agent,
      interested_topics: agent.interested_topics.split(',').map(s => s.trim())
    };
    navigator.clipboard.writeText(JSON.stringify(dataToExport, null, 2));
    alert("Copied to clipboard!");
  };

  const dataToExport = {
    ...agent,
    interested_topics: agent.interested_topics.split(',').map(s => s.trim()).filter(s => s.length > 0)
  };

  const jsonString = JSON.stringify(dataToExport, null, 2);

  return (
    <div className="app-container">
      <div className="glass-header">
        <h1>MiroFish Agent Studio</h1>
        <p>Design complex AI swarm agents predicting the global markets</p>
      </div>

      <div className="template-bar glass-panel">
        <h3>Quick Templates</h3>
        <div className="template-buttons">
          <button onClick={() => setAgent(DEFAULT_RETAIL)} className="btn-vibrant">🚀 Individual Retail Trader</button>
          <button onClick={() => setAgent(DEFAULT_FII)} className="btn-vibrant">🏢 FII Hedge Fund</button>
          <button onClick={() => setAgent(EMPTY_AGENT)} className="btn-outline">Reset</button>
        </div>
      </div>

      <div className="studio-layout">
        <div className="form-container glass-panel">
          <h2>Agent Configuration</h2>
          
          <div className="form-group row-group">
            <div className="input-group">
              <label>Age</label>
              <input type="number" name="age" value={agent.age} onChange={handleInputChange} />
            </div>
            <div className="input-group">
              <label>Gender</label>
              <select name="gender" value={agent.gender} onChange={handleInputChange}>
                <option value="male">Male</option>
                <option value="female">Female</option>
                <option value="other">Other (Institution)</option>
              </select>
            </div>
            <div className="input-group">
              <label>MBTI</label>
              <select name="mbti" value={agent.mbti} onChange={handleInputChange}>
                <option value="INTJ">INTJ</option>
                <option value="ENTP">ENTP</option>
                <option value="ESTP">ESTP</option>
                <option value="INFJ">INFJ</option>
                <option value="ISTJ">ISTJ</option>
              </select>
            </div>
          </div>

          <div className="form-group row-group">
             <div className="input-group">
              <label>Profession</label>
              <input type="text" name="profession" value={agent.profession} onChange={handleInputChange} />
            </div>
            <div className="input-group">
              <label>Country</label>
              <input type="text" name="country" value={agent.country} onChange={handleInputChange} />
            </div>
          </div>

          <div className="form-group">
            <label>Bio (Social Media Profile)</label>
            <textarea name="bio" rows="2" value={agent.bio} onChange={handleInputChange}></textarea>
          </div>

          <div className="form-group">
            <label>Interested Topics (Comma separated)</label>
            <input type="text" name="interested_topics" value={agent.interested_topics} onChange={handleInputChange} />
          </div>

          <div className="form-group">
            <label>Deep Persona Logic (Simulation Brain)</label>
            <textarea name="persona" rows="12" value={agent.persona} onChange={handleInputChange}></textarea>
          </div>

        </div>

        <div className="preview-container glass-panel">
          <div className="preview-header">
            <h2>Live JSON Preview</h2>
            <button onClick={handleCopy} className="btn-copy">Copy JSON</button>
          </div>
          <div className="code-window">
            <pre>
              <code>{jsonString}</code>
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
