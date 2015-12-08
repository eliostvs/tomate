PROJECT = tomate
AUTHOR = eliostvs
PROJECT_ROOT = $(CURDIR)
PACKAGE_ROOT = $(PROJECT_ROOT)/$(PROJECT)
DOCKER_IMAGE_NAME= $(AUTHOR)/$(PROJECT)
VERBOSITY=1

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf

test:  clean
	nosetests --with-coverage --cover-erase --cover-package=$(PACKAGE_ROOT) --verbosity=$(VERBOSITY)

docker-clean:
	docker rmi --force $(DOCKER_IMAGE_NAME) 2> /dev/null || echo Image $(DOCKER_IMAGE_NAME) not found

docker-build:
	docker build -t $(DOCKER_IMAGE_NAME) .

docker-test:
	docker run --rm -v $(PROJECT_ROOT):/code $(DOCKER_IMAGE_NAME)

docker-enter:
	docker run --rm -v $(PROJECT_ROOT):/code -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)

docker-all: docker-clean docker-build docker-test
