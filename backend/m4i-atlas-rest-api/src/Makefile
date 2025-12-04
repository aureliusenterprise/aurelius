include ./python_rest_env

build:
	@docker build -t $(repository):$(version) .
run:
	docker run -p 5000:5000 --name $(repository)  $(repository):$(version)
kill:
	@echo 'Killing container...'
	@docker ps | grep $(repository) | awk '{print $$1}' | xargs docker rm -f
info:
	@echo $(repository):$(version)
