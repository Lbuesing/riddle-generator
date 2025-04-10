build:
	docker compose -f docker-compose.yml build RiddleGenerator

run: 
	docker compose -f docker-compose.yml up RiddleGenerator