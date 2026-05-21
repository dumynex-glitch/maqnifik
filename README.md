# Magnific API Integration

Single-stack web application for integrating with the Magnific API. Features multi-API key management, automatic quota tracking, webhook-based async task handling, and a comprehensive UI for video, image, and audio generation.

## Features

✅ **Multi-API Key Support** - Manage up to 5 API keys with automatic round-robin rotation  
✅ **Quota Tracking** - Per-key, per-service daily quota monitoring (Free tier limits)  
✅ **Webhook Integration** - HMAC-SHA256 verified webhook receiver for async tasks  
✅ **Video Generation** - Kling 2.6 Standard (text-to-video & image-to-video)  
✅ **Image Generation** - Mystic, Flux, and other models  
✅ **Image Editing** - Upscale, background removal, relight, style transfer  
✅ **Audio Generation** - Voiceover, sound effects, audio isolation  
✅ **Gallery** - Automatic gallery with favorites and filtering  
✅ **Real-time Logging** - Structured JSON logs with UI viewer  
✅ **Dashboard** - Comprehensive stats, quota charts, recent activity  
✅ **Single-Stack** - FastAPI backend serves Next.js static frontend on one port  

## Architecture

- **Backend**: Python FastAPI with async SQLAlchemy (SQLite)
- **Frontend**: Next.js 14 (static export) with TypeScript and Tailwind CSS
- **Deployment**: Single port (8000), runs as one process
- **Storage**: SQLite database + file-based cache

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm

### Installation

1. **Clone and navigate to project:**
```bash
cd /home/debian/maqnific
```

2. **Build the application:**
```bash
./build.sh
```

This will:
- Install frontend dependencies
- Build Next.js static export
- Copy static files to backend
- Install Python dependencies

3. **Run the application:**
```bash
cd backend
python run.py
```

4. **Access the app:**
- Main UI: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/api/health

### Initial Configuration

1. Navigate to **Settings** (http://localhost:8000/settings)
2. Add 1-5 Magnific API keys
3. Configure webhook URL (use ngrok for local testing)
4. Optionally add webhook secret for HMAC verification
5. Save configuration

## Project Structure

```
magnific-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app + static serving
│   │   ├── config.py            # Configuration
│   │   ├── database.py          # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/            # Business logic
│   │   │   ├── magnific_client.py
│   │   │   ├── key_rotation.py
│   │   │   ├── quota_manager.py
│   │   │   ├── task_manager.py
│   │   │   ├── gallery_service.py
│   │   │   ├── cache_service.py
│   │   │   └── logger_service.py
│   │   ├── routes/              # API endpoints
│   │   └── utils/               # Utilities
│   ├── data/                    # SQLite + cache + logs
│   ├── static/                  # Next.js build output
│   ├── requirements.txt
│   └── run.py                   # Entry point
├── frontend/
│   ├── app/                     # Next.js pages
│   ├── components/              # React components
│   ├── lib/                     # API client + types
│   └── package.json
├── build.sh                     # Build script
├── Dockerfile
└── docker-compose.yml
```

## API Endpoints

### Configuration
- `POST /api/config/keys` - Save API keys and webhook config
- `GET /api/config/keys` - Get current configuration (masked)

### Dashboard
- `GET /api/dashboard/stats` - Get comprehensive dashboard statistics

### Video Generation
- `POST /api/video/generate` - Generate video (Kling 2.6 std)

### Image Generation
- `POST /api/image/generate` - Generate image (Mystic, Flux, etc.)

### Image Editing
- `POST /api/editing/upscale` - Upscale image
- `POST /api/editing/remove-background` - Remove background
- `POST /api/editing/relight` - Relight image
- `POST /api/editing/style-transfer` - Apply style transfer

### Audio Generation
- `POST /api/audio/generate` - Generate audio (voiceover, sound effects)

### Gallery
- `GET /api/gallery` - Get gallery items
- `POST /api/gallery/{id}/favorite` - Toggle favorite
- `DELETE /api/gallery/{id}` - Delete item

### Tasks
- `GET /api/tasks` - Get all tasks
- `GET /api/tasks/{task_id}` - Get task by ID

### Logs
- `GET /api/logs` - Get application logs with filtering

### Webhooks
- `POST /api/webhooks/magnific` - Receive Magnific webhooks

## Docker Deployment

### Build and run with Docker:

```bash
docker build -t magnific-app .
docker run -p 8000:8000 -v $(pwd)/backend/data:/app/backend/data magnific-app
```

### Or use Docker Compose:

```bash
docker-compose up -d
```

## Webhook Setup

### For Local Development (ngrok):

1. Install ngrok: https://ngrok.com/download
2. Start ngrok tunnel:
```bash
ngrok http 8000
```
3. Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)
4. In Settings, set webhook URL to: `https://abc123.ngrok.io/api/webhooks/magnific`
5. Generate a webhook secret and save it

### For Production:

1. Deploy app to server with public domain
2. Set webhook URL to: `https://yourdomain.com/api/webhooks/magnific`
3. Generate and save webhook secret
4. Ensure HTTPS is enabled (required by Magnific)

## Quota Management

The app tracks daily quota usage per API key per service based on Magnific's Free tier limits:

- **Kling 2.6 Standard**: 5 requests/day
- **Mystic**: 125 requests/day
- **Flux Pro/Dev**: 100 requests/day
- **Image Upscaler**: 125 requests/day
- **Background Removal**: 300 requests/day

When a key exhausts its quota, the app automatically rotates to the next available key.

## Development

### Backend Development:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend Development:

```bash
cd frontend
npm install
npm run dev  # Runs on port 3000
```

For development, frontend proxies API requests to backend on port 8000.

## Troubleshooting

### Frontend not showing:
```bash
./build.sh  # Rebuild frontend
```

### Database issues:
```bash
rm backend/data/database.db  # Reset database
python backend/run.py  # Recreates database
```

### Webhook not receiving:
- Check ngrok is running
- Verify webhook URL in Settings
- Check webhook secret matches
- View logs at http://localhost:8000/logs

### Quota exhausted:
- Add more API keys in Settings
- Check quota status in Dashboard
- Wait for daily reset (UTC midnight)

## Security Notes

- API keys are hashed (SHA256) before storage
- Webhook signatures verified with HMAC-SHA256
- No API keys exposed to frontend
- Server-to-server communication only

## License

MIT

## Support

For issues or questions:
- Check logs: http://localhost:8000/logs
- API documentation: http://localhost:8000/docs
- Magnific API docs: https://docs.magnific.com
