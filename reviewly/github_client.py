"""GitHub related functionality."""
import sys
import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse
from pydantic import BaseModel
from github import Github
from github.PullRequest import PullRequest
from github.Repository import Repository
from github.GithubException import GithubException

class ReviewData(BaseModel):
    """Model for storing review data."""
    pr_number: int
    file_path: str
    code_chunk: str
    review_comment: str
    line_number: Optional[int] = None

    class Config:
        """Pydantic config to allow json serialization"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: str, repo_url: str, cache_dir: str = None):
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), '..', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
        try:
            self.github = Github(token)
            # Test authentication first            
            try:
                user = self.github.get_user().login
                print(f"Successfully authenticated as: {user}")
            except GithubException as e:
                if e.status == 401:
                    print("Error: Invalid GitHub token. Please check your token.", file=sys.stderr)
                    raise e
                else:
                    print(f"GitHub API Error: {str(e)}", file=sys.stderr)
                    raise e
            
            # Extract owner and repo from URL
            self.owner, self.repo_name = self._parse_repo_url(repo_url)
            print(f"Accessing repository: {self.owner}/{self.repo_name}")
            
            self._repo = None
            
            # Test repository access
            try:
                self.repo  # This will trigger the property and test the connection
            except GithubException as e:
                if e.status == 404:
                    print(f"Error: Repository '{self.owner}/{self.repo_name}' not found.", file=sys.stderr)
                    print("Please check if:", file=sys.stderr)
                    print("1. The repository name is correct (case-sensitive)", file=sys.stderr)
                    print("2. The repository exists", file=sys.stderr)
                    print("3. You have access to the repository", file=sys.stderr)
                    raise e
                elif e.status == 403:
                    print(f"Error: No permission to access repository '{self.owner}/{self.repo_name}'", file=sys.stderr)
                    print("Please check if:", file=sys.stderr)
                    print("1. Your token has the 'repo' scope", file=sys.stderr)
                    print("2. You have access to this repository", file=sys.stderr)
                    raise e
                raise e
                
        except Exception as e:
            print(f"Error initializing GitHub client: {str(e)}", file=sys.stderr)
            raise e

    def _parse_repo_url(self, repo_url: str) -> tuple[str, str]:
        """Parse the repository URL to extract owner and repo name."""
        # Handle case where URL is already in owner/repo format
        if '/' in repo_url and not any(x in repo_url for x in ['http', 'git@']):
            parts = repo_url.split('/')
            return parts[-2], parts[-1]  # Preserve case
        
        # Handle full URLs
        url = urlparse(repo_url)
        if not url.path:
            raise ValueError(f"Invalid repository URL format: {repo_url}")
        
        # Remove .git extension if present and preserve case
        path = url.path.rstrip('/')
        if path.endswith('.git'):
            path = path[:-4]
        
        # Split path into parts and get the last two components
        parts = [p for p in path.split('/') if p]
        if len(parts) < 2:
            raise ValueError(f"Invalid repository URL format: {repo_url}")
        
        # Return owner and repo name with original case preserved
        return parts[-2], parts[-1]  # Preserve case exactly as in URL

    @property
    def repo(self) -> Repository:
        """Get the repository instance."""
        if not self._repo:
            try:
                repo_path = f"{self.owner}/{self.repo_name}"
                print(f"Attempting to access repository: {repo_path}")
                self._repo = self.github.get_repo(repo_path)
            except Exception as e:
                raise ValueError(f"Could not access repository {self.owner}/{self.repo_name}. Error: {str(e)}")
        return self._repo

    def _get_cache_path(self) -> Path:
        """Get the path to the cache file for the current repo."""
        return Path(self.cache_dir) / f"{self.owner}_{self.repo_name}_reviews.json"

    def _load_from_cache(self) -> Optional[List[ReviewData]]:
        """Load review data from cache if available."""
        cache_path = self._get_cache_path()
        if cache_path.exists():
            print("Loading reviews from cache...")
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                    return [ReviewData(**item) for item in data]
            except Exception as e:
                print(f"Warning: Failed to load cache: {str(e)}", file=sys.stderr)
        return None

    def _save_to_cache(self, reviews: List[ReviewData]):
        """Save review data to cache."""
        cache_path = self._get_cache_path()
        print(f"Saving {len(reviews)} reviews to cache...")
        try:
            with open(cache_path, 'w') as f:
                json.dump([review.dict() for review in reviews], f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save cache: {str(e)}", file=sys.stderr)

    def get_pr_reviews(self, limit: int = 100, use_cache: bool = True) -> List[ReviewData]:
        """Get review data from recent pull requests."""
        if use_cache:
            cached = self._load_from_cache()
            if cached:
                return cached

        reviews = []
        print("Fetching PR reviews...")
        # Get pull requests
        pulls = self.repo.get_pulls(state='closed', sort='updated', direction='desc')
        
        for pr in pulls[:limit]:
            print(f"Processing PR #{pr.number}...")
            try:
                # Get review comments for the PR
                review_comments = pr.get_review_comments()
                
                for comment in review_comments:
                    # Get line number safely, defaulting to None if not available
                    try:
                        line_number = comment.line if hasattr(comment, 'line') else None
                    except AttributeError:
                        line_number = None

                    reviews.append(
                        ReviewData(
                            pr_number=pr.number,
                            file_path=comment.path,
                            code_chunk=comment.diff_hunk if hasattr(comment, 'diff_hunk') else '',
                            review_comment=comment.body,
                            line_number=line_number
                        )
                    )
            except Exception as e:
                print(f"Warning: Error processing PR #{pr.number}: {str(e)}", file=sys.stderr)
                continue
        
        print(f"Found {len(reviews)} review comments")
        self._save_to_cache(reviews)
        return reviews
