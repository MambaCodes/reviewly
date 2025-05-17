"""Main entry point for reviewly."""
import asyncio
from rich import print
from reviewly.config import get_config
from reviewly.github_client import GitHubClient
from reviewly.analyzer import DeepseekAnalyzer

async def main():
    """Main function."""
    # Load configuration
    config = get_config()
    
    # Initialize clients
    github_client = GitHubClient(config.github_token, config.github_repo_url)
    analyzer = DeepseekAnalyzer(config.deepseek_api_key)
    
    try:
        # Fetch PR reviews
        print("[bold blue]Fetching PR reviews...[/bold blue]")
        reviews = github_client.get_pr_reviews(limit=50)  # Get last 50 PRs
        
        if not reviews:
            print("[bold yellow]No PR reviews found.[/bold yellow]")
            return
        
        print(f"[green]Found {len(reviews)} review comments[/green]")
        
        # Analyze reviews
        print("[bold blue]Analyzing reviews with DeepSeek...[/bold blue]")
        checklist = await analyzer.analyze_reviews(reviews)
        
        # Save results
        output_file = "pr_checklist.md"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("# PR Review Checklist\n\n")
            f.write("This checklist was automatically generated based on recent PR reviews.\n\n")
            f.write(checklist)
        
        print(f"[bold green]✓ Checklist saved to {output_file}[/bold green]")
        
    except Exception as e:
        print(f"[bold red]Error: {str(e)}[/bold red]")

if __name__ == "__main__":
    asyncio.run(main())
