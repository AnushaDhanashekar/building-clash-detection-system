# Building Clash Detection Makefile
VENV = venv
PYTHON = python3
PIP = $(VENV)/bin/pip

.PHONY: venv install run

venv:
	$(PYTHON) -m venv $(VENV)
	@echo "Virtual env created. Activate with:"
	@echo "source $(VENV)/bin/activate"

install: venv
	$(PIP) install -r requirements.txt

run:
	$(PYTHON) -m uvicorn main:app --reload

