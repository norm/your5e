.PHONY: format lint tests-python tests-bats tests test

format:
	@black -q your5e tests

lint:
	@flake8 your5e tests

tests-python:
	@pytest tests

tests-bats:
	@bats tests

tests: tests-python tests-bats

test: format lint tests-python tests-bats
