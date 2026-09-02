VENV_PY := .venv\Scripts\python.exe

.PHONY: install api app run

install:
	uv pip install --python $(VENV_PY) -r API\requirements.txt -r API\requirements-app.txt

api:
	cd API && ..\$(VENV_PY) -m uvicorn main:app --host 0.0.0.0 --port 8000

app:
	cd API && ..\$(VENV_PY) -m streamlit run app.py

run:
	$(MAKE) -j2 api app
