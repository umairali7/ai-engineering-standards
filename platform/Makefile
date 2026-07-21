# AIES Qualification Platform — developer entry points.
# The demo is executable documentation: `make demo` runs the entire workflow
# offline; the same golden path is CI-gated as tests/test_demo.py.
.PHONY: install test validate audit release-hygiene demo integration-demo all

install:            ## editable install + test deps
	pip install -e . && pip install pytest

test:              ## conformance test suite (keyed to AESQS requirement IDs)
	pytest tests/ -q

validate:          ## suite catalog + shipped assessments (the CI gate)
	aies suites validate

audit:             ## repository self-conformance (dogfood), gated at RT2
	aies audit .. --gate --rt 2

release-hygiene:   ## reject local/generated artifacts from the tracked release tree
	python scripts/check_release_artifacts.py ..

demo:              ## core workflow, fully offline (mock runtime + mock judge)
	bash scripts/demo.sh

demo-full:         ## comprehensive tour of the whole platform, fully offline
	bash scripts/demo-full.sh

demo-empirical:    ## Phase-2 empirical harness on a SYNTHETIC panel (see discrimination output)
	python scripts/demo_empirical.py

integration-demo:  ## full workflow against a REAL deployment (opt-in)
	@# Set DEPLOYMENT and JUDGE to registered deployments, then:
	@#   make integration-demo DEPLOYMENT=local-qwen JUDGE=gpt-oss
	bash scripts/integration-demo.sh

all: validate test audit release-hygiene
