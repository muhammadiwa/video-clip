from typing import Dict, List, Optional
import re

class ViralMomentDetector:
    """
    Detect viral moments in video based on multiple factors:
    - Scene changes and action intensity
    - Transcription keywords and sentiment
    - Audio energy and speech patterns
    """
    
    # Viral keywords (words that typically indicate engaging content)
    VIRAL_KEYWORDS = {
        'high': [
            'amazing', 'incredible', 'wow', 'unbelievable', 'shocking', 'insane',
            'crazy', 'awesome', 'fantastic', 'epic', 'mind-blowing', 'spectacular',
            'omg', 'wtf', 'holy', 'damn', 'perfect', 'genius', 'brilliant'
        ],
        'medium': [
            'great', 'good', 'nice', 'cool', 'interesting', 'fun', 'funny',
            'hilarious', 'weird', 'strange', 'unexpected', 'surprise', 'beautiful',
            'wonderful', 'love', 'hate', 'best', 'worst', 'first', 'last'
        ],
        'low': [
            'okay', 'fine', 'normal', 'regular', 'typical', 'usual', 'average'
        ]
    }
    
    # Emotional indicators
    EMOTION_KEYWORDS = {
        'excitement': ['excited', 'exciting', 'thrilled', 'pumped', 'hyped'],
        'humor': ['funny', 'hilarious', 'laugh', 'lol', 'haha', 'joke', 'comedy'],
        'shock': ['shocking', 'surprised', 'unexpected', 'sudden', 'omg', 'wow'],
        'inspiration': ['inspiring', 'motivated', 'powerful', 'moving', 'touching'],
        'controversy': ['controversial', 'debate', 'disagree', 'argument', 'against'],
    }
    
    @staticmethod
    def calculate_viral_score(
        scenes: List[Dict],
        transcription: Optional[Dict] = None,
        video_info: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Calculate viral score for each scene/segment
        Returns: scenes with viral_score added
        """
        try:
            scored_scenes = []
            
            for scene in scenes:
                score_components = {
                    'scene_action': 0.0,
                    'duration_optimal': 0.0,
                    'keyword_relevance': 0.0,
                    'emotion_score': 0.0,
                    'speech_density': 0.0,
                }
                
                # 1. Scene action score (based on complexity)
                if 'complexity_score' in scene:
                    score_components['scene_action'] = scene['complexity_score'] * 0.2
                elif 'action_level' in scene:
                    action_levels = {'high': 0.9, 'medium': 0.6, 'low': 0.3}
                    score_components['scene_action'] = action_levels.get(
                        scene['action_level'], 0.5
                    ) * 0.2
                
                # 2. Duration score (viral clips are usually 15-60 seconds)
                duration = scene.get('duration', 0)
                if 15 <= duration <= 60:
                    score_components['duration_optimal'] = 0.3
                elif 10 <= duration < 15 or 60 < duration <= 90:
                    score_components['duration_optimal'] = 0.2
                else:
                    score_components['duration_optimal'] = 0.1
                
                # 3. Transcription analysis (if available)
                if transcription and 'segments' in transcription:
                    scene_start = scene['start_time']
                    scene_end = scene['end_time']
                    
                    # Find transcription segments in this scene
                    scene_segments = [
                        seg for seg in transcription['segments']
                        if scene_start <= seg['start'] < scene_end
                    ]
                    
                    if scene_segments:
                        # Keyword relevance
                        scene_text = ' '.join([seg['text'].lower() for seg in scene_segments])
                        keyword_score = ViralMomentDetector._calculate_keyword_score(scene_text)
                        score_components['keyword_relevance'] = keyword_score * 0.25
                        
                        # Emotion score
                        emotion_score = ViralMomentDetector._calculate_emotion_score(scene_text)
                        score_components['emotion_score'] = emotion_score * 0.15
                        
                        # Speech density (words per second)
                        word_count = len(scene_text.split())
                        speech_density = word_count / duration if duration > 0 else 0
                        
                        # Optimal speech density: 2-4 words per second
                        if 2 <= speech_density <= 4:
                            score_components['speech_density'] = 0.1
                        elif 1 <= speech_density < 2 or 4 < speech_density <= 5:
                            score_components['speech_density'] = 0.05
                
                # Calculate total viral score
                total_score = sum(score_components.values())
                
                scene_copy = scene.copy()
                scene_copy['viral_score'] = round(total_score, 3)
                scene_copy['score_components'] = score_components
                scene_copy['is_viral_candidate'] = total_score >= 0.6
                
                scored_scenes.append(scene_copy)
            
            # Sort by viral score (highest first)
            scored_scenes.sort(key=lambda x: x['viral_score'], reverse=True)
            
            return scored_scenes
            
        except Exception as e:
            raise Exception(f"Failed to calculate viral score: {str(e)}")
    
    @staticmethod
    def _calculate_keyword_score(text: str) -> float:
        """Calculate score based on viral keywords"""
        score = 0.0
        text_lower = text.lower()
        
        # Count high-value keywords
        high_count = sum(1 for keyword in ViralMomentDetector.VIRAL_KEYWORDS['high']
                        if keyword in text_lower)
        medium_count = sum(1 for keyword in ViralMomentDetector.VIRAL_KEYWORDS['medium']
                          if keyword in text_lower)
        low_count = sum(1 for keyword in ViralMomentDetector.VIRAL_KEYWORDS['low']
                       if keyword in text_lower)
        
        # Weighted scoring
        score = (high_count * 0.5 + medium_count * 0.3 + low_count * 0.1)
        
        # Normalize to 0-1 range
        score = min(score / 3, 1.0)
        
        return score
    
    @staticmethod
    def _calculate_emotion_score(text: str) -> float:
        """Calculate score based on emotional keywords"""
        score = 0.0
        text_lower = text.lower()
        
        emotion_counts = {}
        for emotion, keywords in ViralMomentDetector.EMOTION_KEYWORDS.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            emotion_counts[emotion] = count
        
        # Total emotional content
        total_emotions = sum(emotion_counts.values())
        
        # Normalize to 0-1 range
        score = min(total_emotions / 5, 1.0)
        
        return score
    
    @staticmethod
    def filter_top_viral_moments(
        scored_scenes: List[Dict],
        top_n: int = 5,
        min_score: float = 0.5
    ) -> List[Dict]:
        """
        Filter top viral moments
        Returns: top N scenes with score >= min_score
        """
        try:
            # Filter by minimum score
            filtered = [
                scene for scene in scored_scenes
                if scene['viral_score'] >= min_score
            ]
            
            # Return top N
            return filtered[:top_n]
            
        except Exception as e:
            raise Exception(f"Failed to filter viral moments: {str(e)}")
    
    @staticmethod
    def generate_clip_metadata(scene: Dict, transcription: Optional[Dict] = None) -> Dict:
        """
        Generate metadata for a viral clip
        """
        try:
            metadata = {
                'start_time': scene['start_time'],
                'end_time': scene['end_time'],
                'duration': scene['duration'],
                'viral_score': scene.get('viral_score', 0),
                'is_viral_candidate': scene.get('is_viral_candidate', False),
            }
            
            # Add transcription if available
            if transcription and 'segments' in transcription:
                scene_start = scene['start_time']
                scene_end = scene['end_time']
                
                scene_segments = [
                    seg for seg in transcription['segments']
                    if scene_start <= seg['start'] < scene_end
                ]
                
                if scene_segments:
                    metadata['transcript'] = ' '.join([seg['text'] for seg in scene_segments])
                    metadata['has_speech'] = True
                else:
                    metadata['has_speech'] = False
            
            return metadata
            
        except Exception as e:
            raise Exception(f"Failed to generate clip metadata: {str(e)}")
