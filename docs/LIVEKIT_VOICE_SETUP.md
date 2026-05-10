# Nexora AI LiveKit Voice Setup

Nexora AI now includes a LiveKit-ready voice layer.

## Backend route

```text
POST /media/voice/livekit-token
```

This route creates a LiveKit room token for the logged-in user.

## Required environment variables

Add these values to `.env`:

```env
LIVEKIT_URL=wss://your-livekit-server.example.com
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_DEFAULT_ROOM=nexora-voice
```

## Local development options

You can use:

1. LiveKit Cloud
2. A self-hosted LiveKit server
3. Dockerized LiveKit on your own VPS

## What is implemented

- LiveKit dependency in `backend/requirements.txt`
- LiveKit configuration in `backend/app/config.py`
- Token generation service in `backend/app/services/livekit_service.py`
- Voice token endpoint in `backend/app/routers/media.py`
- Nexora UI label for LiveKit voice interaction

## What still needs frontend wiring

To make the microphone button join a real room, add the LiveKit frontend SDK:

```bash
npm install livekit-client
```

Then call:

```text
POST /media/voice/livekit-token
```

Use the returned `url`, `room`, and `token` to connect the browser to the LiveKit room.

## Recommended next step

Add a `VoiceRoom.jsx` component that:

1. Requests `/media/voice/livekit-token`
2. Connects with `livekit-client`
3. Publishes the microphone track
4. Subscribes to AI or user audio tracks
5. Displays room connection status
