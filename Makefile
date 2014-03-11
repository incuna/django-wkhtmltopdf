SHELL := /bin/bash

release:
	python setup.py register sdist upload

test:
	./run_tests.sh
