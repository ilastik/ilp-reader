.PHONY: fmt
fmt:
	python -m isort --recursive .
	python -m black .
