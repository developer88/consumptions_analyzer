run:
	docker compose run --rm --service-ports py_analyzer

build:
	docker compose build	

bash:
	docker compose run --rm --service-ports py_analyzer bash	

install:
	pip install -r requirements.txt