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
