# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Setup and Environment
```bash
# Setup virtual environment
scripts\setup_venv.bat    # Windows
./scripts/setup_venv.sh   # Linux/macOS

# Install dependencies after activation
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Running the Application
```bash
# Run locally with auto-reload
python app/main.py

# Run with Docker
docker-compose up -d

# Check health
curl http://localhost:8000/status
```

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/scrapers/soundcloud/test_soundcloud_profile_scraper.py

# Run integration tests only
pytest tests/integration/

# Windows/Linux specific test scripts
scripts\run_tests.bat      # Windows
./scripts/run_tests.sh     # Linux/macOS
```

## Key Architecture Patterns

### Scraper Pattern
All scrapers inherit from `BaseScraper` (`app/scrapers/base_scraper.py`):
```python
class CustomScraper(BaseScraper):
    async def scrape(self, *args, **kwargs) -> Any:
        # Implementation here
        pass
```

### Error Handling Hierarchy
- `TemporaryScraperException` - Retryable errors (5xx, timeouts)
- `PermanentScraperException` - Non-retryable errors (4xx except 404)
- `ResourceNotFoundException` - 404 errors
- `RateLimitException` - Rate limiting with retry-after support

### Retry Mechanism
```python
from app.services import with_retry

@with_retry(max_attempts=3, retry_exceptions=[TemporaryScraperException])
async def fetch_data(self, url: str):
    # Method implementation
```

### Testing Architecture
- **Unit Tests**: Mock at service/HTTP level
- **Integration Tests**: Mock at scraper level (public interface)
- Use `@patch` decorators appropriately based on test level

#### Unit Tests Standards
- **ALWAYS create external mocks** in `tests/mocks/` directory (e.g., `soundcloud_mocks.py`, `beatport_mocks.py`)
- **Mock at BaseScraper.fetch level** for scraper tests: `@patch('app.scrapers.base_scraper.BaseScraper.fetch')`
- **Use mock factories** for HTTP responses: `mock_response_factory` from `tests/mocks/http_mocks.py`
- **Create __init__.py files** in all test directories and update imports properly
- **Import mocks from external files**, not inline definitions
- **Follow consistent naming**: `mock_[platform]_[data_type]` (e.g., `mock_soundcloud_user_data`)
- **Always use proper imports** from `tests.mocks.[platform]_mocks` and update `__init__.py` exports

#### Integration Tests Standards  
- **Mock at scraper method level**: `@patch('app.scrapers.[platform].[scraper_class].scrape')`
- **Create integration-specific mocks** in `tests/integration/mocks/[platform]_mocks_integration.py`
- **Test full router workflow** including authentication, validation, error handling
- **Use TestClient** from FastAPI for API endpoint testing

#### Test Structure Example
```python
# Unit test pattern
from tests.mocks.bandcamp_mocks import BANDCAMP_SEARCH_RESPONSE, mock_bandcamp_response_factory

class TestBandcampSearchScraper:
    @pytest.fixture
    def scraper(self):
        return BandcampSearchScraper()
    
    @patch('app.scrapers.base_scraper.BaseScraper.fetch', new_callable=AsyncMock)
    async def test_scrape_success(self, mock_fetch, scraper, mock_bandcamp_response_factory):
        mock_fetch.return_value = mock_bandcamp_response_factory(html=BANDCAMP_SEARCH_RESPONSE)
        # Test implementation
```

## Python Development Standards

### Code Formatting and Linting
```bash
# Format code with black (run before commits)
black .

# Sort imports with isort
isort .

# Lint with ruff (check for errors and style issues)
ruff check .
```

### Code Quality Rules
- **NO COMMENTS unless explicitly requested** - code should be self-documenting
- **Use type hints** for all function parameters and return types
- **Follow PEP 8** naming conventions (snake_case for variables/functions, PascalCase for classes)
- **Import organization**: stdlib first, third-party second, local imports last
- **Avoid wildcard imports** (`from module import *`) - use explicit imports

### Error Handling Standards
- **Use specific exception types** from `app.core.errors` hierarchy
- **Log errors appropriately** using the configured logger
- **Don't catch broad exceptions** unless absolutely necessary
- **Provide meaningful error messages** with context

### Async/Await Best Practices
- **Use async/await consistently** - don't mix with sync code unnecessarily
- **Proper session management** for HTTP clients (use context managers)
- **Handle timeouts and cancellation** gracefully
- **Use AsyncMock** for mocking async functions in tests

### File Organization Rules
- **Create __init__.py** in every package directory
- **Update __init__.py exports** when adding new modules
- **Follow directory structure**: `app/[layer]/[platform]/` pattern
- **Keep imports clean** - use absolute imports from app root

### Security Standards
- **NEVER commit secrets** - use environment variables in `.env` file (must be in `.gitignore`)
- **Validate all external input** - use Pydantic models for validation
- **Keep dependencies updated** - regularly check for security vulnerabilities

## Important Configuration

### Environment Variables Required
```bash
API_KEY=your-api-key-here
SOUNDCLOUD_CLIENT_ID=your-client-id
SOUNDCLOUD_CLIENT_SECRET=your-client-secret
```

### SoundCloud Integration
- Uses OAuth 2.1 Client Credentials Flow
- Services: `SoundcloudAuthService`, `SoundcloudApiService`
- Base URL: `https://api.soundcloud.com`
- Auth header: `OAuth {access_token}`

### Application Structure
- **API Layer**: FastAPI routers (`app/routers/`)
- **Business Layer**: Services (`app/services/`)
- **Data Layer**: Scrapers (`app/scrapers/`)
- **Model Layer**: Pydantic models (`app/models/`)

## Development Workflow

### Adding New Scrapers
1. Create scraper class inheriting from `BaseScraper`
2. Add corresponding Pydantic models in `app/models/`
3. Create router in `app/routers/`
4. Add comprehensive tests (unit + integration)
5. Update `app/main.py` to include new router

### Git Commit Messages
Follow [Conventional Commits](https://www.conventionalcommits.org/) format:
- `feat: add Beatport search endpoint`
- `fix: handle rate limiting in Soundcloud scraper`
- `docs: update API documentation for releases`
- `test: add integration tests for MCP tools`
- `refactor: simplify error handling in base scraper`

Make atomic commits - each commit should represent a single logical change.

### Testing Strategy
- Unit tests mock at appropriate levels (services for scrapers, HTTP for services)
- Integration tests mock at scraper level
- Use `pytest-mock` for mocking and `pytest-httpx` for HTTP mocking

## Development Best Practices

### Initialization and Imports
- **Always use proper initializations**
- **Ensure correct and complete imports for all modules and classes**
- Follow Python best practices for module and class imports
- Verify that all necessary dependencies are imported before use

## Documentation References

For detailed information, refer to these files:

- **Architecture**: See `docs/architecture.md` for complete system architecture, diagrams, and component details
- **Development Context**: See `docs/development.md` for project history, current state, implemented features, and technical notes
- **Project Overview**: See `README.md` for setup instructions and API documentation

## Pre-Commit Checklist

```bash
# 1. Format code
black .
isort .

# 2. Lint code
ruff check .

# 3. Run tests
pytest

# 4. Check coverage (optional)
pytest --cov=app tests/
```