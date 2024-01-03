all: install

run: install 
	python src/main.py
	
test: install
	python src/test_algs.py

install: setup
	pip install -r requirements.txt


clean:
	yes | rm -r .venv 
setup:	
	python3 -m venv .venv && source .venv/bin/activate

