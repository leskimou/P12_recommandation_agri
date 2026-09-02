VENV_PY := .venv\Scripts\python.exe

.PHONY: install test api app run

install:
	uv pip install --python $(VENV_PY) -r API\requirements.txt -r API\requirements-app.txt -r API\requirements-dev.txt

test:
	$(VENV_PY) -m pytest API\tests -v

api:
	cd API && ..\$(VENV_PY) -m uvicorn main:app --host 0.0.0.0 --port 8000

app:
	cd API && ..\$(VENV_PY) -m streamlit run app.py

run:
	$(MAKE) -j2 api app
