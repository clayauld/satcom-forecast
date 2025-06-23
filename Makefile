.PHONY: help install test lint format clean docs

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .

test: ## Run all tests
	cd tests && python3 run_tests.py

test-pytest: ## Run tests with pytest
	pytest tests/ -v

lint: ## Run linting checks
	flake8 custom_components/satcom_forecast/ tests/
	mypy custom_components/satcom_forecast/

format: ## Format code with black
	black custom_components/satcom_forecast/ tests/

format-check: ## Check if code is formatted correctly
	black --check custom_components/satcom_forecast/ tests/

clean: ## Clean up build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/

docs: ## Build documentation
	mkdocs build

docs-serve: ## Serve documentation locally
	mkdocs serve

pre-commit: ## Install pre-commit hooks
	pre-commit install

pre-commit-run: ## Run pre-commit on all files
	pre-commit run --all-files

check: format-check lint test ## Run all checks (format, lint, test) 