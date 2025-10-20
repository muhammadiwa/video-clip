#!/usr/bin/env python3
"""Example usage of Viral Clip AI Generator as a Python library."""

from src.main import ViralClipGenerator
from src.utils.logger import logger


def example_youtube():
    """Example: Process a YouTube video."""
    logger.info("Example: Processing YouTube video")
    
    generator = ViralClipGenerator()
    
    # Process a YouTube video
    results = generator.process_youtube_video(
        url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Replace with actual URL
        num_clips=3,
        clip_duration=60,
        generate_subtitles=True,
        generate_content=True
    )
    
    # Print results
    for result in results:
        print(f"\nClip {result['clip_number']}:")
        print(f"  Duration: {result['duration']:.1f}s")
        print(f"  File: {result['clip_path']}")
        print(f"  Thumbnail: {result['thumbnail_path']}")
        
        if result.get('viral_content'):
            print(f"  Title: {result['viral_content']['title']}")


def example_local():
    """Example: Process a local video file."""
    logger.info("Example: Processing local video")
    
    generator = ViralClipGenerator()
    
    # Process a local video
    results = generator.process_local_video(
        video_path="/path/to/your/video.mp4",  # Replace with actual path
        num_clips=5,
        clip_duration=45,
        generate_subtitles=False,
        generate_content=True
    )
    
    # Print results
    for result in results:
        print(f"\nClip {result['clip_number']}:")
        print(f"  Duration: {result['duration']:.1f}s")
        print(f"  File: {result['clip_path']}")


def example_custom_processing():
    """Example: Custom processing with individual components."""
    from src.downloader.youtube import YouTubeDownloader
    from src.processor.scene_detector import SceneDetector
    from src.processor.video_editor import VideoEditor
    from src.generator.content_generator import ContentGenerator
    
    # Download video
    downloader = YouTubeDownloader()
    video_info = downloader.download("https://www.youtube.com/watch?v=VIDEO_ID")
    
    # Detect scenes
    detector = SceneDetector()
    scenes = detector.detect_scenes(video_info['path'])
    best_moments = detector.get_best_moments(scenes, num_clips=3)
    
    # Extract clips
    editor = VideoEditor()
    for i, (start, end) in enumerate(best_moments, 1):
        clip_path = f"output/clips/custom_clip_{i}.mp4"
        editor.extract_clip(video_info['path'], start, end, clip_path)
    
    # Generate content
    content_gen = ContentGenerator()
    content = content_gen.generate_viral_content(
        video_title=video_info['title'],
        duration=60
    )
    
    print(f"Generated title: {content['title']}")


if __name__ == "__main__":
    # Uncomment the example you want to run
    
    # example_youtube()
    # example_local()
    # example_custom_processing()
    
    print("Uncomment an example function to run it")
