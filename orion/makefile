.DEFAULT_GOAL:=build
NAME   := registry.gitlab.com/libdemsoftware/registr/orion
TAG    := $(shell git log -1 --pretty=%h)

build:
	docker build -t $(NAME):latest .
push:
	docker push $(NAME):latest
	docker push $(NAME):current
	docker push $(NAME):$(TAG)
current:
	docker tag $(NAME):latest $(NAME):current
	docker tag $(NAME):latest $(NAME):$(TAG)

# running #######################################################

delete:
	docker rm -f orion orion_postgres orion_setup
	sudo rm -rf ~/oriondb

up:
	docker-compose up -d

down:
	docker-compose down