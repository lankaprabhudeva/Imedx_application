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

```bash
pytest
```

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
