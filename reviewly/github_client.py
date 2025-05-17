"""GitHub related functionality."""
import sys
from typing import List, Optional
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
    line_number: int

class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self, token: str, repo_url: str):
        try:
            self.github = Github(token)
            # Test authentication first
            try:
                user = self.github.get_user().login
                print(f"Successfully authenticated as: {user}")
            except GithubException as e:
                if e.status == 401:
                    print("Error: Invalid GitHub token. Please check your token.", file=sys.stderr)
                    raise
                else:
                    print(f"GitHub API Error: {str(e)}", file=sys.stderr)
                    raise
            
            # Extract owner and repo from URL
            repo_url = repo_url.rstrip('/')
            if repo_url.endswith('.git'):
                repo_url = repo_url[:-4]
            
            parts = repo_url.split('/')
            # Find the owner and repo name from the URL
            if len(parts) >= 2:
                self.owner = parts[-2]
                self.repo_name = parts[-1]
                print(f"Accessing repository: {self.owner}/{self.repo_name}")
            else:
                raise ValueError(f"Invalid repository URL format: {repo_url}")
            
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
                elif e.status == 403:
                    print(f"Error: No permission to access repository '{self.owner}/{self.repo_name}'", file=sys.stderr)
                    print("Please check if:", file=sys.stderr)
                    print("1. Your token has the 'repo' scope", file=sys.stderr)
                    print("2. You have access to this repository", file=sys.stderr)
                raise
                
        except Exception as e:
            print(f"Error initializing GitHub client: {str(e)}", file=sys.stderr)
            raise

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

    def get_pr_reviews(self, limit: int = 100) -> List[ReviewData]:
        """Get review data from recent pull requests."""
        reviews = []
        
        # Get pull requests
        pulls = self.repo.get_pulls(state='closed', sort='updated', direction='desc')
        
        for pr in pulls[:limit]:
            # Get review comments for the PR
            review_comments = pr.get_review_comments()
            
            for comment in review_comments:
                reviews.append(
                    ReviewData(
                        pr_number=pr.number,
                        file_path=comment.path,
                        code_chunk=comment.diff_hunk,
                        review_comment=comment.body,
                        line_number=comment.line
                    )
                )
        
        return reviews
