#!/usr/bin/env python3
"""Command-line interface for Viral Clip AI Generator."""

import click
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.main import ViralClipGenerator
from src.utils.logger import logger
from src.utils.config import Config


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🎬 Viral Clip AI Generator
    
    Transform long videos into viral YouTube Shorts clips with AI-powered
    titles, descriptions, thumbnails, and automatic subtitles.
    """
    pass


@cli.command()
@click.argument('url')
@click.option(
    '--clips', '-c',
    default=3,
    help='Number of clips to generate (default: 3)'
)
@click.option(
    '--duration', '-d',
    type=int,
    default=None,
    help='Target duration in seconds (30-360, default: auto)'
)
@click.option(
    '--no-subtitles',
    is_flag=True,
    help='Disable subtitle generation'
)
@click.option(
    '--no-content',
    is_flag=True,
    help='Disable viral content generation'
)
def youtube(url, clips, duration, no_subtitles, no_content):
    """Process a YouTube video and generate viral clips.
    
    Example:
        cli.py youtube "https://www.youtube.com/watch?v=VIDEO_ID" --clips 5
    """
    try:
        logger.info(f"🎬 Starting Viral Clip Generator")
        logger.info(f"YouTube URL: {url}")
        logger.info(f"Number of clips: {clips}")
        
        if duration:
            if duration < Config.MIN_CLIP_DURATION or duration > Config.MAX_CLIP_DURATION:
                logger.error(f"Duration must be between {Config.MIN_CLIP_DURATION} and {Config.MAX_CLIP_DURATION} seconds")
                return
        
        generator = ViralClipGenerator()
        
        results = generator.process_youtube_video(
            url=url,
            num_clips=clips,
            clip_duration=duration,
            generate_subtitles=not no_subtitles,
            generate_content=not no_content
        )
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("✅ CLIPS GENERATED SUCCESSFULLY!")
        logger.info("="*60)
        
        for result in results:
            logger.info(f"\n📹 Clip {result['clip_number']}:")
            logger.info(f"   Duration: {result['duration']:.1f}s")
            logger.info(f"   Video: {result['clip_path']}")
            logger.info(f"   Thumbnail: {result['thumbnail_path']}")
            
            if result.get('subtitle_path'):
                logger.info(f"   Subtitles: {result['subtitle_path']}")
            
            if result.get('viral_content'):
                content = result['viral_content']
                logger.info(f"\n   🔥 Viral Content:")
                logger.info(f"   Title: {content.get('title', 'N/A')}")
                logger.info(f"   Description: {content.get('description', 'N/A')[:100]}...")
                logger.info(f"   Tags: {', '.join(content.get('tags', [])[:5])}")
            
            logger.info(f"   Metadata: {result['metadata_path']}")
        
        logger.info("\n" + "="*60)
        logger.info(f"📁 All files saved to: {Config.OUTPUT_DIR}")
        logger.info("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise


@cli.command()
@click.argument('video_path', type=click.Path(exists=True))
@click.option(
    '--clips', '-c',
    default=3,
    help='Number of clips to generate (default: 3)'
)
@click.option(
    '--duration', '-d',
    type=int,
    default=None,
    help='Target duration in seconds (30-360, default: auto)'
)
@click.option(
    '--no-subtitles',
    is_flag=True,
    help='Disable subtitle generation'
)
@click.option(
    '--no-content',
    is_flag=True,
    help='Disable viral content generation'
)
def local(video_path, clips, duration, no_subtitles, no_content):
    """Process a local video file and generate viral clips.
    
    Example:
        cli.py local /path/to/video.mp4 --clips 3 --duration 60
    """
    try:
        logger.info(f"🎬 Starting Viral Clip Generator")
        logger.info(f"Video file: {video_path}")
        logger.info(f"Number of clips: {clips}")
        
        if duration:
            if duration < Config.MIN_CLIP_DURATION or duration > Config.MAX_CLIP_DURATION:
                logger.error(f"Duration must be between {Config.MIN_CLIP_DURATION} and {Config.MAX_CLIP_DURATION} seconds")
                return
        
        generator = ViralClipGenerator()
        
        results = generator.process_local_video(
            video_path=video_path,
            num_clips=clips,
            clip_duration=duration,
            generate_subtitles=not no_subtitles,
            generate_content=not no_content
        )
        
        # Display results
        logger.info("\n" + "="*60)
        logger.info("✅ CLIPS GENERATED SUCCESSFULLY!")
        logger.info("="*60)
        
        for result in results:
            logger.info(f"\n📹 Clip {result['clip_number']}:")
            logger.info(f"   Duration: {result['duration']:.1f}s")
            logger.info(f"   Video: {result['clip_path']}")
            logger.info(f"   Thumbnail: {result['thumbnail_path']}")
            
            if result.get('subtitle_path'):
                logger.info(f"   Subtitles: {result['subtitle_path']}")
            
            if result.get('viral_content'):
                content = result['viral_content']
                logger.info(f"\n   🔥 Viral Content:")
                logger.info(f"   Title: {content.get('title', 'N/A')}")
                logger.info(f"   Description: {content.get('description', 'N/A')[:100]}...")
                logger.info(f"   Tags: {', '.join(content.get('tags', [])[:5])}")
            
            logger.info(f"   Metadata: {result['metadata_path']}")
        
        logger.info("\n" + "="*60)
        logger.info(f"📁 All files saved to: {Config.OUTPUT_DIR}")
        logger.info("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error processing video: {str(e)}")
        raise


@cli.command()
def setup():
    """Setup the application (create directories, check dependencies)."""
    try:
        logger.info("Setting up Viral Clip AI Generator...")
        
        # Create directories
        Config.ensure_directories()
        logger.info(f"✅ Created output directories in: {Config.OUTPUT_DIR}")
        
        # Check API key
        if Config.OPENAI_API_KEY:
            logger.info("✅ OpenAI API key found")
        else:
            logger.warning("⚠️  OpenAI API key not found")
            logger.warning("   Set OPENAI_API_KEY in .env file for AI-powered content generation")
            logger.warning("   Fallback content generation will be used")
        
        logger.info("\n✅ Setup complete!")
        logger.info("\nNext steps:")
        logger.info("  1. (Optional) Set OPENAI_API_KEY in .env file")
        logger.info("  2. Run: python cli.py youtube <URL> or python cli.py local <PATH>")
        
    except Exception as e:
        logger.error(f"Error during setup: {str(e)}")
        raise


if __name__ == '__main__':
    cli()
