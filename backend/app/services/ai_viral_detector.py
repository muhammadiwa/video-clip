"""
AI-based Viral Moment Detection using OpenAI GPT-4 Vision
Analyzes video frames and transcription to detect viral-worthy moments
"""

import base64
import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import json
from openai import OpenAI
from app.core.config import settings


class OpenAIViralDetector:
    """
    AI-powered viral moment detection using GPT-4 Vision
    Analyzes visual content + transcription for viral potential
    """
    
    def __init__(self):
        # Initialize OpenAI client with only api_key (no proxies for v1.0+)
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not configured")
        
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o"  # Use gpt-4o for better vision support
    
    def analyze_frame(
        self,
        frame_path: str,
        transcription_text: Optional[str] = None
    ) -> Dict:
        """
        Analyze a single frame for viral potential using GPT-4 Vision
        
        Args:
            frame_path: Path to frame image
            transcription_text: Optional text transcript for this moment
            
        Returns: Analysis dict with viral_score and reasoning
        """
        try:
            # Encode frame to base64
            with open(frame_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create prompt
            prompt = self._create_viral_analysis_prompt(transcription_text)
            
            # Call GPT-4 Vision
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            # Parse response
            analysis_text = response.choices[0].message.content
            analysis = self._parse_analysis(analysis_text)
            
            return analysis
            
        except Exception as e:
            print(f"[ERROR] Frame analysis failed: {e}")
            return {
                'viral_score': 0.5,
                'reasoning': f"Analysis failed: {str(e)}",
                'categories': [],
                'hook_potential': 0.5,
                'engagement_factors': []
            }
    
    def analyze_scene(
        self,
        video_path: str,
        scene: Dict,
        transcription_segments: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Analyze entire scene for viral potential
        Extracts multiple frames and analyzes them
        
        Args:
            video_path: Path to video file
            scene: Scene dict with start_time, end_time
            transcription_segments: Optional transcription segments in this scene
            
        Returns: Enhanced scene dict with viral analysis
        """
        try:
            # Extract key frames from scene (beginning, middle, end)
            frames = self._extract_scene_frames(
                video_path,
                scene['start_time'],
                scene['end_time'],
                num_frames=3
            )
            
            # Get transcription text for this scene
            scene_text = ""
            if transcription_segments:
                scene_text = " ".join([
                    seg['text'] for seg in transcription_segments
                    if scene['start_time'] <= seg['start'] < scene['end_time']
                ])
            
            # Analyze each frame
            frame_analyses = []
            for frame_path in frames:
                analysis = self.analyze_frame(frame_path, scene_text)
                frame_analyses.append(analysis)
            
            # Aggregate analysis
            avg_score = np.mean([a['viral_score'] for a in frame_analyses])
            max_score = max([a['viral_score'] for a in frame_analyses])
            
            # Combine with rule-based factors
            duration_score = self._calculate_duration_score(scene['duration'])
            
            # Final viral score (weighted combination)
            final_score = (
                avg_score * 0.5 +  # Average AI score
                max_score * 0.3 +  # Peak moment score
                duration_score * 0.2  # Duration optimization
            )
            
            # Enhance scene with AI analysis
            scene_copy = scene.copy()
            scene_copy['viral_score'] = round(final_score, 3)
            scene_copy['ai_analysis'] = {
                'avg_score': round(avg_score, 3),
                'peak_score': round(max_score, 3),
                'frame_analyses': frame_analyses,
                'transcription': scene_text[:200] if scene_text else None,
            }
            scene_copy['is_viral_candidate'] = final_score >= 0.65
            
            return scene_copy
            
        except Exception as e:
            print(f"[ERROR] Scene analysis failed: {e}")
            # Return original scene with default score
            scene_copy = scene.copy()
            scene_copy['viral_score'] = 0.5
            scene_copy['ai_analysis'] = {'error': str(e)}
            return scene_copy
    
    def batch_analyze_scenes(
        self,
        video_path: str,
        scenes: List[Dict],
        transcription: Optional[Dict] = None,
        max_concurrent: int = 3
    ) -> List[Dict]:
        """
        Analyze multiple scenes in batch
        
        Args:
            video_path: Path to video
            scenes: List of scene dicts
            transcription: Full video transcription
            max_concurrent: Max concurrent API calls
            
        Returns: List of analyzed scenes with viral scores
        """
        try:
            transcription_segments = transcription.get('segments', []) if transcription else []
            
            analyzed_scenes = []
            
            # Analyze scenes (limit to avoid high costs)
            for i, scene in enumerate(scenes[:20]):  # Limit to first 20 scenes
                print(f"[AI] Analyzing scene {i+1}/{min(len(scenes), 20)}...")
                
                analyzed_scene = self.analyze_scene(
                    video_path,
                    scene,
                    transcription_segments
                )
                analyzed_scenes.append(analyzed_scene)
            
            # Sort by viral score
            analyzed_scenes.sort(key=lambda x: x['viral_score'], reverse=True)
            
            return analyzed_scenes
            
        except Exception as e:
            print(f"[ERROR] Batch analysis failed: {e}")
            # Return scenes with default scores
            for scene in scenes:
                scene['viral_score'] = 0.5
            return scenes
    
    def _create_viral_analysis_prompt(self, transcription_text: Optional[str] = None) -> str:
        """Create prompt for GPT-4 Vision"""
        prompt = """Analyze this video frame for viral potential on social media (TikTok, YouTube Shorts, Instagram Reels).

Rate the viral potential from 0.0 to 1.0 based on:
1. Visual Impact: Eye-catching, colorful, dynamic, unexpected
2. Emotional Appeal: Exciting, funny, surprising, inspiring, relatable
3. Hook Potential: Would this make someone stop scrolling?
4. Engagement Factors: Action, people, drama, humor, revelation
5. Shareability: Would people want to share this?

"""
        
        if transcription_text:
            prompt += f"\nContext/Dialog: \"{transcription_text}\"\n"
        
        prompt += """
Respond in JSON format:
{
  "viral_score": 0.0-1.0,
  "reasoning": "Brief explanation",
  "categories": ["action", "humor", "surprise", etc.],
  "hook_potential": 0.0-1.0,
  "engagement_factors": ["list of factors"]
}"""
        
        return prompt
    
    def _parse_analysis(self, analysis_text: str) -> Dict:
        """Parse GPT-4 response"""
        try:
            # Try to extract JSON from response
            start = analysis_text.find('{')
            end = analysis_text.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_text = analysis_text[start:end]
                return json.loads(json_text)
            else:
                # Fallback parsing
                return {
                    'viral_score': 0.6,
                    'reasoning': analysis_text,
                    'categories': [],
                    'hook_potential': 0.6,
                    'engagement_factors': []
                }
        except Exception as e:
            print(f"[WARNING] Failed to parse analysis: {e}")
            return {
                'viral_score': 0.5,
                'reasoning': analysis_text[:200],
                'categories': [],
                'hook_potential': 0.5,
                'engagement_factors': []
            }
    
    def _extract_scene_frames(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        num_frames: int = 3
    ) -> List[str]:
        """Extract representative frames from scene"""
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Calculate frame timestamps
            duration = end_time - start_time
            frame_times = []
            
            if num_frames == 1:
                frame_times = [start_time + duration / 2]  # Middle frame
            elif num_frames == 2:
                frame_times = [start_time, end_time - 0.1]  # Start and end
            else:  # 3 or more
                step = duration / (num_frames - 1)
                frame_times = [start_time + i * step for i in range(num_frames)]
            
            # Extract frames
            frame_paths = []
            temp_dir = Path("temp/frame_analysis")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            for i, frame_time in enumerate(frame_times):
                # Seek to frame
                frame_number = int(frame_time * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                
                ret, frame = cap.read()
                if ret:
                    # Save frame
                    frame_path = temp_dir / f"scene_{start_time:.1f}_{i}.jpg"
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(str(frame_path))
            
            cap.release()
            
            return frame_paths
            
        except Exception as e:
            print(f"[ERROR] Frame extraction failed: {e}")
            return []
    
    def _calculate_duration_score(self, duration: float) -> float:
        """Calculate score based on optimal duration for viral clips"""
        # Optimal: 20-50 seconds
        if 20 <= duration <= 50:
            return 1.0
        elif 15 <= duration < 20 or 50 < duration <= 60:
            return 0.8
        elif 10 <= duration < 15:
            return 0.6
        elif 60 < duration <= 90:
            return 0.4
        else:
            return 0.2


class HybridViralDetector:
    """
    Hybrid approach: Combine AI (OpenAI) with rule-based analysis
    Falls back to rule-based if API fails or is too expensive
    """
    
    def __init__(self, use_ai: bool = True):
        # Check if OpenAI API key is configured and not empty
        has_api_key = (
            hasattr(settings, 'OPENAI_API_KEY') and 
            settings.OPENAI_API_KEY is not None and 
            len(str(settings.OPENAI_API_KEY).strip()) > 0
        )
        self.use_ai = use_ai and has_api_key
        self.ai_detector = None
        
        if self.use_ai:
            try:
                self.ai_detector = OpenAIViralDetector()
                print("[INFO] Using AI-powered viral detection (OpenAI GPT-4)")
            except ValueError as e:
                # API key not configured
                print(f"[INFO] OpenAI not configured: {e}")
                self.use_ai = False
                print("[INFO] Using rule-based viral detection (no API key)")
            except Exception as e:
                print(f"[WARNING] Failed to initialize AI detector: {e}")
                self.use_ai = False
                print("[INFO] Falling back to rule-based viral detection")
        else:
            print("[INFO] Using rule-based viral detection")
    
    def detect_viral_moments(
        self,
        video_path: str,
        scenes: List[Dict],
        transcription: Optional[Dict] = None,
        top_n: int = 5,
        min_duration: float = 10.0,
        target_duration: float = 45.0,
        max_duration: float = 60.0,
        merge_scenes: bool = True
    ) -> List[Dict]:
        """
        Detect viral moments using hybrid approach
        
        Args:
            video_path: Path to video
            scenes: List of scenes
            transcription: Optional transcription
            top_n: Number of top clips to return
            min_duration: Minimum clip duration (default 10s)
            target_duration: Target clip duration (default 45s)
            max_duration: Maximum clip duration (default 60s)
            merge_scenes: Whether to merge short scenes into longer clips
            
        Returns: Top viral scenes
        """
        try:
            # Step 1: Merge short scenes into longer clips if requested
            if merge_scenes and len(scenes) > 10:
                print(f"[MERGE] Merging {len(scenes)} short scenes into longer clips (target: {target_duration}s)...")
                scenes = self._merge_scenes_to_duration(
                    scenes, 
                    target_duration=target_duration,
                    max_duration=max_duration
                )
                print(f"[MERGE] Created {len(scenes)} merged clips")
            
            # Step 2: Analyze scenes for viral potential
            if self.use_ai and len(scenes) <= 50:  # Use AI for reasonable number of scenes
                # AI-based detection
                print(f"[AI] Analyzing {len(scenes)} scenes with GPT-4 Vision...")
                analyzed_scenes = self.ai_detector.batch_analyze_scenes(
                    video_path,
                    scenes,
                    transcription
                )
            else:
                # Rule-based fallback (built-in)
                print(f"[RULE-BASED] Analyzing {len(scenes)} scenes with heuristics...")
                analyzed_scenes = self._calculate_viral_score_builtin(scenes, transcription)
            
            # Filter top moments (lowered threshold for short-form clips)
            viral_moments = [s for s in analyzed_scenes if s.get('viral_score', 0) >= 0.35]
            viral_moments.sort(key=lambda x: x['viral_score'], reverse=True)
            
            print(f"[VIRAL] Found {len(viral_moments)} clips passing threshold 0.35")
            return viral_moments[:top_n]
            
        except Exception as e:
            print(f"[ERROR] Hybrid detection failed: {e}")
            # Ultimate fallback (built-in)
            return self._calculate_viral_score_builtin(scenes, transcription)[:top_n]
    
    def _calculate_viral_score_builtin(self, scenes, transcription):
        """Enhanced rule-based viral scoring with better differentiation"""
        scored_scenes = []
        
        for scene in scenes:
            duration = scene.get('duration', 0)
            complexity_score = scene.get('complexity_score', 0.3)
            keyframes_per_second = scene.get('keyframes_per_second', 0)
            scene_count = scene.get('scene_count', 1)  # For merged clips
            
            # Initialize score components
            score_components = {}
            
            # FACTOR 1: Duration optimization (30% weight)
            # Optimal for viral: 30-60s for complete story
            if 45 <= duration <= 60:
                duration_score = 1.0  # Perfect length
            elif 30 <= duration < 45:
                duration_score = 0.9  # Good length
            elif 20 <= duration < 30:
                duration_score = 0.7  # Acceptable
            elif 60 < duration <= 90:
                duration_score = 0.6  # A bit long
            elif 15 <= duration < 20:
                duration_score = 0.5  # Short but ok
            else:
                duration_score = 0.3  # Too short or too long
            
            score_components['duration'] = duration_score * 0.30
            
            # FACTOR 2: Action/Complexity (35% weight) - INCREASED
            # Use the improved complexity score from scene analysis
            complexity_weight = complexity_score * 0.35
            score_components['complexity'] = complexity_weight
            
            # FACTOR 3: Scene dynamics (15% weight)
            # Merged clips with multiple scenes show more variety
            if scene_count >= 4:
                dynamics_score = 1.0  # Great variety
            elif scene_count >= 3:
                dynamics_score = 0.8
            elif scene_count >= 2:
                dynamics_score = 0.6
            else:
                dynamics_score = 0.4  # Single scene
            
            score_components['dynamics'] = dynamics_score * 0.15
            
            # FACTOR 4: Pacing (10% weight)
            # High keyframe density = fast pacing = engaging
            if keyframes_per_second >= 0.8:
                pacing_score = 1.0  # Fast-paced
            elif keyframes_per_second >= 0.5:
                pacing_score = 0.8
            elif keyframes_per_second >= 0.3:
                pacing_score = 0.6
            else:
                pacing_score = 0.4  # Slow-paced
            
            score_components['pacing'] = pacing_score * 0.10
            
            # FACTOR 5: Transcription analysis (10% weight)
            transcription_score = 0.0
            if transcription:
                scene_start = scene.get('start_time', 0)
                scene_end = scene.get('end_time', 0)
                
                # Find text in this scene
                scene_text = ""
                word_count = 0
                if 'segments' in transcription:
                    for seg in transcription['segments']:
                        seg_start = seg.get('start', 0)
                        if scene_start <= seg_start < scene_end:
                            text = seg.get('text', '')
                            scene_text += text + " "
                            word_count += len(text.split())
                
                scene_text_lower = scene_text.lower()
                
                # Check viral keywords (emotion triggers)
                emotion_keywords = {
                    'excitement': ['amazing', 'incredible', 'wow', 'awesome', 'insane', 'crazy'],
                    'surprise': ['shocking', 'unbelievable', 'unexpected', 'surprise', 'what'],
                    'achievement': ['best', 'perfect', 'record', 'first', 'fastest', 'winner'],
                    'conflict': ['vs', 'versus', 'challenge', 'competition', 'battle'],
                    'urgency': ['now', 'must', 'need', 'quick', 'fast', 'hurry']
                }
                
                keyword_matches = 0
                for category, words in emotion_keywords.items():
                    for word in words:
                        if word in scene_text_lower:
                            keyword_matches += 1
                
                # Dialog density (more speech = more engaging)
                if duration > 0:
                    words_per_second = word_count / duration
                    if words_per_second >= 3:
                        dialog_score = 0.5  # High speech rate
                    elif words_per_second >= 1.5:
                        dialog_score = 0.3
                    else:
                        dialog_score = 0.1
                else:
                    dialog_score = 0.0
                
                # Combine transcription factors
                transcription_score = min(1.0, (keyword_matches * 0.15) + dialog_score)
            
            score_components['transcription'] = transcription_score * 0.10
            
            # Calculate final score
            final_score = sum(score_components.values())
            
            # Bonus: High complexity + good duration = extra boost
            if complexity_score >= 0.6 and 30 <= duration <= 60:
                final_score += 0.05  # Synergy bonus
            
            # Ensure score is between 0.0 and 1.0
            final_score = max(0.0, min(1.0, final_score))
            
            scene_copy = scene.copy()
            scene_copy['viral_score'] = round(final_score, 3)
            scene_copy['score_breakdown'] = {
                k: round(v, 3) for k, v in score_components.items()
            }
            scored_scenes.append(scene_copy)
        
        # Sort by score (descending)
        scored_scenes.sort(key=lambda x: x['viral_score'], reverse=True)
        return scored_scenes
    
    def _merge_scenes_to_duration(
        self,
        scenes: List[Dict],
        target_duration: float = 45.0,
        max_duration: float = 60.0
    ) -> List[Dict]:
        """
        Merge adjacent scenes to create clips closer to target duration
        
        Args:
            scenes: List of short scenes
            target_duration: Target duration for merged clips (default 45s)
            max_duration: Maximum allowed duration (default 60s)
            
        Returns: List of merged clips
        """
        if not scenes:
            return []
        
        # Sort scenes by start time
        scenes = sorted(scenes, key=lambda x: x.get('start_time', 0))
        
        merged_clips = []
        current_clip = None
        
        for scene in scenes:
            if current_clip is None:
                # Start new clip
                current_clip = {
                    'start_time': scene['start_time'],
                    'end_time': scene['end_time'],
                    'duration': scene['duration'],
                    'scenes': [scene],
                    'complexity_scores': [scene.get('complexity_score', 0.3)],
                }
            else:
                # Check if we should add this scene to current clip
                potential_duration = scene['end_time'] - current_clip['start_time']
                
                if potential_duration <= max_duration:
                    # Add scene to current clip
                    current_clip['end_time'] = scene['end_time']
                    current_clip['duration'] = potential_duration
                    current_clip['scenes'].append(scene)
                    current_clip['complexity_scores'].append(scene.get('complexity_score', 0.3))
                    
                    # If we're close to target, finish this clip
                    if potential_duration >= target_duration:
                        merged_clips.append(self._finalize_merged_clip(current_clip))
                        current_clip = None
                else:
                    # Current clip is full, save it and start new one
                    merged_clips.append(self._finalize_merged_clip(current_clip))
                    current_clip = {
                        'start_time': scene['start_time'],
                        'end_time': scene['end_time'],
                        'duration': scene['duration'],
                        'scenes': [scene],
                        'complexity_scores': [scene.get('complexity_score', 0.3)],
                    }
        
        # Don't forget the last clip
        if current_clip is not None:
            merged_clips.append(self._finalize_merged_clip(current_clip))
        
        return merged_clips
    
    def _finalize_merged_clip(self, clip: Dict) -> Dict:
        """Finalize merged clip with aggregated metadata"""
        # Average complexity score
        avg_complexity = sum(clip['complexity_scores']) / len(clip['complexity_scores'])
        
        # Determine action level based on complexity
        if avg_complexity >= 0.7:
            action_level = "high"
        elif avg_complexity >= 0.5:
            action_level = "medium"
        else:
            action_level = "low"
        
        return {
            'start_time': clip['start_time'],
            'end_time': clip['end_time'],
            'duration': clip['duration'],
            'scene_count': len(clip['scenes']),
            'complexity_score': round(avg_complexity, 2),
            'action_level': action_level,
            'is_merged': True,
        }
