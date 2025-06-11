# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Development Environment
- Install dependencies: `pipenv install --dev`
- Activate virtual environment: `pipenv shell`

### Running the Application
- Start the Tornado web server: `python main.py`
  - Server runs on port 8888
  - Access at http://localhost:8888

### Testing
- Run all tests: `PYTHONPATH=. pipenv run pytest`
- Run specific app tests: `PYTHONPATH=. pipenv run pytest tornado_app/tests/` or `PYTHONPATH=. pipenv run pytest flask_app/tests/`
- Run with verbose output: `PYTHONPATH=. pipenv run pytest -v`

## Architecture

This project contains multiple web applications:

### Project Structure
- **tornado_app/**: Tornado web application
  - **main.py**: Contains `MainHandler` serving "Hello, world" at root
  - **tests/test_main.py**: HTTP integration and unit tests
- **flask_app/**: Flask web application 
  - **flask_app.py**: Flask application with routes
  - **tests/test_flask_app.py**: Flask application tests

### Key Components
- `MainHandler`: Simple request handler for the root route "/"
- `make_app()`: Factory function that creates and configures the Tornado Application
- `main()`: Async entry point that starts the server and keeps it running

### Testing Strategy
The project uses a hybrid testing approach:
1. HTTP tests via `AsyncHTTPTestCase` for full request/response testing
2. Unit tests via pytest for component-level testing

### Dependencies
- **tornado**: Web framework for async Python applications
- **flask[async]**: Web framework with async support for mixed sync/async endpoints
- **aiohttp**: Async HTTP client library
- **requests**: Synchronous HTTP client library  
- **pytest**: Testing framework (dev dependency)
- **asyncio**: Built-in async support (explicitly listed in Pipfile)