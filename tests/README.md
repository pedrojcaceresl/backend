# Testing Documentation

This directory contains comprehensive tests for the TechHub UPE backend API.

## Test Structure

```
tests/
├── conftest.py                    # Shared pytest fixtures and configuration
├── test_api_endpoints.py          # API endpoint testing
├── test_content_verification.py   # Content quality and quantity verification
├── test_auth_flow.py              # Authentication flow testing
├── test_role_management.py        # User role and permission testing
├── test_file_upload.py            # File upload system testing
└── README.md                      # This documentation
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio httpx
```

### 2. Run All Tests

```bash
# Run the test runner script
python run_tests.py

# Or run pytest directly
python -m pytest tests/ -v
```

### 3. Run Specific Test Files

```bash
# API endpoints only
python -m pytest tests/test_api_endpoints.py -v

# Content verification only
python -m pytest tests/test_content_verification.py -v

# Authentication flow only
python -m pytest tests/test_auth_flow.py -v

# Role management only
python -m pytest tests/test_role_management.py -v

# File upload only
python -m pytest tests/test_file_upload.py -v
```

## Test Categories

### API Endpoint Tests (`test_api_endpoints.py`)
- **Purpose**: Test all REST API endpoints
- **Coverage**: 
  - Course endpoints (`/courses/`)
  - Event endpoints (`/events/`)
  - Job endpoints (`/jobs/`)
  - Authentication endpoints (`/auth/`)
  - Saved items endpoints (`/saved-items/`)
- **Key Features**:
  - Response status validation
  - JSON schema validation
  - Authentication requirement testing
  - Error handling validation

### Content Verification Tests (`test_content_verification.py`)
- **Purpose**: Verify content quality and quantity requirements
- **Coverage**:
  - Minimum content requirements (10+ courses, 15+ events, 20+ jobs)
  - Content quality validation
  - Data completeness checks
- **Key Features**:
  - Automated content auditing
  - Quality metrics validation
  - Content freshness checks

### Authentication Flow Tests (`test_auth_flow.py`)
- **Purpose**: Test user authentication and authorization
- **Coverage**:
  - Login/logout flows
  - Token validation
  - Session management
  - Role-based access control
- **Key Features**:
  - JWT token testing
  - Auth dependency testing
  - Security validation

### Role Management Tests (`test_role_management.py`)
- **Purpose**: Test user roles and permissions
- **Coverage**:
  - Role assignment (ADMIN, STUDENT, COMPANY)
  - Permission validation
  - Role-based feature access
- **Key Features**:
  - Role enum testing
  - Permission matrix validation
  - Access control testing

### File Upload Tests (`test_file_upload.py`)
- **Purpose**: Test file upload functionality
- **Coverage**:
  - CV/Resume uploads
  - File validation
  - Security checks
- **Key Features**:
  - File type validation
  - Size limit testing
  - Security vulnerability checks

## Test Configuration

### Fixtures (defined in `conftest.py`)

- `test_client`: FastAPI TestClient for API testing
- `async_client`: AsyncClient for async endpoint testing
- `mock_user_service`: Mocked user service
- `mock_job_service`: Mocked job service
- `mock_course_service`: Mocked course service
- `sample_users`: Test user data
- `admin_user`, `student_user`, `company_user`: Role-specific test users

### Environment Setup

Tests automatically configure:
- Test database (SQLite in-memory)
- Mock authentication
- Temporary file uploads
- Isolated test environment

## Running Tests with Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m pytest tests/
coverage report
coverage html  # Generates HTML report in htmlcov/
```

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Run only unit tests
python -m pytest -m unit

# Run only integration tests  
python -m pytest -m integration

# Run only authentication tests
python -m pytest -k "auth"

# Run only API tests
python -m pytest -k "api"
```

## Debugging Tests

### Verbose Output
```bash
python -m pytest tests/ -v -s
```

### Stop on First Failure
```bash
python -m pytest tests/ -x
```

### Show Test Durations
```bash
python -m pytest tests/ --durations=10
```

### Run Specific Test
```bash
python -m pytest tests/test_api_endpoints.py::TestAPIEndpoints::test_get_courses -v
```

## Mock Data

Tests use predefined mock data for consistency:

- **Users**: 3 test users (admin, student, company)
- **Courses**: Sample course data with various categories
- **Events**: Sample event data with dates and types
- **Jobs**: Sample job postings with different requirements

## Common Issues

### Import Errors
If you see import errors, ensure:
1. You're in the project root directory
2. Python path includes the project root
3. All dependencies are installed

### Database Errors
Tests use in-memory SQLite by default. If you see database errors:
1. Check that SQLAlchemy is properly installed
2. Ensure test database initialization is working
3. Verify mock services are properly configured

### Authentication Errors
If authentication tests fail:
1. Check JWT secret configuration
2. Verify user fixtures are properly set up
3. Ensure auth dependencies are mocked correctly

## Contributing

When adding new tests:

1. **Follow naming conventions**: `test_*.py` files, `test_*` functions
2. **Use appropriate fixtures**: Leverage existing fixtures in `conftest.py`
3. **Add docstrings**: Document test purpose and expected behavior
4. **Group related tests**: Use classes to organize related test methods
5. **Mock external dependencies**: Don't rely on external services
6. **Test edge cases**: Include both positive and negative test cases

## Performance

Tests are designed to run quickly:
- In-memory database for speed
- Mocked external services
- Minimal test data
- Parallel execution support

Expected test run time: < 30 seconds for full suite

## Integration with CI/CD

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-asyncio httpx coverage
    python run_tests.py
```

## Support

For test-related issues:
1. Check this documentation first
2. Review test output for specific error messages
3. Ensure all dependencies are correctly installed
4. Verify your environment matches test requirements