.PHONY: black
black:
	black src --line-length=120

.PHONY: isort
isort:
	isort src --profile black --line-length=120

.PHONY: flake8
flake8:
    flake8 src --max-line-length=120 \
           src --count --show-source --statistics

.PHONY: mypy
mypy:
	mypy --ignore-missing-imports src

.PHONY: format
format:
	make black
	make isort
	make flake8
	make mypy

.PHONY: run
run:
	streamlit run src/app/main.py