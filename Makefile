.SILENT:

DEBUG        = TOMATE_DEBUG=true
DOCKER_IMAGE = $(eliostvs)/$(PACKAGE)
OBS_API_URL  = https://api.opensuse.org/trigger/runservice
PACKAGE      = tomate
PYTHONPATH   = PYTHONPATH=$(CURDIR)
VERSION      = `cat .bumpversion.cfg | grep current_version | awk '{print $$3}'`
WORK_DIR     = /code

clean:
	find . \( -iname "*.pyc" -o -iname "__pycache__" \) -print0 | xargs -0 rm -rf
	rm -rf .eggs *.egg-info/ .coverage build/ .cache

test: clean
	$(PYTHONPATH) pytest tests --cov=$(PACKAGE)

docker-clean:
	docker rmi --force $(DOCKER_IMAGE) 2> /dev/null || echo Image $(DOCKER_IMAGE) not found

docker-pull:
	docker pull $(DOCKER_IMAGE)

docker-test:
	docker run --rm -v $(CURDIR):$(WORK_DIR) --workdir $(WORK_DIR) $(DOCKER_IMAGE) test

docker-all: docker-clean docker-pull docker-test

docker-enter:
	docker run --rm -v $(CURDIR):$(WORK_DIR) --workdir $(WORK_DIR) -it --entrypoint="bash" $(DOCKER_IMAGE)

trigger-build:
	curl -X POST -H "Authorization: Token $(TOKEN)" $(OBS_API_URL)

release-%:
	git flow init -d
	@grep -q '\[Unreleased\]' CHANGELOG || (echo 'Create the [Unreleased] section in the changelog first!' && exit)
	bumpversion --verbose --commit $*
	git flow release start $(VERSION)
	GIT_MERGE_AUTOEDIT=no git flow release finish -m "Merge branch release/$(VERSION)" -T $(VERSION) $(VERSION) -p
