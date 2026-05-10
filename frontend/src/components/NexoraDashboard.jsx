import React, { useState } from "react";

function MetricBar({ label, value, text }) {
  return (
    <div className="metric-row">
      <div className="metric-label"><span>{label}</span><b>{text}</b></div>
      <div className="bar"><span style={{ width: `${value}%` }} /></div>
    </div>
  );
}

function Suggestion({ icon, title, body }) {
  return (
    <button className="suggestion" type="button">
      <span className="suggestion-icon">{icon}</span>
      <span><b>{title}</b><small>{body}</small></span>
      <em>→</em>
    </button>
  );
}

function RecentChat({ title, time }) {
  return (
    <div className="recent-item">
      <span className="chat-dot">▣</span>
      <span>{title}</span>
      <small>{time}</small>
      <b>⋮</b>
    </div>
  );
}

export default function NexoraDashboard() {
  const [prompt, setPrompt] = useState("");
  const [answer, setAnswer] = useState("");
  const [fileName, setFileName] = useState("");
  const adminEmail = "krishanavinash@gmail.com";
  const adminName = "Krishan Avinash";

  function demoReply() {
    const text = prompt.trim() || "Ask me anything...";
    setAnswer(`Nexora AI is ready. Your prompt was: ${text}\n\nBackend services are available for streaming chat, RAG memory, file uploads, analytics, local embeddings, LiveKit voice rooms, image workers, and distributed model routing.`);
  }

  return (
    <div className="nexora-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brain">✺</div><h1>NEXORA <span>AI</span></h1></div>
        <nav>
          <a className="active">♙ AI Assistant</a>
          <a>▦ Dashboard</a>
          <a>▥ Analytics</a>
          <a>▣ Data Hub</a>
          <a>⚭ Automations</a>
          <a>✾ Models</a>
          <a>⌘ Integrations</a>
          <a>⚙ Settings</a>
        </nav>
        <div className="upgrade-card"><div className="crown">♕</div><h3>Upgrade to Pro</h3><p>Unlock advanced models, longer context, LiveKit voice, and premium automations.</p><button>Upgrade Now</button></div>
        <div className="profile"><div className="avatar">K</div><div><b>{adminName}</b><small>{adminEmail}</small></div><span>⌄</span></div>
      </aside>

      <main className="workspace">
        <header className="topbar">
          <div><h2>AI Assistant</h2><p>Your intelligent partner for knowledge, insights, and automation.</p></div>
          <div className="top-widgets">
            <div className="status-pill"><b>System Status</b><span><i />All Systems Operational</span></div>
            <div className="usage-pill"><b>Usage <em>78%</em></b><span><i style={{ width: "78%" }} /></span><small>7.8K / 10K requests</small></div>
            <button className="plan-btn">♕ Upgrade Plan</button>
            <span className="top-icon">⌕</span><span className="top-icon">♧</span><span className="top-icon">☼</span>
          </div>
        </header>

        <section className="layout-grid">
          <section className="center-column">
            <div className="assistant-card">
              <div className="card-title"><span><span className="orb">✦</span><b>AI Assistant</b></span><button>×</button></div>
              <div className="welcome"><h3>Hello, Krishan</h3><p>How can I help you today?</p></div>
              <div className="prompt-box">
                <textarea value={prompt} onChange={(event) => setPrompt(event.target.value)} placeholder="Ask me anything..." />
                <div className="prompt-actions">
                  <button className="circle">＋</button>
                  <label className="pill-input">◎ Upload<input type="file" onChange={(event) => setFileName(event.target.files?.[0]?.name || "")} /></label>
                  <button className="pill-input">Web Search⌄</button>
                  <button className="mode-pill">♧ Smart Mode⌄</button>
                  <button className="send-btn" onClick={demoReply}>➤</button>
                </div>
                {fileName && <small className="file-chip">Selected: {fileName}</small>}
              </div>
              {answer && <div className="answer-panel"><b>Nexora AI Response</b><pre>{answer}</pre></div>}
            </div>

            <div className="prompt-suggestions">
              <div className="section-head"><b>Prompt Suggestions</b><button>⟳</button></div>
              <div className="suggestion-grid">
                <Suggestion icon="▥" title="Analyze this data" body="Upload a dataset and extract key insights." />
                <Suggestion icon="▤" title="Write a report" body="Generate a detailed report on a topic." />
                <Suggestion icon="◌" title="Explain a concept" body="Break down complex ideas simply." />
                <Suggestion icon="⌘" title="Create a workflow" body="Build an automation workflow." />
              </div>
            </div>

            <div className="recent-card">
              <div className="section-head"><b>Recent Chats</b><button>View All</button></div>
              <div className="recent-grid">
                <RecentChat title="Q3 Sales Performance Analysis" time="2m ago" />
                <RecentChat title="Marketing Campaign Ideas" time="5h ago" />
                <RecentChat title="Customer Sentiment Review" time="1h ago" />
                <RecentChat title="Product Roadmap Planning" time="1d ago" />
                <RecentChat title="Competitor Benchmark Report" time="3h ago" />
                <RecentChat title="Financial Forecasting Model" time="2d ago" />
              </div>
            </div>
          </section>

          <aside className="right-column">
            <div className="panel model-panel"><div className="section-head"><b>◉ Model Status</b><button>View All</button></div><div className="model-content"><div className="ring"><span>Local Model<small>● Active</small></span></div><div className="model-bars"><MetricBar label="Accuracy" value={96} text="96%" /><MetricBar label="Speed" value={66} text="1.2s" /><MetricBar label="Reliability" value={99} text="99.1%" /></div></div></div>
            <div className="panel memory-panel"><div className="section-head"><b>Memory & Context</b><button>Manage</button></div><div className="memory-row"><span>▣</span><b>Context Window</b><em>32K / 128K tokens</em></div><div className="bar large"><span style={{ width: "58%" }} /></div><div className="memory-row"><span>◎</span><b>Conversation Memory</b><em className="green">● High</em></div><div className="memory-row"><span>▤</span><b>Knowledge Base</b><em>Nexora Knowledge Hub</em></div></div>
            <div className="panel voice-panel"><div className="section-head"><b>LiveKit Voice Interaction</b><span>00:00:00</span></div><div className="wave"><span /><span /><span /><span /><button>🎙</button><span /><span /><span /><span /></div><div className="voice-controls"><button>Voice: Nova⌄</button><button>LiveKit</button></div></div>
            <div className="panel quick-panel"><div className="section-head"><b>Quick Actions</b><button>Edit</button></div><div className="quick-grid"><button>▤<span>Summarize<br/>Document</span></button><button>▥<span>Analyze<br/>Data</span></button><button>⌘<span>Generate<br/>Code</span></button><button>⚭<span>Translate<br/>Text</span></button></div></div>
          </aside>
        </section>
      </main>
    </div>
  );
}
