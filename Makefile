PY := .venv/bin/python
ADDRESS ?=
DATE ?=
LAT ?=
LON ?=

.PHONY: setup report serve test clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install -q -e '.[dev]'

# make report ADDRESS="401 N College Ave, Bloomington, IN" DATE=2026-02-19 [LAT=.. LON=..]
report:
	$(PY) -m wxreport.cli report --address "$(ADDRESS)" --date "$(DATE)" $(if $(LAT),--lat $(LAT) --lon $(LON))

serve:
	.venv/bin/uvicorn wxreport.web:app --reload --port 8000

test:
	$(PY) -m pytest -q

clean:
	rm -rf reports/*.pdf
