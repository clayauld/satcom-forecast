.PHONY: test test-all test-structure test-reconfig test-core test-multi test-weather test-summary lint clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  test        - Run all tests"
	@echo "  test-all    - Run all tests with verbose output"
	@echo "  test-structure - Run integration structure test only"
	@echo "  test-reconfig - Run reconfiguration test only"
	@echo "  test-core   - Run core functionality test only"
	@echo "  test-multi  - Run multi-region test only"
	@echo "  test-weather - Run weather detection test only"
	@echo "  test-summary - Run summary length test only"
	@echo "  lint        - Run code linting"
	@echo "  clean       - Clean up cache files"
	@echo "  help        - Show this help message"

# Run all tests
test:
	@echo "🧪 Running SatCom Forecast Test Suite..."
	cd tests && python3 run_tests.py

# Run all tests with verbose output
test-all:
	@echo "🧪 Running SatCom Forecast Test Suite (Verbose)..."
	cd tests && python3 run_tests.py

# Run individual tests
test-structure:
	@echo "🔍 Testing integration structure..."
	cd tests && python3 test_integration_structure.py

test-reconfig:
	@echo "⚙️  Testing reconfiguration functionality..."
	cd tests && python3 test_reconfiguration.py

test-core:
	@echo "🧪 Testing core functionality..."
	cd tests && python3 test_core_functionality.py

test-multi:
	@echo "🌍 Testing multi-region functionality..."
	cd tests && python3 test_multi_region.py

test-weather:
	@echo "🌦️  Testing weather detection..."
	cd tests && python3 test_weather_detection.py

test-summary:
	@echo "📝 Testing summary length..."
	cd tests && python3 test_summary_length.py

# Run linting
lint:
	@echo "🔍 Running code linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 custom_components/satcom_forecast/ --max-line-length=88 --extend-ignore=E203,W503; \
	else \
		echo "flake8 not found. Install with: pip install flake8"; \
	fi
	@if command -v black >/dev/null 2>&1; then \
		black --check --diff custom_components/satcom_forecast/; \
	else \
		echo "black not found. Install with: pip install black"; \
	fi

# Clean up cache files
clean:
	@echo "🧹 Cleaning up cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
