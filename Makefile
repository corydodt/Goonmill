
DNOTIFY=dnotify -q1 -a

start:
	hg serve --daemon --port 28082 --pid-file hgserve.pid

stop:
	kill `cat hgserve.pid`

goonmill-start:
	echo Starting goonmill
	if [ `id -u` -eq 0 ]; then \
		twistd --umask 002 -u cdodt --pid goonmill.pid goonmill --dev; \
		else \
		twistd --umask 002 --pid goonmill.pid goonmill --dev; fi

goonmill-stop:
	echo Stopping goonmill
	-kill `cat goonmill.pid`

n3:
	cd goonmill; \
		cp -av statblock.n3 /var/www/goonmill.org/2009
