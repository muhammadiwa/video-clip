"""AI-powered content generation for viral titles, descriptions, and tags."""

import json
from typing import Dict, List, Optional, Any
from openai import OpenAI
from src.utils.logger import logger
from src.utils.config import Config


class ContentGenerator:
    """Generate viral content using AI."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize content generator.
        
        Args:
            api_key: OpenAI API key (default from config)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OpenAI API key not set. Using fallback content generation.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
    
    def generate_viral_content(
        self, 
        video_title: str = "",
        video_description: str = "",
        clip_context: str = "",
        duration: float = 60
    ) -> Dict[str, any]:
        """Generate viral title, description, and tags for a clip.
        
        Args:
            video_title: Original video title
            video_description: Original video description
            clip_context: Context about the clip
            duration: Clip duration in seconds
            
        Returns:
            Dictionary with title, description, tags, and hashtags
        """
        logger.info("Generating viral content...")
        
        if self.client:
            return self._generate_with_ai(video_title, video_description, clip_context, duration)
        else:
            return self._generate_fallback(video_title, duration)
    
    def _generate_with_ai(
        self, 
        video_title: str, 
        video_description: str,
        clip_context: str,
        duration: float
    ) -> Dict[str, Any]:
        """Generate content using OpenAI API.
        
        Args:
            video_title: Original video title
            video_description: Original video description
            clip_context: Context about the clip
            duration: Clip duration in seconds
            
        Returns:
            Dictionary with generated content
        """
        try:
            prompt = f"""You are a viral content expert specializing in YouTube Shorts. 
            
Original Video Title: {video_title}
Original Description: {video_description[:200]}
Clip Context: {clip_context}
Clip Duration: {duration:.0f} seconds

Generate highly engaging content for this YouTube Short clip:

1. A viral title (max 100 characters) that:
   - Creates curiosity or emotion
   - Uses power words
   - Is optimized for CTR
   
2. A compelling description (max 500 characters) that:
   - Hooks viewers in the first line
   - Includes relevant keywords
   - Adds value or context
   
3. 5-8 relevant tags for YouTube algorithm
4. 5-10 trending hashtags (including #shorts #viral)

Return the response as a JSON object with keys: title, description, tags, hashtags"""

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a viral content creator expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                # Extract JSON from response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    result = json.loads(json_str)
                    
                    logger.info("Generated viral content successfully")
                    return result
            except json.JSONDecodeError:
                logger.warning("Failed to parse JSON response, using fallback")
                
        except Exception as e:
            logger.error(f"Error generating content with AI: {str(e)}")
        
        return self._generate_fallback(video_title, duration)
    
    def _generate_fallback(self, video_title: str, duration: float) -> Dict[str, Any]:
        """Generate fallback content without AI.
        
        Args:
            video_title: Original video title
            duration: Clip duration in seconds
            
        Returns:
            Dictionary with generated content
        """
        logger.info("Using fallback content generation")
        
        # Create a simple viral title
        if video_title:
            title = f"🔥 {video_title[:80]} #Shorts"
        else:
            title = f"🔥 Amazing Viral Moment - Must Watch! #Shorts"
        
        # Create a simple description
        description = f"""This {int(duration)}s clip will blow your mind! 🤯

Watch till the end! 👀

{video_title if video_title else 'Original content'}

Drop a 💯 if you enjoyed!

#shorts #viral #trending #fyp #foryou"""
        
        # Default tags
        tags = ["shorts", "viral", "trending", "amazing", "must watch", "entertainment"]
        
        # Default hashtags
        hashtags = ["#shorts", "#viral", "#trending", "#fyp", "#foryou", "#amazing", "#mustsee", "#entertainment"]
        
        return {
            "title": title,
            "description": description,
            "tags": tags,
            "hashtags": hashtags
        }
    
    def generate_multiple_variants(
        self,
        video_title: str = "",
        video_description: str = "",
        clip_context: str = "",
        duration: float = 60,
        num_variants: int = 3
    ) -> List[Dict[str, Any]]:
        """Generate multiple content variants.
        
        Args:
            video_title: Original video title
            video_description: Original video description
            clip_context: Context about the clip
            duration: Clip duration in seconds
            num_variants: Number of variants to generate
            
        Returns:
            List of content dictionaries
        """
        variants = []
        
        for i in range(num_variants):
            variant = self.generate_viral_content(
                video_title, 
                video_description, 
                clip_context, 
                duration
            )
            variants.append(variant)
        
        return variants
