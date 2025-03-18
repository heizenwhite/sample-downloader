.PHONY: test lint format all

# Run all tests
test:
	pytest tests/ --disable-warnings --cov=app --cov-report=term

# Linting with flake8
lint:
	flake8 app tests --max-line-length=100

# Code formatting with black
format:
	black app tests

# Run everything (format, lint, test)
all: format lint test
