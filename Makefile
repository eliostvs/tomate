PACKAGE = tomate
AUTHOR = eliostvs
PACKAGE_ROOT = $(CURDIR)
DOCKER_IMAGE_NAME= $(AUTHOR)/$(PACKAGE)
PYTHONPATH = PYTHONPATH=$(CURDIR)
PROJECT = home:eliostvs:tomate
DEBUG = TOMATE_DEBUG=true
OBS_API_URL = https://api.opensuse.org:443/trigger/runservice?project=$(PROJECT)&package=$(PACKAGE)
WORK_DIR = /code

ifeq ($(shell which py.test-3 1> /dev/null && echo yes),yes)
	PYTEST = py.test-3
else
	PYTEST = py.test
endif

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf
	rm -rf .eggs *.egg-info/ .coverage build/ .cache

test: clean
	$(PYTHONPATH) $(PYTEST) tests --cov=$(PACKAGE) --cov-report=term-missing --flake8

docker-clean:
	docker rmi --force $(DOCKER_IMAGE_NAME) 2> /dev/null || echo Image $(DOCKER_IMAGE_NAME) not found

docker-pull:
	docker pull $(DOCKER_IMAGE_NAME)

docker-test:
	docker run --rm -v $(PACKAGE_ROOT):$(WORK_DIR) --workdir $(WORK_DIR) $(DOCKER_IMAGE_NAME) test

docker-all: docker-clean docker-pull docker-test

docker-enter:
	docker run --rm -v $(PACKAGE_ROOT):$(WORK_DIR) --workdir $(WORK_DIR) -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)

trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)
