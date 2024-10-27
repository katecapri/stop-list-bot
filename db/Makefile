
.PHONY: build
build:
	docker build -t stop_list_bot-db -f Dockerfile .

.PHONY: run
run:
	- docker network create "stop_list_bot"
	- docker-compose -f docker-compose.yaml up -d
