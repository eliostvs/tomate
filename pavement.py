#!/bin/env python
from optparse import Option

from paver.easy import cmdopts, needs, path, sh
from paver.tasks import task

ROOT_PATH = path(__file__).dirname().abspath()

TOMATE_PATH = ROOT_PATH / 'tomate'


@needs(['test'])
@task
def default():
    pass


@task
@needs(['clean'])
@cmdopts([
    Option('-v', '--verbosity', default=1, type=int),
])
def test(options):
    sh('nosetests --with-coverage --cover-erase --cover-package=%s --verbosity=%s'
       % (TOMATE_PATH, options.test.verbosity))


@task
def clean():
    sh('find . -name "*.pyc" -o -name __pycache__ -print0 | xargs -0 rm -rf')


@task
@needs(['docker_rmi', 'docker_build', 'docker_run'])
def docker_test():
    pass


@task
def docker_rmi():
    sh('docker rmi --force eliostvs/python-tomate', ignore_error=True)


@task
def docker_build():
    sh('docker build -t eliostvs/python-tomate .')


@task
def docker_run():
    sh('docker run --rm -v $PWD:/code eliostvs/python-tomate')
