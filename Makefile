# NYC Ridesharing Data Analysis Dashboard Makefile

.PHONY: help install run-dashboard run-analysis clean setup test

# Default target
help:
	@echo "NYC Ridesharing Data Analysis Dashboard"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo "  install        Install dependencies"
	@echo "  setup          Setup development environment"
	@echo "  run-dashboard  Run the Streamlit dashboard"
	@echo "  run-analysis   Run the data analysis script"
	@echo "  test           Run tests (if available)"
	@echo "  clean          Clean generated files"
	@echo "  help           Show this help message"

# Install dependencies
install:
	pip install -r requirements.txt

# Setup development environment
setup: install
	@echo "Setting up development environment..."
	@mkdir -p data assets docs
	@echo "Development environment ready!"

# Run the Streamlit dashboard
run-dashboard:
	@echo "Starting NYC Ridesharing Dashboard..."
	cd src && streamlit run streamlit_hotspots.py

# Run the data analysis script
run-analysis:
	@echo "Running data analysis..."
	cd src && python uber_analysis.py

# Run tests (placeholder for future tests)
test:
	@echo "Running tests..."
	@echo "No tests configured yet."

# Clean generated files
clean:
	@echo "Cleaning generated files..."
	rm -rf __pycache__/
	rm -rf src/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "Clean complete!"

# Development setup
dev-setup: setup
	@echo "Development setup complete!"
	@echo "Run 'make run-dashboard' to start the dashboard"
	@echo "Run 'make run-analysis' to run data analysis"
