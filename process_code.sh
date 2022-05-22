black ./src
black ./tests
flake8 ./src
mypy --ignore-missing-imports ./src
mypy --ignore-missing-imports ./tests
