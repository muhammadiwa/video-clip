# 🚀 Quick Start Guide

Get started with Viral Clip AI Generator in 5 minutes!

## Installation

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/muhammadiwa/video-clip.git
cd video-clip

# Install dependencies
pip install -r requirements.txt

# Setup environment
python cli.py setup
```

### 2. Configure (Optional)

For AI-powered content generation, add your OpenAI API key:

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API key
# OPENAI_API_KEY=sk-your-key-here
```

## Basic Usage

### Process a YouTube Video

```bash
# Generate 3 viral clips from a YouTube video
python cli.py youtube "https://www.youtube.com/watch?v=VIDEO_ID" --clips 3

# With specific duration (60 seconds)
python cli.py youtube "https://www.youtube.com/watch?v=VIDEO_ID" --clips 5 --duration 60
```

### Process a Local Video

```bash
# Generate clips from a local video file
python cli.py local /path/to/your/video.mp4 --clips 3

# Skip subtitle generation for faster processing
python cli.py local video.mp4 --clips 3 --no-subtitles
```

## What You Get

After processing, you'll find these files in the `output/` directory:

```
output/
├── clips/
│   ├── clip_20240120_001.mp4      # Your viral clip
│   ├── clip_20240120_001.srt      # Subtitles (if enabled)
│   └── ...
├── thumbnails/
│   ├── clip_20240120_001_thumb.jpg  # Thumbnail image
│   └── ...
└── metadata/
    ├── clip_20240120_001_metadata.json  # All metadata
    └── ...
```

## Understanding the Output

Each clip comes with a metadata JSON file containing:

- **Viral Title**: Optimized for clicks and engagement
- **Viral Description**: Engaging description with keywords
- **Tags**: Relevant tags for YouTube algorithm
- **Hashtags**: Trending hashtags including #shorts
- **Transcript**: Full text transcription (if subtitles enabled)
- **Timestamps**: Original start/end times in source video

## Tips for Best Results

### 1. Video Length
- **Recommended**: 10-60 minute videos work best
- Videos should have clear speech and distinct scenes
- Higher quality source = better output quality

### 2. Number of Clips
- **3-5 clips**: Best for most videos
- **1-2 clips**: For shorter source videos (5-15 min)
- **5-10 clips**: For very long videos (60+ min)

### 3. Duration Settings
- **Auto (default)**: Let AI choose optimal duration
- **30-45s**: Quick, punchy content
- **60-90s**: Standard shorts format
- **90-180s**: For detailed content
- **180-360s**: For educational/tutorial content

### 4. Performance
- **With GPU**: Subtitle generation is much faster
- **Without GPU**: Use `--no-subtitles` for faster processing
- **Large videos**: Process in batches with fewer clips

## Common Workflows

### Quick Preview (Fast)
```bash
# Generate 2 clips without subtitles for quick preview
python cli.py youtube "URL" --clips 2 --no-subtitles
```

### Production Ready (Full Features)
```bash
# Generate 5 clips with all features
python cli.py youtube "URL" --clips 5 --duration 60
```

### Batch Processing
```bash
# Process multiple videos
for video in videos/*.mp4; do
    python cli.py local "$video" --clips 3
done
```

## Troubleshooting

### "OpenAI API key not found"
- This is just a warning. The app will use fallback content generation.
- To use AI features, add your API key to `.env` file.

### "FFmpeg not found"
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Out of Memory
- Reduce number of clips: `--clips 2`
- Process shorter videos
- Close other applications

### Slow Processing
- Use `--no-subtitles` to skip subtitle generation
- Reduce number of clips
- Use GPU if available

## Next Steps

1. **Check Output**: Review generated clips in `output/clips/`
2. **Customize**: Edit titles and descriptions in metadata files
3. **Upload**: Upload clips to YouTube Shorts
4. **Optimize**: Adjust parameters based on results

## Need Help?

- 📖 Read the full [README.md](README.md)
- 🐛 Report issues on GitHub
- 💡 Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

---

**Happy Creating! 🎬**
