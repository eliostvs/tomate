PACKAGE = tomate
AUTHOR = eliostvs
PACKAGE_ROOT = $(CURDIR)
DOCKER_IMAGE_NAME= $(AUTHOR)/$(PACKAGE)
PROJECT = home:eliostvs:tomate
PYTHONPATH = PYTHONPATH=$(CURDIR)
OBS_API_URL = https://api.opensuse.org:443/trigger/runservice?project=$(PROJECT)&package=$(PACKAGE)

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf
	rm -rf *.egg-info/ .coverage build/

test: clean
	$(PYTHONPATH) py.test --cov-report term-missing --cov=$(PACKAGE) --flake8 -v

docker-clean:
	docker rmi --force $(DOCKER_IMAGE_NAME) 2> /dev/null || echo Image $(DOCKER_IMAGE_NAME) not found

docker-build:
	docker build -t $(DOCKER_IMAGE_NAME) .

docker-test:
	docker run --rm -v $(PACKAGE_ROOT):/code $(DOCKER_IMAGE_NAME)

docker-all: docker-clean docker-build docker-test

docker-enter:
	docker run --rm -v $(PACKAGE_ROOT):/code -it --entrypoint="bash" $(DOCKER_IMAGE_NAME)
