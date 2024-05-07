# python_template
A template repo for python projects

This has basic setup for

* pylint
* ruff
* black
* pytest
* codecov
* git-lfs
* basic github actions ci
* pulling updates from this template


# manifest_rocker

This is a manifest repo which contains configurations for [dep_rocker](https://github.com/blooop/deps_rocker) extension for automating dependency installation.  The aim is to allow a projects to define its development dependencies in a deps.yaml file which are added to the rocker container. The extension will recursivly search for deps.yaml files and run the install commands in several layers.  

Layer order:
- base: The bottom layer
- repository-software-sources: Set up apt repositories e.g add-apt-repo, wget gpg key
- version-control: add git, svn etc
- language-toolchain : add python, c++ rust etc
- tools: other tools
- expensive: expensive dependencies (cuda, torch etc)
- main: most installation should happen here
- post-main: any setup after everything is installed
- build
- lint
- test

run with:

```
rocker --deps-dependencies ubuntu:22.04
```


## limitations/TODO

The order of the layers relies on convention.  If different projects use a different convention then combining them may break in weird ways



## Continuous Integration Status

[![Ci](https://github.com/blooop/python_template/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/blooop/python_template/actions/workflows/ci.yml?query=branch%3Amain)
[![Codecov](https://codecov.io/gh/blooop/python_template/branch/main/graph/badge.svg?token=Y212GW1PG6)](https://codecov.io/gh/blooop/python_template)
[![GitHub issues](https://img.shields.io/github/issues/blooop/python_template.svg)](https://GitHub.com/blooop/python_template/issues/)
[![GitHub pull-requests merged](https://badgen.net/github/merged-prs/blooop/python_template)](https://github.com/blooop/python_template/pulls?q=is%3Amerged)
[![GitHub release](https://img.shields.io/github/release/blooop/python_template.svg)](https://GitHub.com/blooop/python_template/releases/)
[![License](https://img.shields.io/pypi/l/bencher)](https://opensource.org/license/mit/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)](https://www.python.org/downloads/release/python-310/)


To set up your project run the vscode task "pull updates from template repo" and then task "rename project template name"
