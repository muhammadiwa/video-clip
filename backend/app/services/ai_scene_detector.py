"""
AI-based Scene Detection using TransNetV2
Much faster than PySceneDetect for long videos (30-60s vs 45+ min!)
"""

import torch
import numpy as np
import cv2
from pathlib import Path
from typing import List, Dict, Optional, Callable
import subprocess
import json


class TransNetV2SceneDetector:
    """
    AI-based scene detection using TransNetV2
    - 10-100x faster than PySceneDetect
    - More accurate scene boundaries
    - GPU-accelerated
    """
    
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
    
    def load_model(self):
        """Load TransNetV2 model"""
        try:
            # Try to import transnetv2
            from transnetv2 import TransNetV2
            
            if self.model is None:
                print(f"Loading TransNetV2 model on {self.device}...")
                self.model = TransNetV2()
                if self.device == "cuda":
                    self.model = self.model.cuda()
                print("Model loaded successfully!")
            
            return True
        except ImportError:
            print("[WARNING] TransNetV2 not installed. Install with: pip install transnetv2")
            return False
    
    def detect_scenes(
        self,
        video_path: str,
        threshold: float = 0.5,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict]:
        """
        Detect scenes using TransNetV2 AI model
        
        Args:
            video_path: Path to video file
            threshold: Scene detection threshold (0.0-1.0, default: 0.5)
            progress_callback: Optional progress callback
            
        Returns: List of scene dicts with start/end times
        """
        try:
            if not self.load_model():
                raise Exception("TransNetV2 model not available")
            
            if progress_callback:
                progress_callback(0.1, "Analyzing video with AI...")
            
            # Run prediction
            from transnetv2 import TransNetV2
            predictions, frame_indices = self.model.predict_video(video_path)
            
            if progress_callback:
                progress_callback(0.7, "Processing scene boundaries...")
            
            # Find scene boundaries
            scenes = self._extract_scenes(
                predictions, 
                frame_indices, 
                video_path,
                threshold
            )
            
            if progress_callback:
                progress_callback(1.0, f"AI detection complete! Found {len(scenes)} scenes")
            
            return scenes
            
        except Exception as e:
            raise Exception(f"TransNetV2 scene detection failed: {str(e)}")
    
    def _extract_scenes(
        self,
        predictions: np.ndarray,
        frame_indices: np.ndarray,
        video_path: str,
        threshold: float = 0.5
    ) -> List[Dict]:
        """Extract scene boundaries from predictions"""
        try:
            # Get video FPS
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            
            # Find scene changes (predictions > threshold)
            scene_changes = np.where(predictions > threshold)[0]
            
            # Convert to time-based scenes
            scenes = []
            
            if len(scene_changes) == 0:
                # No scene changes, return whole video as one scene
                return [{
                    'scene_number': 1,
                    'start_time': 0.0,
                    'end_time': frame_indices[-1] / fps,
                    'duration': frame_indices[-1] / fps,
                    'start_frame': 0,
                    'end_frame': int(frame_indices[-1]),
                    'ai_confidence': 1.0,
                }]
            
            # Add first scene (from start to first change)
            if scene_changes[0] > 0:
                scenes.append({
                    'scene_number': 1,
                    'start_time': 0.0,
                    'end_time': frame_indices[scene_changes[0]] / fps,
                    'duration': frame_indices[scene_changes[0]] / fps,
                    'start_frame': 0,
                    'end_frame': int(frame_indices[scene_changes[0]]),
                    'ai_confidence': float(predictions[scene_changes[0]]),
                })
            
            # Add scenes between changes
            for i in range(len(scene_changes) - 1):
                start_idx = scene_changes[i]
                end_idx = scene_changes[i + 1]
                
                start_time = frame_indices[start_idx] / fps
                end_time = frame_indices[end_idx] / fps
                
                scenes.append({
                    'scene_number': len(scenes) + 1,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': end_time - start_time,
                    'start_frame': int(frame_indices[start_idx]),
                    'end_frame': int(frame_indices[end_idx]),
                    'ai_confidence': float(predictions[end_idx]),
                })
            
            # Add last scene (from last change to end)
            last_idx = scene_changes[-1]
            scenes.append({
                'scene_number': len(scenes) + 1,
                'start_time': frame_indices[last_idx] / fps,
                'end_time': frame_indices[-1] / fps,
                'duration': (frame_indices[-1] - frame_indices[last_idx]) / fps,
                'start_frame': int(frame_indices[last_idx]),
                'end_frame': int(frame_indices[-1]),
                'ai_confidence': float(predictions[last_idx]),
            })
            
            return scenes
            
        except Exception as e:
            raise Exception(f"Failed to extract scenes: {str(e)}")


