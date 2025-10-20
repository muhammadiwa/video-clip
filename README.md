# 🎬 Viral Clip AI Generator

Transform long videos (YouTube/Upload) into **viral clips ready for YouTube Shorts** with AI-powered content generation!

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- 🎯 **Intelligent Scene Detection**: Automatically identifies the most interesting moments from long videos
- ⏱️ **Flexible Duration**: Generate clips from 30 seconds to 6 minutes (optimized for YouTube Shorts)
- 📱 **YouTube Shorts Format**: Auto-converts to 9:16 aspect ratio (1080x1920)
- 🤖 **AI-Powered Content**: Generates viral titles, descriptions, tags, and hashtags
- 📝 **Automatic Subtitles**: Speech-to-text transcription using Whisper AI
- 🖼️ **Thumbnail Generation**: Extracts high-quality thumbnails from clips
- 🔗 **YouTube Download**: Direct download from YouTube URLs
- 📂 **Local Video Support**: Process videos from your local storage

## 🚀 Quick Start

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/muhammadiwa/video-clip.git
cd video-clip
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Setup environment variables** (optional, for AI content generation)
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run setup**
```bash
python cli.py setup
```

### Basic Usage

#### Process a YouTube Video
```bash
python cli.py youtube "https://www.youtube.com/watch?v=VIDEO_ID" --clips 3
```

#### Process a Local Video
```bash
python cli.py local /path/to/video.mp4 --clips 5 --duration 60
```

## 📖 Detailed Usage

### YouTube Video Processing

Generate 3 viral clips from a YouTube video:
```bash
python cli.py youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --clips 3
```

Generate 5 clips with specific duration (60 seconds each):
```bash
python cli.py youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --clips 5 --duration 60
```

Disable subtitle generation:
```bash
python cli.py youtube "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --no-subtitles
```

### Local Video Processing

Generate clips from local video:
```bash
python cli.py local video.mp4 --clips 3
```

With custom duration:
```bash
python cli.py local video.mp4 --clips 5 --duration 45
```

## 📋 Command Reference

### `youtube` command
Process a YouTube video and generate viral clips.

**Options:**
- `--clips, -c`: Number of clips to generate (default: 3)
- `--duration, -d`: Target duration in seconds (30-360, default: auto)
- `--no-subtitles`: Disable subtitle generation
- `--no-content`: Disable viral content generation

### `local` command
Process a local video file and generate viral clips.

**Options:**
- Same as `youtube` command

### `setup` command
Setup the application (create directories, check dependencies).

## 🔧 Configuration

Edit `.env` file to customize settings:

```env
# OpenAI API Key (for AI content generation)
OPENAI_API_KEY=your_api_key_here

# Output directories
OUTPUT_DIR=output
CLIP_DIR=output/clips
THUMBNAIL_DIR=output/thumbnails
METADATA_DIR=output/metadata

# Clip duration settings
MIN_CLIP_DURATION=30
MAX_CLIP_DURATION=360
DEFAULT_CLIP_DURATION=60
TARGET_RESOLUTION=1080x1920

# Scene detection settings
SCENE_THRESHOLD=27.0
MIN_SCENE_LENGTH=3.0
```

## 📁 Output Structure

Generated files are organized as follows:

```
output/
├── clips/              # Generated video clips (.mp4)
│   ├── clip_20240120_001.mp4
│   ├── clip_20240120_001.srt (subtitles)
│   └── ...
├── thumbnails/         # Extracted thumbnails (.jpg)
│   ├── clip_20240120_001_thumb.jpg
│   └── ...
└── metadata/          # Clip metadata (.json)
    ├── clip_20240120_001_metadata.json
    └── ...
```

### Metadata Format

Each clip has a JSON metadata file containing:

```json
{
  "clip_number": 1,
  "original_video": "Original Video Title",
  "start_time": 120.5,
  "end_time": 180.5,
  "duration": 60.0,
  "clip_path": "output/clips/clip_20240120_001.mp4",
  "thumbnail_path": "output/thumbnails/clip_20240120_001_thumb.jpg",
  "subtitle_path": "output/clips/clip_20240120_001.srt",
  "transcript": "Full transcript text...",
  "viral_content": {
    "title": "🔥 Amazing Moment - You Won't Believe This! #Shorts",
    "description": "This incredible moment will blow your mind! 🤯\n\nWatch till the end! 👀\n\n#shorts #viral #trending",
    "tags": ["shorts", "viral", "trending", "amazing"],
    "hashtags": ["#shorts", "#viral", "#trending", "#fyp"]
  },
  "created_at": "20240120_153045"
}
```

## 🎯 How It Works

1. **Video Acquisition**: Downloads video from YouTube or loads from local file
2. **Scene Detection**: Uses AI to detect scene changes and identify interesting moments
3. **Clip Extraction**: Extracts the best moments based on duration and content
4. **Format Conversion**: Converts to YouTube Shorts format (9:16 aspect ratio)
5. **Thumbnail Generation**: Extracts high-quality thumbnail from middle of clip
6. **Subtitle Generation**: Uses Whisper AI to transcribe audio and generate SRT subtitles
7. **Content Generation**: Uses OpenAI GPT to create viral titles, descriptions, and tags
8. **Output**: Saves clips, thumbnails, subtitles, and metadata

## 🧠 AI-Powered Features

### Scene Detection
Uses computer vision to detect scene changes and identify the most dynamic moments in your video.

### Content Generation
When OpenAI API key is provided, generates:
- **Viral Titles**: Catchy, emotion-driven titles optimized for CTR
- **Engaging Descriptions**: Compelling descriptions with hooks and keywords
- **Smart Tags**: Relevant tags for YouTube algorithm
- **Trending Hashtags**: Popular hashtags including #shorts and #viral

### Automatic Subtitles
Uses OpenAI's Whisper model for accurate speech-to-text transcription in multiple languages.

## 📦 Dependencies

- **yt-dlp**: YouTube video downloading
- **moviepy**: Video editing and processing
- **opencv-python**: Scene detection and video analysis
- **whisper**: Speech recognition for subtitles
- **openai**: AI content generation
- **scenedetect**: Scene change detection
- **click**: CLI interface

## 🔍 System Requirements

- Python 3.8 or higher
- FFmpeg (automatically installed with moviepy)
- 4GB+ RAM (8GB+ recommended for longer videos)
- GPU recommended for faster subtitle generation (optional)

## 🐛 Troubleshooting

### FFmpeg not found
Install FFmpeg:
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### Out of memory errors
- Process shorter videos
- Reduce number of clips
- Use smaller Whisper model (`tiny` instead of `base`)

### OpenAI API errors
- Check API key is valid
- Ensure you have credits in your OpenAI account
- Fallback content generation will be used if API fails

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

**Muhammad Iwa**

## 🙏 Acknowledgments

- OpenAI Whisper for speech recognition
- yt-dlp for YouTube downloading
- MoviePy for video processing
- PySceneDetect for scene detection

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Made with ❤️ for content creators**