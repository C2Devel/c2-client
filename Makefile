.PHONY: env sources srpm rpm clean pypi copr

DIST    ?= epel-6-x86_64
VENV    ?= .venv
PIP     ?= $(VENV)/bin/pip
PYTHON  ?= $(VENV)/bin/python
PYVER   ?= python2.7

PACKAGE := c2-client
VERSION := $(shell rpm -q --qf "%{version}\n" --specfile $(PACKAGE).spec | head -1)
RELEASE := $(shell rpm -q --qf "%{release}\n" --specfile $(PACKAGE).spec | head -1)

all: env

env:
ifeq ($(wildcard $(PIP)),)
	virtualenv $(VENV) --python=$(PYVER)
endif
	$(PIP) uninstall c2client -q -y ||:
	$(PIP) install -U -r ./requirements.txt
	$(PYTHON) setup.py develop --no-deps

sources: clean
	@git archive --format=tar --prefix="$(PACKAGE)-$(VERSION)/" \
		$(shell git rev-parse --verify HEAD) | gzip > "$(PACKAGE)-$(VERSION).tar.gz"

srpm: sources
	@mkdir -p srpms/
	rpmbuild -bs --define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(CURDIR)/srpms" $(PACKAGE).spec

rpm:
	@mkdir -p rpms/$(DIST)
	/usr/bin/mock -r $(DIST) \
		--rebuild srpms/$(PACKAGE)-$(VERSION)-$(RELEASE).src.rpm \
		--resultdir rpms/$(DIST) --no-cleanup-after

copr: srpm
	@copr-cli build --nowait c2devel/c2-sdk \
		srpms/$(PACKAGE)-$(VERSION)-$(RELEASE).src.rpm

pypi: clean
	@python setup.py sdist bdist_wheel upload

clean:
	@rm -rf .venv/ build/ dist/ *.egg* .eggs/ rpms/ srpms/ *.tar.gz *.rpm
