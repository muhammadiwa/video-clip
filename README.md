# Viral Clip AI

AI-powered video editing platform that automatically transforms long videos into viral short clips with subtitles, voice-overs, and professional editing.

## Features

- 🎬 AI-powered viral clip detection
- 📝 Automatic subtitle generation with custom styling
- 🎙️ Multi-language voice-over
- ✂️ Advanced video editor (trim, split, merge)
- 🎨 Brand kit & templates
- 📤 Batch export for multiple platforms
- 🔗 YouTube & direct upload support

## Tech Stack

### Frontend
- Next.js 14 (React)
- TypeScript
- Tailwind CSS
- Three.js (3D animations)
- Fabric.js (Canvas editing)

### Backend
- FastAPI (Python)
- PostgreSQL
- Redis (Job queue)
- FFmpeg (Video processing)
- OpenAI Whisper (Speech-to-text)

## Project Structure

```
video-clip/
├── backend/          # FastAPI backend
├── frontend/         # Next.js frontend
├── docker/           # Docker configurations
└── docs/             # Documentation
```

## Getting Started

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

## Development Phases

- ✅ Phase 1: Foundation (Project setup, basic upload, video player)
- ⏳ Phase 2: AI Core (YouTube downloader, transcription, scene detection)
- ⏳ Phase 3: Editor MVP (Timeline, trim/split, subtitle overlay)
- ⏳ Phase 4: Advanced Features (Multi-track, voice-over, brand kit)
- ⏳ Phase 5: UI/UX Polish (3D animations, glassmorphism)
- ⏳ Phase 6: Integration (Social media APIs, auto-upload)

## License

MIT
