
DNOTIFY=dnotify -q1 -a

start:
	hg serve --daemon --port 28082 --pid-file hgserve.pid

stop:
	kill `cat hgserve.pid`

goonmill-start:
	echo Starting goonmill
	twistd --pid goonmill.pid goonmill --dev
	nohup $(DNOTIFY) goonmill/n3data -e ./copyn3.sh  \
		>dnotify.log 2>&1 & \
		echo $$! > dnotify.pid

goonmill-stop:
	echo Stopping goonmill
	-kill `cat goonmill.pid`
	-kill `cat dnotify.pid`

