"""LLM integration for analyzing PR reviews."""
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .github_client import ReviewData

class DeepseekAnalyzer:
    """Client for analyzing PR reviews using Deepseek API."""
    
    def __init__(self, api_key: str):
        self.llm = ChatOpenAI(
            model="deepseek-reasoner",
            openai_api_key=api_key,
            base_url="https://api.deepseek.com/v1",
            temperature=0.3,
            top_p=0.1,
            reasoning_effort="high"
        )
        self.summarization_prompt = self._create_summarization_prompt()
        self.final_prompt = self._create_final_prompt()
    
    def _create_summarization_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for summarizing a batch of reviews."""
        template = """Analyze these PR review comments and extract key issues, patterns, and suggestions:

{context}

Provide a concise summary highlighting:
1. Common issues found
2. Best practices mentioned
3. Important feedback patterns

Keep the summary focused and actionable."""

        return ChatPromptTemplate.from_template(template)
    
    def _create_final_prompt(self) -> ChatPromptTemplate:
        """Create the prompt template for generating the final checklist."""
        template = """You are an expert code reviewer. Based on these summaries of PR reviews, generate a comprehensive checklist for future code reviews.

Review Summaries:
{context}

Create a detailed markdown checklist with the following sections:
# PR Review Checklist

## Common Issues to Watch For
- [list the most frequent problems found]

## Best Practices to Enforce
- [list the key practices to maintain]

## Areas Needing Extra Attention
- [list specific areas that often need more review]

## Positive Patterns to Encourage
- [list good practices seen in the reviews]

Make each item specific, actionable, and based on the actual review data. Use clear examples where helpful."""

        return ChatPromptTemplate.from_template(template)
    
    def analyze_reviews(self, reviews: List[ReviewData]) -> str:
        """Analyze PR reviews and generate a checklist."""
        print(f"Processing {len(reviews)} reviews in batches...")
        
        # Group reviews by PR to maintain context
        pr_groups = self._group_reviews_by_pr(reviews)
        
        # Split the groups into manageable chunks
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,
            chunk_overlap=1000,
            separators=["\n\n", "\n", " "]
        )
        
        # Process each batch and collect summaries
        summaries = []
        batch_size = 5  # Process 5 PRs at a time
        
        for i in range(0, len(pr_groups), batch_size):
            batch = pr_groups[i:i + batch_size]
            context = self._prepare_context(batch)
            
            try:
                # Generate summary for this batch
                print(f"Analyzing batch {i//batch_size + 1}/{(len(pr_groups) + batch_size - 1)//batch_size}...")
                chain = self.summarization_prompt | self.llm
                result = chain.invoke({"context": context})
                summaries.append(result.content)
            except Exception as e:
                print(f"Warning: Error processing batch {i//batch_size + 1}: {str(e)}")
                continue
        
        if not summaries:
            raise RuntimeError("Failed to generate any summaries from the reviews")
        
        # Generate final checklist from summaries
        try:
            chain = self.final_prompt | self.llm
            result = chain.invoke({"context": "\n\n".join(summaries)})
            return result.content
        except Exception as e:
            raise RuntimeError(f"Failed to generate final checklist: {str(e)}") from e
    
    def _group_reviews_by_pr(self, reviews: List[ReviewData]) -> List[List[ReviewData]]:
        """Group reviews by PR number."""
        pr_dict = {}
        for review in reviews:
            if review.pr_number not in pr_dict:
                pr_dict[review.pr_number] = []
            pr_dict[review.pr_number].append(review)
        return list(pr_dict.values())
    
    def _prepare_context(self, pr_groups: List[List[ReviewData]]) -> str:
        """Prepare context from groups of review data for the LLM."""
        context_parts = []
        
        for group in pr_groups:
            if not group:
                continue
                
            pr_num = group[0].pr_number
            context_parts.append(f"PR #{pr_num}:")
            
            for review in group:
                context_parts.append(f"File: {review.file_path}")
                if review.code_chunk:
                    # Truncate very long code chunks
                    code = review.code_chunk[:500] + "..." if len(review.code_chunk) > 500 else review.code_chunk
                    context_parts.append(f"Code:\n```\n{code}\n```")
                context_parts.append(f"Review comment: {review.review_comment}\n")
        
        return "\n".join(context_parts)
