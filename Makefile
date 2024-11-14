.PHONY: build preview clean kill publish ensure-killed

# Ensure process is really killed with retries
ensure-killed:
	@for i in 1 2 3; do \
		(lsof -ti:8000 | xargs kill -9 2>/dev/null || true) && \
		(pkill -9 -f "python.*blog\.py.*preview" 2>/dev/null || true) && \
		sleep 2 && \
		if ! lsof -i:8000 >/dev/null 2>&1; then \
			exit 0; \
		fi; \
	done
	@if lsof -i:8000 >/dev/null 2>&1; then \
		echo "Failed to free port 8000 after multiple attempts" && exit 1; \
	fi

# Kill any process running on port 8000
kill: ensure-killed

# Build the static site
build:
	python blog.py

# Start preview server (killing existing one if needed)
preview: kill
	python blog.py preview

# Clean generated files
clean:
	rm -rf output/

# Publish to GitHub Pages
publish:
	python blog.py publish