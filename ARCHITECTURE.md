# 🏗️ Viral Clip AI Generator - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIRAL CLIP AI GENERATOR                      │
└─────────────────────────────────────────────────────────────────┘

INPUT SOURCES
┌──────────────┐        ┌──────────────┐
│   YouTube    │   OR   │ Local Video  │
│     URL      │        │     File     │
└──────┬───────┘        └──────┬───────┘
       │                       │
       └───────────┬───────────┘
                   ↓
           ┌───────────────┐
           │  DOWNLOADER   │
           │   youtube.py  │
           └───────┬───────┘
                   ↓
           ┌───────────────┐
           │  Video File   │
           │   (.mp4)      │
           └───────┬───────┘
                   ↓
    ┌──────────────────────────────┐
    │       VIDEO PROCESSOR        │
    │                              │
    │  ┌────────────────────┐     │
    │  │  Scene Detector    │     │
    │  │ scene_detector.py  │     │
    │  └────────┬───────────┘     │
    │           ↓                  │
    │  ┌────────────────────┐     │
    │  │   Video Editor     │     │
    │  │  video_editor.py   │     │
    │  └────────┬───────────┘     │
    └───────────┼──────────────────┘
                ↓
    ┌──────────────────────────────┐
    │   CONTENT GENERATORS         │
    │                              │
    │  ┌────────────────────┐     │
    │  │ Subtitle Generator │     │
    │  │subtitle_generator.py│    │
    │  └────────┬───────────┘     │
    │           │                  │
    │  ┌────────┴───────────┐     │
    │  │ Content Generator  │     │
    │  │content_generator.py│     │
    │  └────────┬───────────┘     │
    └───────────┼──────────────────┘
                ↓
         OUTPUT FILES
    ┌────────────────────┐
    │  Viral Clips       │
    │  ├─ video.mp4      │
    │  ├─ subtitles.srt  │
    │  ├─ thumbnail.jpg  │
    │  └─ metadata.json  │
    └────────────────────┘
```

## Component Flow

### 1. Input Stage
```
User Input (URL/File)
       ↓
[YouTubeDownloader] → Validates URL
       ↓
[VideoManager] → Downloads/Loads video
       ↓
Video File Ready
```

### 2. Analysis Stage
```
Video File
       ↓
[SceneDetector] → Detects scene changes
       ↓
Scene List [(start, end), ...]
       ↓
[get_best_moments()] → Scores and ranks scenes
       ↓
Best Moments List
```

### 3. Processing Stage
```
Best Moments + Video File
       ↓
[VideoEditor.extract_clip()]
       ├→ Extracts subclip
       ├→ Converts to 9:16 format
       └→ Saves as MP4
       ↓
Clip Files
```

### 4. Enhancement Stage
```
Clip Files
       ↓
├─ [SubtitleGenerator]
│       ├→ Extracts audio
│       ├→ Transcribes with Whisper
│       └→ Generates SRT file
│
├─ [VideoEditor.extract_thumbnail()]
│       └→ Extracts frame as JPG
│
└─ [ContentGenerator]
        ├→ Analyzes content
        ├→ Calls OpenAI API (or fallback)
        └→ Generates viral content
       ↓
Enhanced Output
```

### 5. Output Stage
```
All Components Ready
       ↓
[ViralClipGenerator] → Assembles metadata
       ↓
Saves to output/ directory
       ├─ clips/video.mp4
       ├─ clips/subtitles.srt
       ├─ thumbnails/thumb.jpg
       └─ metadata/info.json
```

## Data Flow

### Main Application Flow
```python
ViralClipGenerator.process_youtube_video()
    ↓
1. YouTubeDownloader.download(url)
    → Returns: {path, title, description, ...}
    ↓
2. SceneDetector.detect_scenes(video_path)
    → Returns: [(start, end), ...]
    ↓
3. SceneDetector.get_best_moments(scenes)
    → Returns: [best_moments]
    ↓
4. For each moment:
    ↓
    4a. VideoEditor.extract_clip(start, end)
        → Saves: clip.mp4
    ↓
    4b. VideoEditor.extract_thumbnail(clip)
        → Saves: thumbnail.jpg
    ↓
    4c. SubtitleGenerator.generate_subtitles(clip)
        → Saves: subtitles.srt
        → Returns: transcript text
    ↓
    4d. ContentGenerator.generate_viral_content()
        → Returns: {title, description, tags, hashtags}
    ↓
    4e. Save metadata.json
        → Combines all information
    ↓
5. Return results list
```

## Module Dependencies

```
cli.py
  └── src.main.ViralClipGenerator
       ├── src.downloader.youtube.YouTubeDownloader
       │    └── yt_dlp
       ├── src.processor.scene_detector.SceneDetector
       │    └── scenedetect
       ├── src.processor.video_editor.VideoEditor
       │    ├── moviepy
       │    └── PIL
       ├── src.generator.content_generator.ContentGenerator
       │    └── openai
       ├── src.generator.subtitle_generator.SubtitleGenerator
       │    ├── whisper
       │    └── moviepy
       └── src.utils
            ├── config.py (dotenv)
            └── logger.py (colorama)
