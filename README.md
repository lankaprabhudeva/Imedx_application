# Playwright MCP Test Automation Framework

This repository is an end-to-end Python automation framework for the Imedx application.
It is built with Playwright and Pytest and includes support for environment-driven execution, page object modeling, and an MCP server for generating test artifacts.

## Project Summary

- **Purpose:** Automate UI testing for Imedx workflows using Playwright.
- **Primary users:** QA engineers, automation developers, and anyone who needs to run or extend UI tests.
- **Key features:**
  - Browser automation with Playwright
  - Test execution via Pytest
  - Page Object Model for maintainable page classes
  - Environment configuration in `config/environments.yaml`
  - Helper scripts to run tests across environments
  - Built-in MCP server for generating tests, page objects, and documentation

## What is included

- `pages/` — page objects and workflow automation pages
- `tests/` — pytest tests and E2E test cases
- `config/` — environment settings and configuration
- `scripts/` — helper scripts for test execution
- `mcp_server/` — MCP server implementation
- `requirements.txt` — Python dependencies

This framework provides:

- Playwright with Pytest
- Page Object Model
- Skills-based test case generation
- MCP server implementation
- Generated manual and automation test outputs

## Setup Guide for New Team Members

### Prerequisites

Before cloning the repository, ensure you have the following installed:

1. **Python 3.8 or higher**
   - Download from https://www.python.org/downloads/
   - Verify: `python --version`

2. **Git**
   - Download from https://git-scm.com/downloads
   - Verify: `git --version`

3. **A code editor (optional but recommended)**
   - VS Code: https://code.visualstudio.com/

### Step 1: Clone the Repository

```bash
git clone https://github.com/lankaprabhudeva/Imedx_application.git
cd Imedx_application
```

### Step 2: Create a Python Virtual Environment

This isolates project dependencies from your system Python.

**Windows (PowerShell or Command Prompt):**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your terminal prompt after activation.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `playwright` — browser automation library
- `pytest` — test framework
- `pytest-playwright` — pytest plugin for Playwright
- `pytest-html` — HTML test report generation
- `pyyaml` — for environment configuration
- `mcp` — Model Context Protocol support

### Step 4: Install Playwright Browsers

```bash
playwright install
```

This downloads the browser binaries (Chromium, Firefox, WebKit) that Playwright needs to run.

### Step 5: Configure Environment (Optional)

Edit `config/environments.yaml` if you need to add custom environment URLs or credentials:

```yaml
dev:
  url: "https://dev-env.example.com"
  username: "dev_user"
qa:
  url: "https://qa-env.example.com"
  username: "qa_user"
```

### Verification

Run a quick test to ensure everything is set up correctly:

```bash
pytest --version
playwright --version
```

You should see version numbers for both tools.

## Run Tests

### Run all tests
```bash
pytest
```

### Run tests for a specific environment

**Windows PowerShell:**
```powershell
$env:ENV = "hcs_demo"
pytest
```

**Windows Command Prompt:**
```cmd
set ENV=hcs_demo
pytest
```

**macOS / Linux:**
```bash
ENV=hcs_demo pytest
```

### Run tests from a specific test file
```bash
pytest tests/test_login.py
```

### Run tests with HTML report
```bash
pytest --html=report.html --self-contained-html
```

### Run helper script (recommended for easy environment selection)
```bash
python scripts/run_environment_tests.py --env hcs_demo
```

### Run all environments
```bash
python scripts/run_environment_tests.py --all
```

Supported environment keys in `config/environments.yaml`:
- `dev`, `qa`, `hcs_dev`, `hcs_demo`, `san_prod`, `san_dev`, `hcs_cobl`, `hcs_internal`, `fiji`, `nmhs`, `usa`, `pallasai_test`

## Troubleshooting

### Issue: Python not found
**Solution:** Ensure Python is installed and added to PATH. Test with `python --version`

### Issue: Virtual environment not activating
**Solution:** Check you used the correct activation command for your OS. After activation, you should see `(.venv)` in your terminal.

### Issue: Playwright browsers not installed
**Solution:** Run `playwright install` to download browser binaries.

### Issue: Tests cannot find pages or selectors
**Solution:** Verify that the environment URL in `config/environments.yaml` is correct and accessible.

### Issue: Permission denied on `.venv/Scripts/activate` (Windows)
**Solution:** Run PowerShell as Administrator, or use Command Prompt instead.



## Run MCP Server

```bash
python -m mcp_server.server
```

This starts the MCP server on `http://127.0.0.1:8000`.

## MCP Tools

- `generate_test_cases`
- `generate_playwright_tests`
- `generate_page_object`
- `generate_manual_test_document`

## Example Requirement

```text
As a user, I want to login with valid username and password.
If credentials are correct, I should be redirected to dashboard.
If credentials are wrong, I should see an error message.
```
