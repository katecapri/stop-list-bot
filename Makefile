
.PHONY: run
run:
	cd db && make build && make run && cd .. && \
	docker build -t stop_list_bot-project -f Dockerfile . && docker-compose up
