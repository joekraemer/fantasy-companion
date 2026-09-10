# 🤖 AI Agent Guidelines: Fantasy Companion

Welcome, AI Agent! This document outlines the project structure, development workflows, and testing guidelines for the **Fantasy Companion** repository.

## 🏗️ Repository Structure

The project follows a modular Python architecture designed for Streamlit:

- `app.py`: The main entry point for the Streamlit dashboard.
- `requirements.txt`: Python dependencies.
- `.env`: Local secrets and configuration (never commit this).
- `docs/`: System architecture (`ARCHITECTURE.md`) and API schemas (`DATA_ARSENAL.md`).
- `src/core/`: Central data management, caching (`data_manager.py`), and configuration.
- `src/engines/`: Wrappers for external APIs (`espn_client.py`, `nfl_stats.py`).
- `src/ui/`: Streamlit view components and layouts.
- `tests/`: Automated unit and integration tests (using `pytest`).

## 🛠️ Build & Setup Instructions

To run or develop locally, execute the following from the workspace root:

1. **Environment Initialization:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configuration:** Verify the `.env` file is present and populated with ESPN league credentials (`LEAGUE_ID`, `SWID`, `ESPN_S2`).
3. **Run Application:**
   ```bash
   streamlit run app.py
   ```

## 🧪 Testing Guidelines

We prioritize test-driven reliability. Our primary testing framework is `pytest`.

### How to Run Tests
From the workspace root, make sure your virtual environment is active:
- **Run all tests:** `python -m pytest`
- **Run specific file:** `python -m pytest tests/test_espn_client.py`
- **Run with coverage:** `python -m pytest --cov=src`

### Writing Tests
1. **Location:** Place all test files in the `tests/` directory. Prefix filenames with `test_` (e.g., `test_data_manager.py`).
2. **Mocking External APIs:** The app relies on live data (`espn-api`, NFLverse Parquet). You MUST mock network requests and API responses in unit tests using `unittest.mock.patch` or `requests-mock`. Tests should not fail during the off-season or without an internet connection.
3. **Focus:** Ensure that data transformation logic (e.g., merging Vegas odds with free-agent pools) is thoroughly tested with dummy dataframes.

## 🐙 GitHub Integration & AI Workflow

AI Agents are expected to actively manage project state and code quality via the GitHub CLI (`gh`).

### Issue Tracking & Project Management
1. **Implementation Plans:** When architecting a new feature, track the proposed implementation plan in a GitHub issue.
2. **Claiming Issues (Concurrency Lock):** To prevent duplicate work, the moment an AI agent begins working on an existing issue, it MUST use the `gh` CLI to claim it:
   - Add a comment to the issue: `gh issue comment <issue-number> -b "🤖 **AI Agent Claim:** I have begun work on this issue on branch \`<branch-name>\`."`
   - Add a label to the issue: `gh issue edit <issue-number> --add-label "status: AI-in-progress"` (create the label if it does not exist).
3. **Bugs & Technical Debt:** If you encounter a bug or edge case that cannot be fixed immediately within the current context, **log a GitHub issue** for it.
4. **Bug Bashing & Investigations:** When investigating complex bugs, log your learnings, stack traces, and hypotheses as comments on the relevant GitHub issue.
5. **Follow-on Features:** If you come up with an idea for a follow-on feature or optimization, do not scope creep. Instead, log a new GitHub issue labeled `enhancement`.

### AI Code Review (Subagent Workflow)
To maintain high code quality, we utilize an AI peer-review system:
1. When a significant feature is completed, the primary AI agent should create a Pull Request or Branch.
2. A **subagent** should be spun up (e.g., using the `invoke_subagent` tool).
3. The reviewer subagent will analyze the diff, check for edge cases, performance, and adherence to `AGENTS.md`.
4. The primary agent will address the subagent's feedback and push updates. **ONLY the human user is authorized to merge Pull Requests into the main branch. Agents must NEVER execute a merge.**
