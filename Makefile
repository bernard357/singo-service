help:
	@echo "install - install code and dependencies for developers and pipelines"
	@echo "shell - enter your specific development environment"
	@echo "lint - analyze python code"
	@echo "test - perform python tests"
	@echo "coverage - track untested code in web browser"
	@echo "bandit - look for secret strings in the code"

# python code to be analyzed
CODE_PATH := singo

install:
	@echo "Installing software..."
	python3 -m venv .env
	. .env/bin/activate && pip install -r requirements.txt

shell:
	@echo "Hit <Ctl-D> to exit this shell"
	. .env/bin/activate && bash

lint:
	python -m flake8 --max-complexity 6 --ignore E402,E501,F841,W503 ${CODE_PATH}
	python -m flake8 --max-complexity 6 --ignore E402,E501,E722,F401,F841,W503 tests

test-wip:
	python -m pytest -m wip -ra tests/

test:
	python -m pytest -ra tests/

test-all:
	python -m pytest --durations=5 --run-slow -ra tests/

define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT
BROWSER := python -c "$$BROWSER_PYSCRIPT"

coverage:
	python -m coverage run --omit "*/.env/*,*/tests/*" -m pytest --run-slow
	python -m coverage report -m
	python -m coverage html
	$(BROWSER) htmlcov/index.html

coverage-api:
	python -m coverage run --omit "*/.env/*,*/tests/*" -m pytest -m api
	python -m coverage report -m
	python -m coverage html
	$(BROWSER) htmlcov/index.html

bandit:
	python -m bandit -r ${CODE_PATH}

serve:
	STATE_FILE=fixtures/test_state.yaml python singo

test-curl:
	# create a user record
	code=$(shell curl --header "Content-Type: application/json" \
	     --request POST \
	     --data '{"id":"xyz","password":"xyz"}' \
	     --write-out %{http_code} --silent --output /dev/null  \
	     http://localhost:5000/register) && test "$${code}" = "201"
	# test that duplicate record is forbidden
	code=$(shell curl --header "Content-Type: application/json" \
	     --request POST \
	     --data '{"id":"xyz","password":"xyz"}' \
	     --write-out %{http_code} --silent --output /dev/null  \
	     http://localhost:5000/register) && test "$${code}" = "400"
	# login
	code=$(shell curl --header "Content-Type: application/json" \
	     --request POST \
	     --data '{"id":"Sylvia","password":"P455w@rd"}' \
	     --write-out %{http_code} --silent --output /dev/null  \
			 -c .bearer  \
	     http://localhost:5000/login) && test "$${code}" = "200"
	# list users
	code=$(shell curl --header "Content-Type: application/json" \
	     --request GET \
	     --write-out %{http_code} --silent --output /dev/null  \
			 -b .bearer  \
	     http://localhost:5000/users) && test "$${code}" = "200"
	echo "done"

image:
	docker build -t singo-server:v1 .

container:
	docker run -d -p 5000:5000 --rm --name singo-server singo-server:v1

tracked-in-git:
	git log --pretty=format: --name-only | sort - -u

remove-from-git:
	@[ ! -z "${PATH_TO_REMOVE}" ] || (echo "You should set PATH_TO_REMOVE. For example: PATH_TO_REMOVE=yarn.lock make remove-from-git"; exit 1)
	@read -p "Are you sure that you want to destroy file '${PATH_TO_REMOVE}'? [y/N]: " sure && [ $${sure:-N} == y ]
	git filter-branch --force --index-filter \
  	"git rm --cached --ignore-unmatch ${PATH_TO_REMOVE}" \
  	--prune-empty --tag-name-filter cat -- --all
