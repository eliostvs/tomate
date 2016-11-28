PACKAGE = tomate
AUTHOR = eliostvs
PACKAGE_ROOT = $(CURDIR)
DOCKER_IMAGE_NAME= $(AUTHOR)/$(PACKAGE)
PYTHONPATH = PYTHONPATH=$(CURDIR)
PROJECT = home:eliostvs:tomate
DEBUG = TOMATE_DEBUG=true
OBS_API_URL = https://api.opensuse.org:443/trigger/runservice?project=$(PROJECT)&package=$(PACKAGE)

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf
	rm -rf *.egg-info/ .coverage build/

lint:
	flake8

test: clean
	$(PYTHONPATH) py.test tests --cov=$(PACKAGE)

docker-clean:
	docker rmi --force $(DOCKER_IMAGE_NAME) 2> /dev/null || echo Image $(DOCKER_IMAGE_NAME) not found

docker-build:
	docker build -t $(DOCKER_IMAGE_NAME) .

docker-test:
	docker run --rm -v $(PACKAGE_ROOT):/code $(DOCKER_IMAGE_NAME) test

docker-lint:
	docker run --rm -v $(PACKAGE_ROOT):/code $(DOCKER_IMAGE_NAME) lint

docker-all: docker-clean docker-build docker-test

docker-enter:
	docker run --rm -v $(PACKAGE_ROOT):/code -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)

trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)
