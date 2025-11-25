from scenedetect import detect, ContentDetector, AdaptiveDetector
from scenedetect.video_splitter import split_video_ffmpeg
from typing import List, Dict, Tuple
from pathlib import Path

class SceneDetector:
    """Video scene detection using PySceneDetect"""
    
    @staticmethod
    def detect_scenes(
        video_path: str,
        threshold: float = 27.0,
        min_scene_len: float = 1.0
    ) -> List[Dict]:
        """
        Detect scene changes in video
        Returns: list of scenes with start/end timestamps
        """
        try:
            # Detect scenes
            scene_list = detect(
                video_path,
                ContentDetector(threshold=threshold, min_scene_len=min_scene_len)
            )
            
            scenes = []
            for i, scene in enumerate(scene_list):
                start_time = scene[0].get_seconds()
                end_time = scene[1].get_seconds()
                duration = end_time - start_time
                
                scenes.append({
                    'scene_number': i + 1,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration,
                    'start_frame': scene[0].get_frames(),
                    'end_frame': scene[1].get_frames(),
                })
            
            return scenes
            
        except Exception as e:
            raise Exception(f"Failed to detect scenes: {str(e)}")
    
    @staticmethod
    def detect_scenes_adaptive(
        video_path: str,
        adaptive_threshold: float = 3.0,
        min_scene_len: float = 1.0
    ) -> List[Dict]:
        """
        Detect scenes using adaptive algorithm (better for gradual transitions)
        Returns: list of scenes with start/end timestamps
        """
        try:
            # Detect scenes with adaptive detector
            scene_list = detect(
                video_path,
                AdaptiveDetector(
                    adaptive_threshold=adaptive_threshold,
                    min_scene_len=min_scene_len
                )
            )
            
            scenes = []
            for i, scene in enumerate(scene_list):
                start_time = scene[0].get_seconds()
                end_time = scene[1].get_seconds()
                duration = end_time - start_time
                
                scenes.append({
                    'scene_number': i + 1,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': duration,
                    'start_frame': scene[0].get_frames(),
                    'end_frame': scene[1].get_frames(),
                })
            
            return scenes
            
        except Exception as e:
            raise Exception(f"Failed to detect scenes (adaptive): {str(e)}")
    
    @staticmethod
    def split_video_by_scenes(
        video_path: str,
        output_dir: str,
        scenes: List[Dict]
    ) -> List[str]:
        """
        Split video into separate files based on scene timestamps
        Returns: list of output file paths
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Note: This is a placeholder for actual split implementation
            # You might want to use FFmpeg for actual splitting
            output_files = []
            
            return output_files
            
        except Exception as e:
            raise Exception(f"Failed to split video by scenes: {str(e)}")
    
    @staticmethod
    def analyze_scene_complexity(scenes: List[Dict]) -> List[Dict]:
        """
        Analyze scene complexity and add scores
        Returns: scenes with complexity scores
        """
        try:
            analyzed_scenes = []
            
            for scene in scenes:
                # Simple heuristic: shorter scenes often have more action
                duration = scene['duration']
                
                if duration < 2.0:
                    complexity_score = 0.9
                    action_level = "high"
                elif duration < 5.0:
                    complexity_score = 0.6
                    action_level = "medium"
                else:
                    complexity_score = 0.3
                    action_level = "low"
                
                scene_copy = scene.copy()
                scene_copy['complexity_score'] = complexity_score
                scene_copy['action_level'] = action_level
                analyzed_scenes.append(scene_copy)
            
            return analyzed_scenes
            
        except Exception as e:
            raise Exception(f"Failed to analyze scene complexity: {str(e)}")
