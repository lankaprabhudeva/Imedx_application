# Playwright MCP Test Automation Framework

This framework provides:

- Playwright with Pytest
- Page Object Model
- Skills-based test case generation
- MCP server implementation
- Generated manual and automation test outputs

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
playwright install
```

## Run Tests

Run the default environment:

```bash
pytest
```

Run a specific environment using the `ENV` variable:

```bash
ENV=hcs_demo pytest
```

On Windows PowerShell:

```powershell
$env:ENV = "hcs_demo"
pytest
```

Or use the helper script:

```bash
python scripts/run_environment_tests.py --env hcs_demo
```

Run all environments from `config/environments.yaml`:

```bash
python scripts/run_environment_tests.py --all
```

Supported environment keys:

- `dev`
- `qa`
- `hcs_dev`
- `hcs_demo`
- `san_prod`
- `san_dev`
- `hcs_cobl`
- `hcs_internal`
- `fiji`
- `nmhs`
- `usa`
- `pallasai_test`

Run generated tests only:

```bash
pytest tests/generated/
```

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
