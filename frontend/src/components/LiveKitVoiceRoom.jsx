import React, { useRef, useState } from "react";
import { Room, RoomEvent, createLocalAudioTrack } from "livekit-client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function LiveKitVoiceRoom({ loginToken, roomName = "nexora-voice" }) {
  const roomRef = useRef(null);
  const [status, setStatus] = useState("disconnected");
  const [error, setError] = useState("");
  const [participants, setParticipants] = useState([]);

  async function fetchToken() {
    const response = await fetch(`${API_URL}/media/voice/livekit-token`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${loginToken}`,
      },
      body: JSON.stringify({ room: roomName }),
    });
    const data = await response.json();
    if (!response.ok || data.status !== "ready") {
      throw new Error(data.detail || data.message || "LiveKit is not configured yet.");
    }
    return data;
  }

  async function connect() {
    setError("");
    setStatus("connecting");
    try {
      const data = await fetchToken();
      const room = new Room({ adaptiveStream: true, dynacast: true });
      room.on(RoomEvent.ParticipantConnected, () => {
        setParticipants(Array.from(room.remoteParticipants.values()).map((p) => p.identity));
      });
      room.on(RoomEvent.ParticipantDisconnected, () => {
        setParticipants(Array.from(room.remoteParticipants.values()).map((p) => p.identity));
      });
      await room.connect(data.url, data.token);
      const audioTrack = await createLocalAudioTrack({ echoCancellation: true, noiseSuppression: true });
      await room.localParticipant.publishTrack(audioTrack);
      roomRef.current = room;
      setStatus("connected");
      setParticipants(Array.from(room.remoteParticipants.values()).map((p) => p.identity));
    } catch (err) {
      setStatus("error");
      setError(err.message || String(err));
    }
  }

  async function disconnect() {
    if (roomRef.current) {
      roomRef.current.disconnect();
      roomRef.current = null;
    }
    setParticipants([]);
    setStatus("disconnected");
  }

  return (
    <div className="livekit-room">
      <div className="section-head"><b>LiveKit Voice Room</b><span>{status}</span></div>
      <div className="voice-controls">
        <button disabled={!loginToken || status === "connected" || status === "connecting"} onClick={connect}>Connect Voice</button>
        <button disabled={status !== "connected"} onClick={disconnect}>Disconnect</button>
      </div>
      {error && <small className="voice-error">{error}</small>}
      <small>Room: {roomName}</small>
      <small>Participants: {participants.length ? participants.join(", ") : "none"}</small>
    </div>
  );
}