```

## Configuration Flow

```
.env file
    ↓
[load_dotenv()]
    ↓
Config class
    ├── API_KEYS
    ├── DIRECTORIES
    ├── VIDEO_SETTINGS
    └── SCENE_SETTINGS
    ↓
Used by all modules
```

## Error Handling Strategy

```
User Action
    ↓
Try: Execute operation
    ↓
├─ Success → Log info → Continue
│
└─ Exception caught
       ↓
    Log error
       ↓
    ├─ Recoverable? 
    │   ├─ Yes → Use fallback → Continue
    │   └─ No → Propagate exception
    ↓
User informed via logs/error message
```

## CLI Command Flow

### YouTube Command
```bash
python cli.py youtube URL --clips 3
    ↓
1. Parse arguments (click)
2. Validate parameters
3. Create ViralClipGenerator instance
4. Call process_youtube_video()
5. Display results
6. Show file locations
```

### Local Command
```bash
python cli.py local video.mp4 --clips 5
    ↓
1. Parse arguments (click)
2. Validate file exists
3. Create ViralClipGenerator instance
4. Call process_local_video()
5. Display results
6. Show file locations
```

### Setup Command
```bash
python cli.py setup
    ↓
1. Create output directories
2. Check API key
3. Display status
4. Show next steps
```

## Processing Pipeline

### Optimized for Performance
```
┌──────────────────────────────────────┐
│         Video Processing             │
│  (Most time-consuming operation)     │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│      Scene Detection (Async)         │
│  ├─ Downscale for speed              │
│  ├─ Content detection algorithm      │
│  └─ Scene boundary detection         │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│    Parallel Processing (Per Clip)    │
│  ├─ Video extraction                 │
│  ├─ Thumbnail generation             │
│  ├─ Subtitle generation (optional)   │
│  └─ Content generation (API call)    │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│      Output Assembly                 │
│  └─ Write all files to disk          │
└──────────────────────────────────────┘
```

## Memory Management

```
Video File (Source)
    ↓
Load → Process → Close
    ↓
Clip 1: Load → Process → Write → Close → Clean
Clip 2: Load → Process → Write → Close → Clean
Clip 3: Load → Process → Write → Close → Clean
    ↓
Temp Files Cleaned
    ↓
Final Output Ready
```

## API Integration

### OpenAI Integration
```
User Request
    ↓
Check API Key
    ├─ Present?
    │   ├─ Yes → Call OpenAI API
    │   │       ├─ Success → Parse response
    │   │       └─ Error → Use fallback
    │   └─ No → Use fallback
    ↓
Return generated content
```

### Whisper Integration
```
Video/Audio File
    ↓
Load Whisper Model (lazy)
    ↓
Extract Audio → WAV file
    ↓
Transcribe
    ├─ Generate segments
    ├─ Timestamps
    └─ Full text
    ↓
Format as SRT
    ↓
Clean temp audio file
```

## Extensibility Points

### Adding New Video Sources
```python
# src/downloader/new_source.py
class NewSourceDownloader:
    def download(self, url: str) -> dict:
        # Implement download logic
        return video_info
```

### Adding New Processors
```python
# src/processor/new_processor.py
class NewProcessor:
    def process(self, video_path: str) -> result:
        # Implement processing logic
        return result
```

### Adding New Generators
```python
# src/generator/new_generator.py
class NewGenerator:
    def generate(self, input_data: dict) -> output:
        # Implement generation logic
        return output
```

## Testing Architecture

```
tests/
  └── test_basic.py
       ├── TestConfig → Config loading
       ├── TestLogger → Logging setup
       └── TestImports → Module imports

Future tests:
  ├── test_downloader.py → Video downloading
  ├── test_processor.py → Scene detection, editing
  ├── test_generator.py → Content/subtitle generation
  └── test_integration.py → End-to-end flows
```

## Deployment Architecture

```
Development
    ↓
├─ Local Testing
├─ Code Review
├─ Security Scan
└─ Documentation
    ↓
Production Ready
    ↓
├─ pip install requirements.txt
├─ Configure .env
└─ python cli.py setup
    ↓
Ready for Use
```

## Security Architecture

```
User Input
    ↓
[Validation Layer]
    ├─ URL validation
    ├─ File path validation
    └─ Parameter validation
    ↓
[Processing Layer]
    ├─ Safe file operations
    ├─ Temp file cleanup
    └─ No code execution
    ↓
[API Layer]
    ├─ API keys from .env
    ├─ No hardcoded secrets
    └─ Error handling
    ↓
Secure Output
```

---

This architecture enables:
- **Modularity**: Easy to extend and modify
- **Scalability**: Can process multiple videos
- **Maintainability**: Clear separation of concerns
- **Testability**: Each component can be tested independently
- **Security**: Multiple validation and safety layers
