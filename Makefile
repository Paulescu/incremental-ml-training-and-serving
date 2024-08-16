install:
	@echo "Install Python Poetry to build the project"
	curl -sSL https://install.python-poetry.org | python3 -
	poetry env use $(shell which python3.10) && \
	poetry install

start-redpanda:
	docker compose -f redpanda.yml up -d

stop-redpanda:
	docker compose -f redpanda.yml down

producers:
	poetry run python src/producers.py

training:
	poetry run python src/training.py

predict:
	poetry run python src/predict.py
