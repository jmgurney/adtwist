test:
	. ./t/bin/activate && \
		echo adtwist.py | entr sh -c 'python -m coverage run -m unittest adtwist && coverage report -m --omit=t/\*'

setup:
	virtualenv t && \
		. ./t/bin/activate && \
		pip install -r requirements.txt
