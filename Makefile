# Human++ Color Scheme
# Makefile for common operations
#
# The core invariant: palette.toml is the single source of truth.
# Everything in dist/ and site/ is generated — do not edit by hand.

.PHONY: all build site dist preview colortest apply apply-dry analyze propose derive clean check help

# Default target
all: build

# Build all theme files from palette.toml
build:
	@python3 tools/build.py

# Build only the site (fast iteration for web)
site:
	@python3 -c "from tools.build import parse_palette, generate_palette_json, generate_site; c,m = parse_palette(); generate_palette_json(c,m); generate_site(c,m)"

# Build only dist/ outputs (no site)
dist:
	@python3 -c "from tools.build import *; c,m = parse_palette(); generate_ghostty(c,m); generate_sketchybar(c,m); generate_borders(c,m); generate_skhd(c,m); generate_colortest(c,m); generate_base24_yaml(c,m); update_vscode_theme(c,m)"

# Preview the palette in terminal
preview:
	@./scripts/preview.sh

# Display color test (terminal ANSI mapping)
colortest:
	@./dist/scripts/colortest.sh

# Apply theme to installed applications
apply:
	@./scripts/apply.sh

# Apply theme (dry run - show what would happen)
apply-dry:
	@./scripts/apply.sh --dry-run

# Analyze palette in OKLCH color space
analyze:
	@python3 tools/analyze.py

# Generate palette improvement proposals
propose:
	@python3 tools/propose.py

# Derive quiet accents from loud accents
derive:
	@python3 tools/derive_base24.py palette.toml

# Clean generated files (keeps source files)
clean:
	@echo "Cleaning generated files..."
	@rm -rf dist/ site/data/
	@rm -f .palette-cache.json
	@echo "Done."

# CI check: build and verify no uncommitted changes
check: build
	@echo "Checking for uncommitted changes..."
	@if git diff --quiet && git diff --cached --quiet; then \
		echo "✓ All generated files are up to date"; \
	else \
		echo "✗ Generated files are out of sync with palette.toml"; \
		echo "  Run 'make build' and commit the changes"; \
		git diff --stat; \
		exit 1; \
	fi

# Help
help:
	@echo "Human++ Color Scheme"
	@echo ""
	@echo "Core invariant: palette.toml is the single source of truth."
	@echo "Everything in dist/ and site/ is generated."
	@echo ""
	@echo "Targets:"
	@echo "  make build     - Build all theme files from palette.toml"
	@echo "  make site      - Build only site/ (fast iteration)"
	@echo "  make dist      - Build only dist/ outputs"
	@echo "  make preview   - Preview palette in terminal (true color)"
	@echo "  make colortest - Display terminal ANSI color mapping"
	@echo "  make apply     - Apply theme to installed applications"
	@echo "  make apply-dry - Show what apply would do (no changes)"
	@echo "  make analyze   - Analyze palette in OKLCH color space"
	@echo "  make check     - Build and verify no uncommitted changes (CI)"
	@echo "  make clean     - Clean generated files"
	@echo ""
	@echo "Do not edit dist/ or site/ by hand — change palette.toml and rebuild."
