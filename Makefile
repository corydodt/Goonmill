
start:
	hg serve --daemon --port 28082 --pid-file hgserve.pid

stop:
	kill `cat hgserve.pid`

goonmill-start:
	twistd --pid goonmill.pid goonmill --dev

goonmill-stop:
	kill `cat goonmill.pid`

