import React, { useState } from "react";

const API = "http://localhost:8000";

export default function App() {
  const [email, setEmail] = useState("admin@koai.local");
  const [password, setPassword] = useState("admin12345");
  const [jwt, setJwt] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [prompt, setPrompt] = useState("Use my uploaded documents if relevant. Explain what K.O. AI Cloud can do.");
  const [answer, setAnswer] = useState("");
  const [status, setStatus] = useState("");
  const [file, setFile] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  async function register() {
    const res = await fetch(`${API}/auth/register`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    setStatus(JSON.stringify(await res.json(), null, 2));
  }

  async function login() {
    const res = await fetch(`${API}/auth/login`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ email, password }) });
    const data = await res.json();
    setJwt(data.access_token || "");
    setStatus(JSON.stringify(data, null, 2));
  }

  async function createKey() {
    const res = await fetch(`${API}/api-keys`, { method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${jwt}` }, body: JSON.stringify({ name: "Dashboard Key" }) });
    const data = await res.json();
    setApiKey(data.key || "");
    setStatus(JSON.stringify(data, null, 2));
  }

  async function upload() {
    if (!file) return;
    const body = new FormData();
    body.append("file", file);
    const res = await fetch(`${API}/files/upload`, { method: "POST", headers: { Authorization: `Bearer ${jwt}` }, body });
    setStatus(JSON.stringify(await res.json(), null, 2));
  }

  async function normalChat() {
    setAnswer("Thinking locally...");
    const res = await fetch(`${API}/v1/chat/completions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ messages: [{ role: "user", content: prompt }], max_tokens: 1600, use_rag: true, session_id: "dashboard" })
    });
    const data = await res.json();
    setAnswer(data.response || JSON.stringify(data, null, 2));
  }

  async function streamingChat() {
    setAnswer("");
    const res = await fetch(`${API}/v1/chat/stream`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${apiKey}` },
      body: JSON.stringify({ messages: [{ role: "user", content: prompt }], max_tokens: 1600, use_rag: true, session_id: "dashboard-stream" })
    });
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const events = buffer.split("\n\n");
      buffer = events.pop() || "";
      for (const event of events) {
        const line = event.split("\n").find(x => x.startsWith("data: "));
        if (!line) continue;
        const json = line.replace("data: ", "");
        if (json === "{}") continue;
        try {
          const data = JSON.parse(json);
          if (data.token) setAnswer(prev => prev + data.token);
        } catch {}
      }
    }
  }

  async function loadAnalytics() {
    const res = await fetch(`${API}/admin/analytics`, { headers: { Authorization: `Bearer ${jwt}` } });
    setAnalytics(await res.json());
  }

  return (
    <main className="page">
      <section className="hero">
        <h1>K.O. AI Cloud v2</h1>
        <p>Standalone local AI platform with streaming chat, RAG memory, file upload, API keys, analytics, voice/image scaffolds, and distributed GPU routing.</p>
      </section>

      <section className="grid">
        <div className="card">
          <h2>Account</h2>
          <input value={email} onChange={e => setEmail(e.target.value)} />
          <input value={password} onChange={e => setPassword(e.target.value)} type="password" />
          <button onClick={register}>Register</button>
          <button onClick={login}>Login</button>
        </div>

        <div className="card">
          <h2>API Key</h2>
          <button disabled={!jwt} onClick={createKey}>Generate API Key</button>
          <textarea value={apiKey} readOnly placeholder="API key appears once" />
        </div>
      </section>

      <section className="card">
        <h2>RAG File Upload</h2>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
        <button disabled={!jwt || !file} onClick={upload}>Upload + Index in Qdrant</button>
      </section>

      <section className="card">
        <h2>Streaming Local AI Chat</h2>
        <textarea value={prompt} onChange={e => setPrompt(e.target.value)} />
        <button disabled={!apiKey} onClick={normalChat}>Normal Chat</button>
        <button disabled={!apiKey} onClick={streamingChat}>Streaming Chat</button>
        <pre>{answer}</pre>
      </section>

      <section className="card">
        <h2>Admin Analytics</h2>
        <button disabled={!jwt} onClick={loadAnalytics}>Load Analytics</button>
        <pre>{analytics ? JSON.stringify(analytics, null, 2) : "No analytics loaded"}</pre>
      </section>

      <section className="card">
        <h2>Status</h2>
        <pre>{status}</pre>
      </section>
    </main>
  );
}
