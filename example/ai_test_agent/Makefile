# Makefile for AI Test Agent

.PHONY: help install demo test clean run-uncommitted run-branch run-commit

help:
	@echo "AI Test Agent - Available Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install           Install dependencies in virtual environment"
	@echo "  make demo              Run demonstration (no API key needed)"
	@echo ""
	@echo "Usage:"
	@echo "  make run-uncommitted   Analyze uncommitted changes"
	@echo "  make run-branch        Compare branches (set BASE and COMPARE vars)"
	@echo "  make run-commit        Analyze specific commit (set COMMIT var)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean             Remove generated files and caches"
	@echo "  make test              Run tests (future)"
	@echo ""
	@echo "Examples:"
	@echo "  make run-uncommitted"
	@echo "  make run-branch BASE=master COMPARE=feature/new-api"
	@echo "  make run-commit COMMIT=abc123def"

install:
	@echo "Setting up virtual environment..."
	python3 -m venv venv
	@echo "Installing dependencies..."
	./venv/bin/pip install -r requirements.txt
	@echo ""
	@echo "Setup complete! Don't forget to:"
	@echo "  1. Activate venv: source venv/bin/activate"
	@echo "  2. Set API key: export OPENAI_API_KEY=sk-..."

demo:
	@echo "Running demonstration..."
	python3 demo.py

run-uncommitted:
	@echo "Analyzing uncommitted changes..."
	python3 src/cli.py analyze-uncommitted

run-branch:
	@if [ -z "$(BASE)" ] || [ -z "$(COMPARE)" ]; then \
		echo "Error: Please specify BASE and COMPARE branches"; \
		echo "Usage: make run-branch BASE=master COMPARE=feature/new-api"; \
		exit 1; \
	fi
	@echo "Comparing $(BASE) with $(COMPARE)..."
	python3 src/cli.py compare-branches --base-branch $(BASE) --compare-branch $(COMPARE)

run-commit:
	@if [ -z "$(COMMIT)" ]; then \
		echo "Error: Please specify COMMIT"; \
		echo "Usage: make run-commit COMMIT=abc123def"; \
		exit 1; \
	fi
	@echo "Analyzing commit $(COMMIT)..."
	python3 src/cli.py analyze-commit --commit-sha $(COMMIT)

test:
	@echo "Running tests..."
	@echo "Note: Test suite not yet implemented"
	# python3 -m pytest tests/

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__ src/__pycache__
	rm -rf venv
	rm -rf *.pyc src/*.pyc
	rm -rf .pytest_cache
	rm -rf reports/*.json reports/*.md
	rm -rf artifacts/*
	@echo "Clean complete!"

.DEFAULT_GOAL := help
