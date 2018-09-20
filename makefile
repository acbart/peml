.PHONY: docs test

test:
	python -m unittest discover -s test/

verbose_test:
	python -m unittest discover -s test/ -v
    
coverage:
	coverage run --source=. -m unittest discover -s test/
	coverage html -i
	coverage report
	echo "HTML version available at ./htmlcov/index.html"

style:
	flake8 peml/