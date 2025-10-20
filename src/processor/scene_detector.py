"""Scene detection for identifying interesting moments in videos."""

from typing import List, Tuple
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from src.utils.logger import logger
from src.utils.config import Config


class SceneDetector:
    """Detect scenes in a video to identify interesting moments."""
    
    def __init__(self, threshold: float = None, min_scene_len: float = None):
        """Initialize scene detector.
        
        Args:
            threshold: Scene detection threshold (default from config)
            min_scene_len: Minimum scene length in seconds (default from config)
        """
        self.threshold = threshold or Config.SCENE_THRESHOLD
        self.min_scene_len = min_scene_len or Config.MIN_SCENE_LENGTH
    
    def detect_scenes(self, video_path: str) -> List[Tuple[float, float]]:
        """Detect scenes in a video.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of tuples (start_time, end_time) in seconds
        """
        logger.info(f"Detecting scenes in video: {video_path}")
        
        try:
            # Create video manager and scene manager
            video_manager = VideoManager([video_path])
            scene_manager = SceneManager()
            
            # Add content detector
            scene_manager.add_detector(
                ContentDetector(threshold=self.threshold, min_scene_len=int(self.min_scene_len))
            )
            
            # Start video manager
            video_manager.set_downscale_factor()
            video_manager.start()
            
            # Detect scenes
            scene_manager.detect_scenes(frame_source=video_manager)
            
            # Get scene list
            scene_list = scene_manager.get_scene_list()
            
            # Convert to list of tuples (start, end) in seconds
            scenes = []
            for scene in scene_list:
                start_time = scene[0].get_seconds()
                end_time = scene[1].get_seconds()
                scenes.append((start_time, end_time))
            
            logger.info(f"Detected {len(scenes)} scenes")
            
            return scenes
            
        except Exception as e:
            logger.error(f"Error detecting scenes: {str(e)}")
            raise
    
    def get_best_moments(
        self, 
        scenes: List[Tuple[float, float]], 
        min_duration: int = None,
        max_duration: int = None,
        num_clips: int = 3
    ) -> List[Tuple[float, float]]:
        """Select the best moments from detected scenes.
        
        Args:
            scenes: List of detected scenes
            min_duration: Minimum clip duration in seconds
            max_duration: Maximum clip duration in seconds
            num_clips: Number of clips to select
            
        Returns:
            List of best moment tuples (start_time, end_time)
        """
        min_duration = min_duration or Config.MIN_CLIP_DURATION
        max_duration = max_duration or Config.MAX_CLIP_DURATION
        
        # Filter scenes by duration
        valid_scenes = []
        for start, end in scenes:
            duration = end - start
            if min_duration <= duration <= max_duration:
                valid_scenes.append((start, end))
        
        # If no valid scenes, try to combine adjacent scenes
        if not valid_scenes and scenes:
            logger.info("No scenes match duration criteria, combining adjacent scenes")
            combined_scenes = self._combine_scenes(scenes, min_duration, max_duration)
            valid_scenes = combined_scenes
        
        # Sort by scene length (longer scenes are usually more interesting)
        valid_scenes.sort(key=lambda x: x[1] - x[0], reverse=True)
        
        # Return top N scenes
        best_moments = valid_scenes[:num_clips]
        
        logger.info(f"Selected {len(best_moments)} best moments")
        
        return best_moments
    
    def _combine_scenes(
        self, 
        scenes: List[Tuple[float, float]], 
        min_duration: int, 
        max_duration: int
    ) -> List[Tuple[float, float]]:
        """Combine adjacent scenes to meet duration requirements.
        
        Args:
            scenes: List of scenes to combine
            min_duration: Minimum desired duration
            max_duration: Maximum desired duration
            
        Returns:
            List of combined scenes
        """
        combined = []
        
        i = 0
        while i < len(scenes):
            start = scenes[i][0]
            end = scenes[i][1]
            
            # Try to combine with next scenes
            j = i + 1
            while j < len(scenes) and (end - start) < min_duration:
                # Check if gap between scenes is small (< 2 seconds)
                if scenes[j][0] - end < 2.0:
                    end = scenes[j][1]
                    j += 1
                else:
                    break
            
            duration = end - start
            if min_duration <= duration <= max_duration:
                combined.append((start, end))
            
            i = j if j > i + 1 else i + 1
        
        return combined
