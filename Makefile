.PHONY: env clean pypi

VENV    ?= .venv
PIP     ?= $(VENV)/bin/pip3
PYTHON  ?= $(VENV)/bin/python3
PYVER   ?= python3

all: env

env:
ifeq ($(wildcard $(PIP)),)
	virtualenv $(VENV) --python=$(PYVER)
endif
	$(PIP) uninstall c2client -q -y ||:
	$(PIP) install -U -r ./requirements.txt
	$(PYTHON) setup.py develop --no-deps

pypi: clean
	@python setup.py sdist bdist_wheel upload

clean:
	@rm -rf .venv/ build/ dist/ *.egg* .eggs/ *.tar.gz