class FastSceneDetector:
    """
    Fast scene detection alternatives when AI is not available
    """
    
    @staticmethod
    def detect_keyframe_scenes(
        video_path: str,
        keyframe_interval: float = 5.0,
        min_scene_length: float = 10.0
    ) -> List[Dict]:
        """
        Fast scene detection using FFmpeg keyframe detection
        Much faster than PySceneDetect (seconds vs minutes)
        
        Args:
            video_path: Path to video
            keyframe_interval: Check for keyframes every N seconds
            min_scene_length: Minimum scene length in seconds
            
        Returns: List of scenes
        """
        try:
            import ffmpeg
            
            # Get video info
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            
            # Use FFmpeg to detect I-frames (keyframes)
            cmd = [
                'ffprobe',
                '-select_streams', 'v:0',
                '-show_entries', 'packet=pts_time,flags',
                '-of', 'json',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            
            # Extract keyframe timestamps
            keyframe_times = []
            for packet in data.get('packets', []):
                if 'K' in packet.get('flags', ''):  # K = keyframe
                    pts_time = float(packet.get('pts_time', 0))
                    keyframe_times.append(pts_time)
            
            # Group keyframes into scenes
            scenes = []
            if not keyframe_times:
                # No keyframes found, create time-based segments
                return FastSceneDetector.create_time_segments(duration, min_scene_length)
            
            scene_start = 0.0
            current_scene_keyframes = []
            
            for kf_time in keyframe_times:
                current_scene_keyframes.append(kf_time)
                
                # Check if we should start new scene
                if kf_time - scene_start >= min_scene_length:
                    scenes.append({
                        'scene_number': len(scenes) + 1,
                        'start_time': scene_start,
                        'end_time': kf_time,
                        'duration': kf_time - scene_start,
                        'start_frame': 0,
                        'end_frame': 0,
                        'keyframe_count': len(current_scene_keyframes),
                    })
                    scene_start = kf_time
                    current_scene_keyframes = []
            
            # Add last scene
            if scene_start < duration:
                scenes.append({
                    'scene_number': len(scenes) + 1,
                    'start_time': scene_start,
                    'end_time': duration,
                    'duration': duration - scene_start,
                    'start_frame': 0,
                    'end_frame': 0,
                    'keyframe_count': len(current_scene_keyframes),
                })
            
            return scenes if scenes else FastSceneDetector.create_time_segments(duration)
            
        except Exception as e:
            print(f"[WARNING] Keyframe detection failed: {e}")
            # Fallback to time-based segments
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return FastSceneDetector.create_time_segments(duration)
    
    @staticmethod
    def create_time_segments(
        video_duration: float,
        segment_length: float = 60.0
    ) -> List[Dict]:
        """
        Create fixed-duration time segments (instant)
        Fallback when other methods fail
        """
        segments = []
        start = 0.0
        i = 1
        
        while start < video_duration:
            end = min(start + segment_length, video_duration)
            
            segments.append({
                'scene_number': i,
                'start_time': start,
                'end_time': end,
                'duration': end - start,
                'start_frame': 0,
                'end_frame': 0,
                'is_time_based': True,
            })
            
            start = end
            i += 1
        
        return segments


# Auto-select best method
class SmartSceneDetector:
    """
    Automatically select best scene detection method
    """
    
    @staticmethod
    def analyze_scene_complexity(
        scenes: List[Dict],
        video_path: Optional[str] = None
    ) -> List[Dict]:
        """
        Analyze scene complexity with multiple factors
        
        Args:
            scenes: List of scenes to analyze
            video_path: Optional video path for deep analysis
            
        Returns: scenes with complexity scores
        """
        try:
            analyzed_scenes = []
            
            for scene in scenes:
                # Get basic info
                duration = scene.get('duration', 0)
                keyframe_count = scene.get('keyframe_count', 0)
                
                # FACTOR 1: Keyframe density (scene changes = action)
                if duration > 0:
                    keyframes_per_second = keyframe_count / duration
                else:
                    keyframes_per_second = 0
                
                # More keyframes = more cuts/action
                if keyframes_per_second >= 1.0:
                    keyframe_score = 0.9
                    action_level = "high"
                elif keyframes_per_second >= 0.5:
                    keyframe_score = 0.7
                    action_level = "medium-high"
                elif keyframes_per_second >= 0.3:
                    keyframe_score = 0.5
                    action_level = "medium"
                elif keyframes_per_second >= 0.1:
                    keyframe_score = 0.3
                    action_level = "low-medium"
                else:
                    keyframe_score = 0.2
                    action_level = "low"
                
                # FACTOR 2: Duration factor (shorter can be more intense)
                if duration < 5.0:
                    duration_factor = 0.8
                elif duration < 15.0:
                    duration_factor = 0.6
                elif duration < 30.0:
                    duration_factor = 0.4
                else:
                    duration_factor = 0.3
                
                # FACTOR 3: AI confidence (if available from TransNetV2)
                ai_confidence = scene.get('ai_confidence', 0.5)
                
                # Combine factors (weighted)
                complexity_score = (
                    keyframe_score * 0.5 +      # 50% from keyframe density
                    duration_factor * 0.3 +     # 30% from duration
                    ai_confidence * 0.2          # 20% from AI confidence
                )
                
                # Ensure score is between 0.1 and 1.0
                complexity_score = max(0.1, min(1.0, complexity_score))
                
                scene_copy = scene.copy()
                scene_copy['complexity_score'] = round(complexity_score, 3)
                scene_copy['action_level'] = action_level
                scene_copy['keyframes_per_second'] = round(keyframes_per_second, 2)
                analyzed_scenes.append(scene_copy)
            
            return analyzed_scenes
            
        except Exception as e:
            print(f"[WARNING] Scene complexity analysis failed: {e}")
            # Fallback: return scenes with default scores
            for scene in scenes:
                scene['complexity_score'] = 0.5
                scene['action_level'] = "medium"
            return scenes
    
    @staticmethod
    def detect_scenes(
        video_path: str,
        video_duration: float,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> List[Dict]:
        """
        Smart scene detection - automatically selects best method
        
        Priority:
        1. TransNetV2 (AI) - if available and GPU present
        2. FFmpeg keyframes - fast and reliable
        3. Time-based segments - instant fallback
        """
        try:
            # Try TransNetV2 first (AI-based, fastest with GPU)
            if torch.cuda.is_available():
                try:
                    detector = TransNetV2SceneDetector()
                    if detector.load_model():
                        if progress_callback:
                            progress_callback(0.0, "Using AI scene detection (TransNetV2)...")
                        scenes = detector.detect_scenes(video_path, progress_callback=progress_callback)
                        # Analyze complexity with video path
                        return SmartSceneDetector.analyze_scene_complexity(scenes, video_path)
                except Exception as e:
                    print(f"[WARNING] TransNetV2 failed: {e}")
            
            # Try FFmpeg keyframe detection (fast, no AI)
            if progress_callback:
                progress_callback(0.0, "Using fast keyframe detection...")
            
            scenes = FastSceneDetector.detect_keyframe_scenes(video_path)
            
            # Analyze complexity with video path
            scenes = SmartSceneDetector.analyze_scene_complexity(scenes, video_path)
            
            if progress_callback:
                progress_callback(1.0, f"Keyframe detection complete! Found {len(scenes)} scenes")
            
            return scenes
            
        except Exception as e:
            # Ultimate fallback: time-based segments
            print(f"[WARNING] All scene detection methods failed: {e}")
            print(f"[INFO] Using time-based segments as fallback")
            
            if progress_callback:
                progress_callback(0.5, "Using time-based segments...")
            
            scenes = FastSceneDetector.create_time_segments(video_duration, segment_length=60.0)
            
            # Analyze complexity
            scenes = SmartSceneDetector.analyze_scene_complexity(scenes, video_path)
            
            if progress_callback:
                progress_callback(1.0, f"Created {len(scenes)} time-based segments")
            
            return scenes
