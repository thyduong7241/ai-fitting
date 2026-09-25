.PHONY: install dev test lint clean

# Default target
.DEFAULT_GOAL := help

# Colors for terminal output
GREEN=\033[0;32m
YELLOW=\033[0;33m
NC=\033[0m # No Color

install: ## Install dependencies using venv and pyproject.toml
	@echo "${GREEN}Setting up venv and installing dependencies...${NC}"
	python3 -m venv .venv
	./.venv/bin/pip install -e ".[dev]"

dev: ## Run development server
	@echo "${GREEN}Starting development server...${NC}"
	./.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint: ## Run linting
	@echo "${GREEN}Running ruff linter...${NC}"
	./.venv/bin/ruff check app

test: ## Run tests
	@echo "${GREEN}Running tests...${NC}"
	./.venv/bin/pytest

clean: ## Clean up cache files
	@echo "${YELLOW}Cleaning up cache files...${NC}"
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete

help: ## Show this help
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'