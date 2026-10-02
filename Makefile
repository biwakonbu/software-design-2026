PYTHON ?= python3.12

.PHONY: install test export build qa privacy
install:
	npm ci
	npx playwright install chromium

test:
	$(PYTHON) -m unittest discover -s tests -v

export:
	node scripts/export-pdfs.mjs
	node scripts/export-workbooks.mjs

build:
	node scripts/build-slides.mjs

qa:
	$(PYTHON) scripts/render-pdfs.py

privacy:
	$(PYTHON) scripts/check-public.py
