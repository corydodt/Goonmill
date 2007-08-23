
DNOTIFY=dnotify -q1 -a

start:
	hg serve --daemon --port 28082 --pid-file hgserve.pid

stop:
	kill `cat hgserve.pid`

goonmill-start:
	echo Starting goonmill
	twistd --pid goonmill.pid goonmill --dev

goonmill-stop:
	echo Stopping goonmill
	-kill `cat goonmill.pid`

