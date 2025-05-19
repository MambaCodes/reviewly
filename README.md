# Reviewly 🔍

Reviewly is an intelligent PR checklist generator that helps teams catch issues before reviews by learning from past feedback patterns. It creates customized, actionable checklists that developers can use to self-review their code.

## 🎯 Purpose

Code reviews often catch the same types of issues repeatedly, leading to multiple review cycles and decreased team productivity. Reviewly automates this process by:

- Learning from your team's historical PR review patterns
- Generating tailored pre-review checklists that match your team's standards
- Helping developers catch common issues before requesting reviews
- Creating a self-review culture with data-driven guidelines
- Reducing review iterations and improving code quality upfront

## ✨ Features

- 📊 Analyzes PR review comments using AI
- 🔄 Caches review data for faster processing
- 📝 Generates comprehensive review checklists
- 🎨 Identifies team-specific coding patterns
- 🚀 Surfaces actionable improvements

## 🛠 Installation

1. Clone the repository:

   ```powershell
   git clone https://github.com/yourusername/reviewly.git
   cd reviewly
   ```

2. Create a virtual environment and install dependencies:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   uv pip install -e .
   ```

3. Create a `.env` file with your credentials:
   ```env
   GITHUB_REPO_URL=https://github.com/org/repo
   GITHUB_TOKEN=your_github_token
   DEEPSEEK_API_KEY=your_deepseek_api_key
   ```

## 🚀 Usage

Run Reviewly to analyze your repository's PR reviews:

```powershell
uv run main.py
```

The tool will:

1. Fetch recent PR reviews from your repository
2. Analyze the review patterns using AI
3. Generate a comprehensive `pr_checklist.md` file

## 📋 Generated Checklist

The generated checklist includes:

- Common issues to watch for
- Best practices to enforce
- Areas needing extra attention
- Positive patterns to encourage

## 📸 Sample Outputs

### Terminal Output

```powershell
Successfully authenticated as: [redacted for privacy]
Accessing repository: MambaCodes/[redacted for privacy]
Attempting to access repository: MambaCodes/[redacted for privacy]
Fetching PR reviews...
Loading reviews from cache...
Found 676 review comments
Analyzing reviews with DeepSeek...
Processing 676 reviews in batches...
Analyzing batch 1/6...
Analyzing batch 2/6...
Analyzing batch 3/6...
Analyzing batch 4/6...
Analyzing batch 5/6...
Analyzing batch 6/6...
✓ Checklist saved to pr_checklist.md
```

### Generated Checklist Example

```markdown
# PR Review Checklist

## Common Issues to Watch For

- **Type Safety Issues**
  - Missing TypeScript types/props (avoid `any`, enforce strict typing)
  - Zod schema validation gaps (e.g., using `nonempty()` instead of `min(1)`)
- **State Management Anti-Patterns**
  - Unnecessary `useState`/`useEffect` for data that could use React Query
  - Manual form state management instead of `react-hook-form`
- **Component Smells**
  - Hardcoded colors/values (e.g., `border-gray-700` instead of theme variables)
  - Redundant Tailwind classes (e.g., `h-4 w-4` instead of `size-4`)
  - Missing empty states for lists/tables

[...and more sections...]
```

## Generating the Checklist (the markdown one which can be added in PR template)

So with the output I got in the previous step inside the `pr_checklist.md` file, I just used this prompt:

```markdown
I want you to generate a developer-friendly PR checklist in markdown that people would realistically tick off while raising a pull request.

Here is the reference data to base the checklist on:
{the content of the pr_checklist.md file comes here}
```

and voila, I got the checklist in a developer-friendly format.

```markdown
# ✅ PR Checklist (for Authors & Reviewers)

Please confirm each item before marking the PR as ready for review.

---

### 🔒 Type Safety & Validation

- [ ] No usage of `any`; all types are explicit
- [ ] Zod schemas used & validated properly (e.g., `nonempty()`, regex, enums)
- [ ] Centralized validation in `lib/validations`

### 🧠 State & Data Flow

- [ ] Avoided unnecessary `useState`/`useEffect` – used React Query when possible
- [ ] API calls use TanStack Query; no raw `fetch`
- [ ] Query components follow `loading → error → data` pattern

### 🧩 Components & UI

- [ ] Used `shadcn/ui` components for inputs, buttons, etc.
- [ ] No hardcoded colors/classes; used theme (`text-primary`, `size-4`, etc.)
- [ ] Empty states are handled for lists/tables
- [ ] Responsive & accessible (`FormLabel`, proper alt text)

### 🛡 Security & Auth

- [ ] Passwords: no hardcoded patterns, use secure generation
- [ ] Validations enforced on both backend & frontend
- [ ] Routes and auth checks are consistent and non-redundant

### ⚠️ Error Handling

- [ ] Proper loading/error states implemented
- [ ] User-facing errors use `toast.error` with `getErrorMessage(error)`

### 📁 Code Quality & Structure

- [ ] Constants → `lib/constants`
- [ ] Logic extracted to hooks/helpers (e.g., `useFilteredData`)
- [ ] Self-closing JSX tags, clean formatting

### 🚀 Performance & Best Practices

- [ ] Expensive functions memoized (`useMemo`, `useCallback`)
- [ ] No `useEffect` timers — use `useInterval` if needed
- [ ] Discriminated unions used for complex TypeScript states

---

✅ Tick every box before merging! Small habits = long-term quality.
```

## 🔧 Configuration

### Environment Variables

- `GITHUB_REPO_URL`: URL of the GitHub repository to analyze
- `GITHUB_TOKEN`: GitHub personal access token with repo access
- `DEEPSEEK_API_KEY`: API key for DeepSeek's AI model

### Output Files

The following files are generated during execution and are ignored by git:

- `pr_checklist.md`: Generated review checklist
- `cache/`: Directory containing cached PR review data
- `.env`: Your environment variables file

### Performance Settings

- By default, analyzes the last 50 PRs (configurable)
- Caches review data to avoid repeated API calls
- Uses batched processing for large repositories

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/awesome-feature`)
3. Commit your changes (`git commit -m 'Add awesome feature'`)
4. Push to the branch (`git push origin feature/awesome-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Uses [PyGithub](https://github.com/PyGithub/PyGithub) for GitHub API integration
- Powered by DeepSeek's AI for analysis
- Built with [LangChain](https://github.com/langchain-ai/langchain) for AI orchestration
