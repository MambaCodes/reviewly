"""LLM integration for analyzing PR reviews."""
import httpx
from typing import List
from .github_client import ReviewData

class DeepseekAnalyzer:
    """Client for analyzing PR reviews using Deepseek API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1"  # Replace with actual API endpoint
    
    async def analyze_reviews(self, reviews: List[ReviewData]) -> str:
        """Analyze PR reviews and generate a checklist."""
        # Prepare the context for the LLM
        context = self._prepare_context(reviews)
        
        # Call Deepseek API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-code",  # Replace with actual model name
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert code reviewer. Analyze the provided PR reviews and generate a comprehensive checklist for future code reviews based on common patterns and issues found."
                        },
                        {
                            "role": "user",
                            "content": context
                        }
                    ],
                    "temperature": 0.3
                }
            )
            
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
    
    def _prepare_context(self, reviews: List[ReviewData]) -> str:
        """Prepare context from review data for the LLM."""
        context = "Based on the following PR reviews, generate a markdown checklist:\n\n"
        
        for review in reviews:
            context += f"PR #{review.pr_number} - {review.file_path}:\n"
            context += f"Code:\n```\n{review.code_chunk}\n```\n"
            context += f"Review comment: {review.review_comment}\n\n"
        
        return context
